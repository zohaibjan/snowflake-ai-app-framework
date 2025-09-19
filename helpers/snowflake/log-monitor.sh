#!/bin/bash
# Log monitoring and analysis script for SPCS deployments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DEFAULT_LINES=100
LOG_RETENTION_DAYS=7

print_header() {
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${BLUE}🔍 SPCS Log Monitor - Snowflake Container Services Log Analysis${NC}"
    echo -e "${BLUE}================================================================${NC}"
}

print_usage() {
    cat << EOF
Usage: $0 [OPTIONS] COMMAND [APP_NAME]

Commands:
    monitor <app_name>     Monitor live logs for an app service
    recent <app_name>      Show recent logs (last 100 lines)
    errors <app_name>      Show only error logs from last 24 hours
    search <app_name> <pattern>  Search logs for specific pattern
    tail <app_name>        Follow live logs (like tail -f)
    analyze <app_name>     Analyze log patterns and provide insights
    export <app_name>      Export logs to file for further analysis
    cleanup               Clean up old log exports
    list                  List all available services for monitoring

Options:
    -h, --help           Show this help message
    -l, --lines N        Number of lines to display (default: 100)
    -d, --days N         Number of days for historical analysis (default: 7)
    -f, --format FORMAT  Output format: plain, json, table (default: plain)
    -o, --output FILE    Output to file instead of stdout
    -v, --verbose        Verbose output

Examples:
    $0 monitor forms_review
    $0 recent forms_review --lines 50
    $0 errors forms_review --days 3
    $0 search forms_review "authentication"
    $0 analyze forms_review --verbose

EOF
}

# Parse command line arguments
LINES=$DEFAULT_LINES
DAYS=$LOG_RETENTION_DAYS
FORMAT="plain"
OUTPUT=""
VERBOSE=false
COMMAND=""
APP_NAME=""
SEARCH_PATTERN=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            print_usage
            exit 0
            ;;
        -l|--lines)
            LINES="$2"
            shift 2
            ;;
        -d|--days)
            DAYS="$2"
            shift 2
            ;;
        -f|--format)
            FORMAT="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        monitor|recent|errors|search|tail|analyze|export|cleanup|list)
            COMMAND="$1"
            shift
            if [[ $COMMAND == "search" ]]; then
                APP_NAME="$1"
                SEARCH_PATTERN="$2"
                shift 2
            elif [[ $COMMAND != "cleanup" && $COMMAND != "list" ]]; then
                APP_NAME="$1"
                shift
            fi
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
done

# Validate inputs
if [[ -z "$COMMAND" ]]; then
    echo -e "${RED}❌ Error: Command is required${NC}"
    print_usage
    exit 1
fi

if [[ $COMMAND != "cleanup" && $COMMAND != "list" && -z "$APP_NAME" ]]; then
    echo -e "${RED}❌ Error: App name is required for command '$COMMAND'${NC}"
    print_usage
    exit 1
fi

# Utility functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

verbose_log() {
    if [[ $VERBOSE == true ]]; then
        echo -e "${PURPLE}🔍 $1${NC}"
    fi
}

# Check if Snowflake CLI is available
check_snowflake_cli() {
    if ! command -v snow &> /dev/null; then
        log_error "Snowflake CLI not found. Please install snowflake-cli-labs"
        exit 1
    fi
    
    verbose_log "Snowflake CLI is available"
}

# Execute Snowflake SQL query
execute_sql() {
    local query="$1"
    local format_type="${2:-json}"
    
    verbose_log "Executing SQL: $query"
    
    if [[ "$format_type" == "json" ]]; then
        snow sql -q "$query" --format json 2>/dev/null || {
            log_error "Failed to execute SQL query"
            return 1
        }
    else
        snow sql -q "$query" --format table 2>/dev/null || {
            log_error "Failed to execute SQL query"
            return 1
        }
    fi
}

# Get service name for app
get_service_name() {
    local app_name="$1"
    echo "${app_name^^}_SERVICE"
}

# Get container name for app
get_container_name() {
    local app_name="$1"
    echo "${app_name}-container"
}

# List available services
list_services() {
    log_info "Listing available SPCS services..."
    
    local query="SHOW SERVICES;"
    local services
    
    if services=$(execute_sql "$query" "table"); then
        echo "$services" | grep -E "(name|status)" || log_warning "No services found"
    else
        log_error "Failed to retrieve services list"
        return 1
    fi
}

# Get recent logs for a service
get_recent_logs() {
    local app_name="$1"
    local lines="${2:-$LINES}"
    local service_name
    local container_name
    
    service_name=$(get_service_name "$app_name")
    container_name=$(get_container_name "$app_name")
    
    log_info "Retrieving last $lines log lines for $app_name..."
    
    local query="SELECT SYSTEM\$GET_SERVICE_LOGS('$service_name', $lines, '$container_name');"
    local logs
    
    if logs=$(execute_sql "$query"); then
        if [[ "$FORMAT" == "json" ]]; then
            echo "$logs"
        else
            echo "$logs" | jq -r '.[0]["SYSTEM$GET_SERVICE_LOGS(\047'$service_name'\047, '$lines', \047'$container_name'\047)"]' 2>/dev/null || echo "$logs"
        fi
    else
        log_error "Failed to retrieve logs for $app_name"
        return 1
    fi
}

# Monitor live logs (periodic refresh)
monitor_logs() {
    local app_name="$1"
    local service_name
    local container_name
    
    service_name=$(get_service_name "$app_name")
    container_name=$(get_container_name "$app_name")
    
    log_info "Starting live log monitoring for $app_name (Press Ctrl+C to stop)..."
    log_info "Service: $service_name, Container: $container_name"
    echo ""
    
    # Track last seen log to avoid duplicates
    local last_timestamp=""
    
    while true; do
        local query="SELECT SYSTEM\$GET_SERVICE_LOGS('$service_name', 20, '$container_name');"
        local logs
        
        if logs=$(execute_sql "$query"); then
            local log_content
            log_content=$(echo "$logs" | jq -r '.[0]["SYSTEM$GET_SERVICE_LOGS(\047'$service_name'\047, 20, \047'$container_name'\047)"]' 2>/dev/null || echo "$logs")
            
            if [[ -n "$log_content" && "$log_content" != "null" ]]; then
                # Extract timestamp from first log line to detect new logs
                local current_timestamp
                current_timestamp=$(echo "$log_content" | head -n1 | grep -o '[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}T[0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}' || echo "")
                
                if [[ "$current_timestamp" != "$last_timestamp" ]]; then
                    echo -e "${CYAN}[$(date '+%H:%M:%S')] New logs:${NC}"
                    echo "$log_content"
                    echo ""
                    last_timestamp="$current_timestamp"
                fi
            fi
        fi
        
        sleep 5
    done
}

# Get error logs only
get_error_logs() {
    local app_name="$1"
    local days="${2:-1}"
    
    log_info "Retrieving error logs for $app_name from last $days days..."
    
    # First get recent logs, then filter for errors
    local logs
    logs=$(get_recent_logs "$app_name" 1000)
    
    if [[ -n "$logs" && "$logs" != "null" ]]; then
        # Filter for common error patterns
        echo "$logs" | grep -i -E "(error|exception|fail|fatal|panic|crash)" --color=always || {
            log_info "No error patterns found in recent logs"
        }
    else
        log_warning "No logs available for filtering"
    fi
}

# Search logs for specific pattern
search_logs() {
    local app_name="$1"
    local pattern="$2"
    
    if [[ -z "$pattern" ]]; then
        log_error "Search pattern is required"
        return 1
    fi
    
    log_info "Searching logs for pattern: '$pattern' in $app_name..."
    
    local logs
    logs=$(get_recent_logs "$app_name" 1000)
    
    if [[ -n "$logs" && "$logs" != "null" ]]; then
        echo "$logs" | grep -i "$pattern" --color=always || {
            log_info "No matches found for pattern '$pattern'"
        }
    else
        log_warning "No logs available for searching"
    fi
}

# Analyze log patterns
analyze_logs() {
    local app_name="$1"
    
    log_info "Analyzing log patterns for $app_name..."
    
    local logs
    logs=$(get_recent_logs "$app_name" 1000)
    
    if [[ -n "$logs" && "$logs" != "null" ]]; then
        echo -e "${BLUE}📊 Log Analysis Summary:${NC}"
        echo ""
        
        # Count total lines
        local total_lines
        total_lines=$(echo "$logs" | wc -l)
        echo -e "Total log lines: ${CYAN}$total_lines${NC}"
        
        # Count error patterns
        local error_count
        error_count=$(echo "$logs" | grep -i -c -E "(error|exception|fail|fatal)" 2>/dev/null || echo "0")
        echo -e "Error messages: ${RED}$error_count${NC}"
        
        # Count warning patterns
        local warning_count
        warning_count=$(echo "$logs" | grep -i -c -E "(warn|warning)" 2>/dev/null || echo "0")
        echo -e "Warning messages: ${YELLOW}$warning_count${NC}"
        
        # Count info patterns
        local info_count
        info_count=$(echo "$logs" | grep -i -c -E "(info|information)" 2>/dev/null || echo "0")
        echo -e "Info messages: ${BLUE}$info_count${NC}"
        
        # Most common log levels
        echo ""
        echo -e "${BLUE}📈 Most frequent log patterns:${NC}"
        echo "$logs" | grep -o -E "(ERROR|WARN|INFO|DEBUG|TRACE)" | sort | uniq -c | sort -rn | head -5
        
        # Recent errors (if any)
        if [[ $error_count -gt 0 ]]; then
            echo ""
            echo -e "${RED}🚨 Recent errors (last 5):${NC}"
            echo "$logs" | grep -i -E "(error|exception|fail|fatal)" | tail -5
        fi
        
        # Health assessment
        echo ""
        echo -e "${BLUE}🏥 Health Assessment:${NC}"
        if [[ $error_count -eq 0 ]]; then
            echo -e "Status: ${GREEN}Healthy${NC} - No errors detected"
        elif [[ $error_count -lt 5 ]]; then
            echo -e "Status: ${YELLOW}Minor Issues${NC} - Few errors detected"
        else
            echo -e "Status: ${RED}Attention Needed${NC} - Multiple errors detected"
        fi
    else
        log_warning "No logs available for analysis"
    fi
}

# Export logs to file
export_logs() {
    local app_name="$1"
    local timestamp
    timestamp=$(date '+%Y%m%d_%H%M%S')
    local filename="${app_name}_logs_${timestamp}.txt"
    
    if [[ -n "$OUTPUT" ]]; then
        filename="$OUTPUT"
    fi
    
    log_info "Exporting logs for $app_name to $filename..."
    
    local logs
    logs=$(get_recent_logs "$app_name" 10000)
    
    if [[ -n "$logs" && "$logs" != "null" ]]; then
        {
            echo "# SPCS Logs Export"
            echo "# App: $app_name"
            echo "# Exported: $(date)"
            echo "# Generated by: SPCS Log Monitor"
            echo ""
            echo "$logs"
        } > "$filename"
        
        log_success "Logs exported to $filename"
        
        # Show file info
        local file_size
        file_size=$(du -h "$filename" | cut -f1)
        echo -e "File size: ${CYAN}$file_size${NC}"
        echo -e "Lines exported: ${CYAN}$(echo "$logs" | wc -l)${NC}"
    else
        log_error "No logs available to export"
        return 1
    fi
}

# Clean up old log exports
cleanup_exports() {
    log_info "Cleaning up log export files older than $LOG_RETENTION_DAYS days..."
    
    local count
    count=$(find . -name "*_logs_*.txt" -type f -mtime +$LOG_RETENTION_DAYS | wc -l)
    
    if [[ $count -gt 0 ]]; then
        find . -name "*_logs_*.txt" -type f -mtime +$LOG_RETENTION_DAYS -delete
        log_success "Cleaned up $count old log files"
    else
        log_info "No old log files to clean up"
    fi
}

# Main execution
main() {
    print_header
    
    check_snowflake_cli
    
    case $COMMAND in
        list)
            list_services
            ;;
        monitor)
            monitor_logs "$APP_NAME"
            ;;
        recent)
            get_recent_logs "$APP_NAME" "$LINES"
            ;;
        errors)
            get_error_logs "$APP_NAME" "$DAYS"
            ;;
        search)
            search_logs "$APP_NAME" "$SEARCH_PATTERN"
            ;;
        tail)
            monitor_logs "$APP_NAME"
            ;;
        analyze)
            analyze_logs "$APP_NAME"
            ;;
        export)
            export_logs "$APP_NAME"
            ;;
        cleanup)
            cleanup_exports
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            print_usage
            exit 1
            ;;
    esac
}

# Trap Ctrl+C for clean exit
trap 'echo -e "\n${YELLOW}⚠️  Log monitoring stopped by user${NC}"; exit 0' INT

# Run main function
main