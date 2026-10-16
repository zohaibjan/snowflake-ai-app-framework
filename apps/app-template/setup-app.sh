#!/bin/bash
# Setup script for {{APP_NAME}} Snowflake objects
# This script creates all necessary Snowflake objects for your app

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="{{APP_NAME}}"
APP_NAME_UPPER="${APP_NAME^^}"
DB_NAME="${APP_NAME_UPPER}_DB"
SCHEMA_NAME="AI_APPS"
STAGE_NAME="${APP_NAME_UPPER}_STAGE"
TABLE_NAME="${APP_NAME_UPPER}_ANALYSES"
USER_NAME="${APP_NAME_UPPER}_USER"

print_header() {
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${BLUE}🏗️  Setting up Snowflake objects for ${APP_NAME}${NC}"
    echo -e "${BLUE}================================================================${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if snow CLI is available
check_snow_cli() {
    if ! command -v snow &> /dev/null; then
        print_error "Snowflake CLI not found. Please install snowflake-cli-labs"
        exit 1
    fi
    print_success "Snowflake CLI is available"
}

# Execute SQL command
execute_sql() {
    local sql="$1"
    local description="$2"
    
    print_info "Executing: $description"
    
    if snow sql -q "$sql" > /dev/null 2>&1; then
        print_success "$description completed"
    else
        print_warning "$description may have issues (this might be normal if objects already exist)"
    fi
}

# Main setup function
setup_snowflake_objects() {
    print_header
    
    print_info "Setting up objects for app: ${APP_NAME}"
    print_info "Database: ${DB_NAME}"
    print_info "Schema: ${SCHEMA_NAME}"
    print_info "Stage: ${STAGE_NAME}"
    print_info "Table: ${TABLE_NAME}"
    print_info "User: ${USER_NAME}"
    echo ""
    
    # Create database
    execute_sql "CREATE DATABASE IF NOT EXISTS ${DB_NAME};" "Create database ${DB_NAME}"
    
    # Use database
    execute_sql "USE DATABASE ${DB_NAME};" "Switch to database ${DB_NAME}"
    
    # Create schema
    execute_sql "CREATE SCHEMA IF NOT EXISTS ${SCHEMA_NAME};" "Create schema ${SCHEMA_NAME}"
    
    # Use schema
    execute_sql "USE SCHEMA ${SCHEMA_NAME};" "Switch to schema ${SCHEMA_NAME}"
    
    # Create file upload stage
    execute_sql "CREATE STAGE IF NOT EXISTS ${STAGE_NAME} 
                 DIRECTORY = (ENABLE = TRUE)
                 COMMENT = 'File upload stage for ${APP_NAME} application';" "Create file upload stage"
    
    # Create analysis results table
    execute_sql "CREATE TABLE IF NOT EXISTS ${TABLE_NAME} (
        ANALYSIS_ID STRING PRIMARY KEY,
        FILE_NAME STRING NOT NULL,
        ANALYSIS_TYPE STRING DEFAULT 'general',
        MODEL_USED STRING DEFAULT 'mistral-large',
        ANALYSIS_RESULT VARIANT,
        INPUT_LENGTH INTEGER,
        OUTPUT_LENGTH INTEGER,
        SUCCESS BOOLEAN DEFAULT TRUE,
        CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
        UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
    ) COMMENT = 'Analysis results for ${APP_NAME} application';" "Create analysis results table"
    
    # Create app-specific user (optional - for production deployments)
    print_info "Creating app-specific user (this may require ACCOUNTADMIN privileges)"
    execute_sql "CREATE USER IF NOT EXISTS ${USER_NAME} 
                 DEFAULT_WAREHOUSE = 'COMPUTE_WH'
                 DEFAULT_DATABASE = '${DB_NAME}'
                 DEFAULT_SCHEMA = '${SCHEMA_NAME}'
                 COMMENT = 'Service user for ${APP_NAME} application';" "Create app user"
    
    # Grant necessary permissions to app user
    execute_sql "GRANT USAGE ON DATABASE ${DB_NAME} TO USER ${USER_NAME};" "Grant database usage to app user"
    execute_sql "GRANT USAGE ON SCHEMA ${DB_NAME}.${SCHEMA_NAME} TO USER ${USER_NAME};" "Grant schema usage to app user"
    execute_sql "GRANT READ, WRITE ON STAGE ${DB_NAME}.${SCHEMA_NAME}.${STAGE_NAME} TO USER ${USER_NAME};" "Grant stage permissions to app user"
    execute_sql "GRANT SELECT, INSERT, UPDATE ON TABLE ${DB_NAME}.${SCHEMA_NAME}.${TABLE_NAME} TO USER ${USER_NAME};" "Grant table permissions to app user"
    execute_sql "GRANT USAGE ON WAREHOUSE COMPUTE_WH TO USER ${USER_NAME};" "Grant warehouse usage to app user"
    
    # Grant Cortex AI permissions
    print_info "Granting Cortex AI permissions (may require additional privileges)"
    execute_sql "GRANT USAGE ON DATABASE SNOWFLAKE TO USER ${USER_NAME};" "Grant Snowflake database usage"
    execute_sql "GRANT USAGE ON SCHEMA SNOWFLAKE.CORTEX TO USER ${USER_NAME};" "Grant Cortex schema usage"
    
    echo ""
    print_success "Setup completed for ${APP_NAME}!"
    
    # Display summary
    echo -e "${BLUE}📋 Setup Summary:${NC}"
    echo -e "   Database: ${GREEN}${DB_NAME}${NC}"
    echo -e "   Schema: ${GREEN}${SCHEMA_NAME}${NC}"
    echo -e "   Stage: ${GREEN}${STAGE_NAME}${NC}"
    echo -e "   Table: ${GREEN}${TABLE_NAME}${NC}"
    echo -e "   User: ${GREEN}${USER_NAME}${NC}"
    echo ""
    echo -e "${YELLOW}📝 Next Steps:${NC}"
    echo -e "   1. Update your .env file with the database and schema names"
    echo -e "   2. Test your Snowflake connection: ${BLUE}python -c 'from utils.snowflake_utils import get_snowflake_session; print(get_snowflake_session())'${NC}"
    echo -e "   3. Run your application: ${BLUE}streamlit run app.py${NC}"
    echo -e "   4. Configure key-pair authentication for ${USER_NAME} before use; no password is provisioned"
}

# Cleanup function (optional)
cleanup_objects() {
    print_warning "This will delete all ${APP_NAME} objects from Snowflake!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up ${APP_NAME} objects..."
        
        execute_sql "DROP TABLE IF EXISTS ${DB_NAME}.${SCHEMA_NAME}.${TABLE_NAME};" "Drop analysis table"
        execute_sql "DROP STAGE IF EXISTS ${DB_NAME}.${SCHEMA_NAME}.${STAGE_NAME};" "Drop file stage"
        execute_sql "DROP USER IF EXISTS ${USER_NAME};" "Drop app user"
        execute_sql "DROP DATABASE IF EXISTS ${DB_NAME};" "Drop database"
        
        print_success "Cleanup completed"
    else
        print_info "Cleanup cancelled"
    fi
}

# Test connection function
test_connection() {
    print_info "Testing Snowflake connection..."
    
    if snow sql -q "SELECT CURRENT_VERSION(), CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE();" > /dev/null 2>&1; then
        print_success "Connection test successful"
        
        # Test Cortex AI
        print_info "Testing Cortex AI availability..."
        if snow sql -q "SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large', 'Hello, this is a test.') as test_response;" > /dev/null 2>&1; then
            print_success "Cortex AI is available"
        else
            print_warning "Cortex AI may not be available or accessible"
        fi
    else
        print_error "Connection test failed. Please check your Snowflake configuration."
        exit 1
    fi
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  setup     Set up all Snowflake objects for ${APP_NAME} (default)"
    echo "  test      Test Snowflake connection and Cortex AI availability"
    echo "  cleanup   Remove all ${APP_NAME} objects from Snowflake"
    echo "  help      Show this usage information"
    echo ""
    echo "Examples:"
    echo "  $0              # Set up all objects"
    echo "  $0 setup        # Set up all objects"
    echo "  $0 test         # Test connection"
    echo "  $0 cleanup      # Clean up objects"
}

# Main script logic
main() {
    check_snow_cli
    
    case "${1:-setup}" in
        setup)
            setup_snowflake_objects
            ;;
        test)
            test_connection
            ;;
        cleanup)
            cleanup_objects
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"