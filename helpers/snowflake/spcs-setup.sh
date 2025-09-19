#!/bin/bash
# Snowflake SPCS Setup and Troubleshooting Script
# Automates the creation of compute pools, permissions, and diagnostics

set -e

# Configuration
DEFAULT_DATABASE="APPS_DB"
DEFAULT_SCHEMA="AI_APPS"
DEFAULT_WAREHOUSE="COMPUTE_WH"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Snowflake CLI
    if ! command -v snow &> /dev/null; then
        log_error "Snowflake CLI not found. Please install snowflake-cli-labs."
        exit 1
    fi
    
    # Check jq for JSON processing
    if ! command -v jq &> /dev/null; then
        log_warning "jq not found. Installing jq for JSON processing..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y jq
        elif command -v yum &> /dev/null; then
            sudo yum install -y jq
        elif command -v brew &> /dev/null; then
            brew install jq
        else
            log_error "Cannot install jq automatically. Please install jq manually."
            exit 1
        fi
    fi
    
    log_success "Prerequisites check passed"
}

# Test Snowflake connection
test_connection() {
    log_info "Testing Snowflake connection..."
    
    if snow sql -q "SELECT CURRENT_VERSION();" > /dev/null 2>&1; then
        log_success "Connected to Snowflake successfully"
        
        # Get account info
        ACCOUNT_INFO=$(snow sql -q "SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE();" --format=json)
        ACCOUNT=$(echo $ACCOUNT_INFO | jq -r '.[0]["CURRENT_ACCOUNT()"]')
        USER=$(echo $ACCOUNT_INFO | jq -r '.[0]["CURRENT_USER()"]')
        ROLE=$(echo $ACCOUNT_INFO | jq -r '.[0]["CURRENT_ROLE()"]')
        
        log_info "Account: $ACCOUNT"
        log_info "User: $USER"
        log_info "Role: $ROLE"
        
        return 0
    else
        log_error "Failed to connect to Snowflake"
        return 1
    fi
}

# Check SPCS prerequisites
check_spcs_prerequisites() {
    log_info "Checking SPCS prerequisites..."
    
    # Check if user has required privileges
    PRIVILEGES_CHECK=$(snow sql -q "SHOW GRANTS ON ACCOUNT;" --format=json 2>/dev/null | jq -r '.[] | select(.privilege == "CREATE COMPUTE POOL") | .privilege' || echo "")
    
    if [[ -z "$PRIVILEGES_CHECK" ]]; then
        log_warning "CREATE COMPUTE POOL privilege not directly visible. This might require ACCOUNTADMIN role."
    else
        log_success "Required privileges detected"
    fi
    
    # Try to show existing compute pools
    POOLS_COUNT=$(snow sql -q "SHOW COMPUTE POOLS;" --format=json 2>/dev/null | jq 'length' || echo "0")
    log_info "Found $POOLS_COUNT existing compute pools"
    
    # Check for image repositories
    REPOS_COUNT=$(snow sql -q "SHOW IMAGE REPOSITORIES;" --format=json 2>/dev/null | jq 'length' || echo "0")
    log_info "Found $REPOS_COUNT existing image repositories"
}

# Create compute pools
create_compute_pools() {
    log_info "Creating compute pools for SPCS..."
    
    # Production pool
    log_info "Creating production compute pool: APP_POOL"
    snow sql -q "CREATE COMPUTE POOL IF NOT EXISTS APP_POOL
    MIN_NODES = 1
    MAX_NODES = 5
    INSTANCE_FAMILY = CPU_X64_XS
    AUTO_RESUME = TRUE
    AUTO_SUSPEND_SECS = 3600
    COMMENT = 'Production compute pool for applications';" && log_success "APP_POOL created"
    
    # Staging pool
    log_info "Creating staging compute pool: STAGING_POOL"
    snow sql -q "CREATE COMPUTE POOL IF NOT EXISTS STAGING_POOL
    MIN_NODES = 1
    MAX_NODES = 2
    INSTANCE_FAMILY = CPU_X64_XS
    AUTO_RESUME = TRUE
    AUTO_SUSPEND_SECS = 1800
    COMMENT = 'Staging compute pool for testing';" && log_success "STAGING_POOL created"
    
    # Development pool
    log_info "Creating development compute pool: DEV_POOL"
    snow sql -q "CREATE COMPUTE POOL IF NOT EXISTS DEV_POOL
    MIN_NODES = 1
    MAX_NODES = 1
    INSTANCE_FAMILY = CPU_X64_XS
    AUTO_RESUME = TRUE
    AUTO_SUSPEND_SECS = 900
    COMMENT = 'Development compute pool for quick testing';" && log_success "DEV_POOL created"
}

# Create image repository
create_image_repository() {
    log_info "Creating image repository..."
    
    snow sql -q "CREATE IMAGE REPOSITORY IF NOT EXISTS ${DEFAULT_DATABASE}.${DEFAULT_SCHEMA}.APP_IMAGES
    COMMENT = 'Repository for application container images';" && log_success "Image repository created"
    
    # Get repository URL
    REPO_URL=$(snow sql -q "SELECT REPOSITORY_URL FROM INFORMATION_SCHEMA.IMAGE_REPOSITORIES WHERE REPOSITORY_NAME = 'APP_IMAGES';" --format=json | jq -r '.[0].REPOSITORY_URL // "Not found"')
    
    if [[ "$REPO_URL" != "Not found" ]]; then
        log_success "Image repository URL: $REPO_URL"
    else
        log_warning "Could not retrieve image repository URL"
    fi
}

# Setup database and schema
setup_database_schema() {
    log_info "Setting up database and schema..."
    
    # Create database
    snow sql -q "CREATE DATABASE IF NOT EXISTS $DEFAULT_DATABASE
    COMMENT = 'Database for AI applications and services';" && log_success "Database $DEFAULT_DATABASE created"
    
    # Create schema
    snow sql -q "CREATE SCHEMA IF NOT EXISTS $DEFAULT_DATABASE.$DEFAULT_SCHEMA
    COMMENT = 'Schema for AI application deployments';" && log_success "Schema $DEFAULT_SCHEMA created"
    
    # Set context
    snow sql -q "USE DATABASE $DEFAULT_DATABASE;"
    snow sql -q "USE SCHEMA $DEFAULT_SCHEMA;"
}

# Create roles and permissions
setup_roles_permissions() {
    log_info "Setting up roles and permissions..."
    
    # Create app developer role
    snow sql -q "CREATE ROLE IF NOT EXISTS APP_DEVELOPER
    COMMENT = 'Role for AI application developers';" && log_success "APP_DEVELOPER role created"
    
    # Create app service role
    snow sql -q "CREATE ROLE IF NOT EXISTS APP_SERVICE
    COMMENT = 'Role for AI application service accounts';" && log_success "APP_SERVICE role created"
    
    # Grant basic permissions to APP_DEVELOPER
    log_info "Granting permissions to APP_DEVELOPER role..."
    snow sql -q "GRANT USAGE ON DATABASE $DEFAULT_DATABASE TO ROLE APP_DEVELOPER;"
    snow sql -q "GRANT USAGE ON SCHEMA $DEFAULT_DATABASE.$DEFAULT_SCHEMA TO ROLE APP_DEVELOPER;"
    snow sql -q "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA $DEFAULT_DATABASE.$DEFAULT_SCHEMA TO ROLE APP_DEVELOPER;"
    snow sql -q "GRANT ALL PRIVILEGES ON ALL STAGES IN SCHEMA $DEFAULT_DATABASE.$DEFAULT_SCHEMA TO ROLE APP_DEVELOPER;"
    snow sql -q "GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA $DEFAULT_DATABASE.$DEFAULT_SCHEMA TO ROLE APP_DEVELOPER;"
    snow sql -q "GRANT ALL PRIVILEGES ON ALL PROCEDURES IN SCHEMA $DEFAULT_DATABASE.$DEFAULT_SCHEMA TO ROLE APP_DEVELOPER;"
    snow sql -q "GRANT USAGE ON IMAGE REPOSITORY $DEFAULT_DATABASE.$DEFAULT_SCHEMA.APP_IMAGES TO ROLE APP_DEVELOPER;"
    snow sql -q "GRANT USAGE ON WAREHOUSE $DEFAULT_WAREHOUSE TO ROLE APP_DEVELOPER;"
    
    # Grant compute pool permissions
    snow sql -q "GRANT USAGE ON COMPUTE POOL APP_POOL TO ROLE APP_DEVELOPER;" 2>/dev/null || log_warning "Could not grant APP_POOL usage"
    snow sql -q "GRANT USAGE ON COMPUTE POOL STAGING_POOL TO ROLE APP_DEVELOPER;" 2>/dev/null || log_warning "Could not grant STAGING_POOL usage"
    snow sql -q "GRANT USAGE ON COMPUTE POOL DEV_POOL TO ROLE APP_DEVELOPER;" 2>/dev/null || log_warning "Could not grant DEV_POOL usage"
    
    # Grant service creation privileges
    snow sql -q "GRANT CREATE SERVICE ON COMPUTE POOL APP_POOL TO ROLE APP_DEVELOPER;" 2>/dev/null || log_warning "Could not grant CREATE SERVICE on APP_POOL"
    snow sql -q "GRANT CREATE SERVICE ON COMPUTE POOL STAGING_POOL TO ROLE APP_DEVELOPER;" 2>/dev/null || log_warning "Could not grant CREATE SERVICE on STAGING_POOL"
    snow sql -q "GRANT CREATE SERVICE ON COMPUTE POOL DEV_POOL TO ROLE APP_DEVELOPER;" 2>/dev/null || log_warning "Could not grant CREATE SERVICE on DEV_POOL"
    
    log_success "Permissions setup completed"
}

# Diagnose deployment issues
diagnose_deployment() {
    local APP_NAME=$1
    
    if [[ -z "$APP_NAME" ]]; then
        log_error "App name required for diagnosis"
        return 1
    fi
    
    log_info "Diagnosing deployment for $APP_NAME..."
    
    # Check if service exists
    SERVICE_COUNT=$(snow sql -q "SHOW SERVICES LIKE '$APP_NAME%';" --format=json 2>/dev/null | jq 'length' || echo "0")
    log_info "Found $SERVICE_COUNT services for $APP_NAME"
    
    if [[ "$SERVICE_COUNT" -gt 0 ]]; then
        # Get service details
        SERVICE_INFO=$(snow sql -q "SHOW SERVICES LIKE '$APP_NAME%';" --format=json)
        echo "$SERVICE_INFO" | jq -r '.[] | "Service: \(.name), Status: \(.status), Pool: \(.compute_pool)"'
        
        # Get service logs
        log_info "Getting service logs for $APP_NAME..."
        snow sql -q "SELECT SYSTEM$GET_SERVICE_LOGS('$APP_NAME-prod', 0, '$APP_NAME-container');" 2>/dev/null || log_warning "Could not retrieve service logs"
    fi
    
    # Check if user exists
    USER_COUNT=$(snow sql -q "SHOW USERS LIKE '${APP_NAME}_USER';" --format=json 2>/dev/null | jq 'length' || echo "0")
    if [[ "$USER_COUNT" -gt 0 ]]; then
        log_success "App user ${APP_NAME}_USER exists"
    else
        log_warning "App user ${APP_NAME}_USER not found"
    fi
    
    # Check if stage exists
    STAGE_COUNT=$(snow sql -q "SHOW STAGES LIKE '${APP_NAME}_STAGE';" --format=json 2>/dev/null | jq 'length' || echo "0")
    if [[ "$STAGE_COUNT" -gt 0 ]]; then
        log_success "App stage ${APP_NAME}_STAGE exists"
    else
        log_warning "App stage ${APP_NAME}_STAGE not found"
    fi
    
    # Check tables
    TABLE_COUNT=$(snow sql -q "SHOW TABLES LIKE '${APP_NAME}%';" --format=json 2>/dev/null | jq 'length' || echo "0")
    log_info "Found $TABLE_COUNT tables for $APP_NAME"
}

# Main menu
show_menu() {
    echo ""
    echo "🚀 Snowflake SPCS Setup and Troubleshooting Tool"
    echo "================================================"
    echo "1) Check Prerequisites"
    echo "2) Test Connection"
    echo "3) Check SPCS Prerequisites"
    echo "4) Setup Database and Schema"
    echo "5) Create Compute Pools"
    echo "6) Create Image Repository"
    echo "7) Setup Roles and Permissions"
    echo "8) Run Complete Setup (1-7)"
    echo "9) Diagnose App Deployment"
    echo "0) Exit"
    echo ""
    read -p "Choose an option: " choice
}

# Main execution
main() {
    while true; do
        show_menu
        
        case $choice in
            1)
                check_prerequisites
                ;;
            2)
                test_connection
                ;;
            3)
                check_spcs_prerequisites
                ;;
            4)
                setup_database_schema
                ;;
            5)
                create_compute_pools
                ;;
            6)
                create_image_repository
                ;;
            7)
                setup_roles_permissions
                ;;
            8)
                log_info "Running complete SPCS setup..."
                check_prerequisites
                test_connection
                check_spcs_prerequisites
                setup_database_schema
                create_compute_pools
                create_image_repository
                setup_roles_permissions
                log_success "Complete setup finished!"
                ;;
            9)
                read -p "Enter app name to diagnose: " app_name
                diagnose_deployment "$app_name"
                ;;
            0)
                log_info "Goodbye!"
                exit 0
                ;;
            *)
                log_error "Invalid option. Please choose 0-9."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi