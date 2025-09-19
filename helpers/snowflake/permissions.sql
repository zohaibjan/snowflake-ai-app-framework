-- Comprehensive permissions setup for SPCS applications
-- This script creates roles, users, and grants proper permissions for app deployment

USE ROLE ACCOUNTADMIN;

-- =============================================
-- SECTION 1: Create Core Roles
-- =============================================

-- Application developer role
CREATE ROLE IF NOT EXISTS APP_DEVELOPER
    COMMENT = 'Role for AI application developers with SPCS deployment privileges';

-- Application service role  
CREATE ROLE IF NOT EXISTS APP_SERVICE
    COMMENT = 'Role for application service accounts and automated processes';

-- Application admin role
CREATE ROLE IF NOT EXISTS APP_ADMIN
    COMMENT = 'Administrative role for managing applications and compute resources';

-- =============================================
-- SECTION 2: Create Service Users Template
-- =============================================

-- This procedure creates app-specific users with proper permissions
CREATE OR REPLACE PROCEDURE CREATE_APP_USER(
    APP_NAME VARCHAR,
    USER_PASSWORD VARCHAR DEFAULT NULL
)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    user_name VARCHAR;
    generated_password VARCHAR;
BEGIN
    user_name := UPPER(:APP_NAME) || '_USER';
    
    -- Generate password if not provided
    IF (:USER_PASSWORD IS NULL) THEN
        generated_password := RANDSTR(32, RANDOM());
    ELSE
        generated_password := :USER_PASSWORD;
    END IF;
    
    -- Create user
    EXECUTE IMMEDIATE 'CREATE USER IF NOT EXISTS ' || user_name || 
        ' PASSWORD = ''' || generated_password || '''' ||
        ' DEFAULT_ROLE = ''APP_SERVICE''' ||
        ' COMMENT = ''Service user for ' || :APP_NAME || ' application''';
    
    -- Grant role to user
    EXECUTE IMMEDIATE 'GRANT ROLE APP_SERVICE TO USER ' || user_name;
    
    -- Grant app-specific permissions
    EXECUTE IMMEDIATE 'GRANT USAGE ON DATABASE APPS_DB TO USER ' || user_name;
    EXECUTE IMMEDIATE 'GRANT USAGE ON SCHEMA APPS_DB.AI_APPS TO USER ' || user_name;
    EXECUTE IMMEDIATE 'GRANT USAGE ON WAREHOUSE COMPUTE_WH TO USER ' || user_name;
    
    RETURN 'User ' || user_name || ' created with password: ' || generated_password;
END;
$$;

-- =============================================
-- SECTION 3: Database and Schema Permissions
-- =============================================

-- Grant database permissions to APP_DEVELOPER
GRANT USAGE ON DATABASE APPS_DB TO ROLE APP_DEVELOPER;
GRANT USAGE ON SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT CREATE TABLE ON SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT CREATE STAGE ON SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT CREATE VIEW ON SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT CREATE PROCEDURE ON SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT CREATE FUNCTION ON SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;

-- Grant permissions on existing objects
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT ALL PRIVILEGES ON ALL STAGES IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT ALL PRIVILEGES ON ALL VIEWS IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT ALL PRIVILEGES ON ALL PROCEDURES IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;

-- Grant permissions on future objects
GRANT ALL PRIVILEGES ON FUTURE TABLES IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT ALL PRIVILEGES ON FUTURE STAGES IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT ALL PRIVILEGES ON FUTURE VIEWS IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT ALL PRIVILEGES ON FUTURE PROCEDURES IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT ALL PRIVILEGES ON FUTURE FUNCTIONS IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;

-- Grant database permissions to APP_SERVICE
GRANT USAGE ON DATABASE APPS_DB TO ROLE APP_SERVICE;
GRANT USAGE ON SCHEMA APPS_DB.AI_APPS TO ROLE APP_SERVICE;

-- Grant read/write on existing tables and stages
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_SERVICE;
GRANT READ, WRITE ON ALL STAGES IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_SERVICE;
GRANT USAGE ON ALL PROCEDURES IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_SERVICE;
GRANT USAGE ON ALL FUNCTIONS IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_SERVICE;

-- Grant permissions on future objects for APP_SERVICE
GRANT SELECT, INSERT, UPDATE, DELETE ON FUTURE TABLES IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_SERVICE;
GRANT READ, WRITE ON FUTURE STAGES IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_SERVICE;
GRANT USAGE ON FUTURE PROCEDURES IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_SERVICE;
GRANT USAGE ON FUTURE FUNCTIONS IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_SERVICE;

-- =============================================
-- SECTION 4: Warehouse Permissions
-- =============================================

-- Grant warehouse usage
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE APP_DEVELOPER;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE APP_SERVICE;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE APP_ADMIN;

-- APP_ADMIN can manage warehouse
GRANT OPERATE ON WAREHOUSE COMPUTE_WH TO ROLE APP_ADMIN;

-- =============================================
-- SECTION 5: Image Repository Permissions
-- =============================================

-- Grant image repository permissions
GRANT USAGE ON IMAGE REPOSITORY APPS_DB.AI_APPS.APP_IMAGES TO ROLE APP_DEVELOPER;
GRANT READ ON IMAGE REPOSITORY APPS_DB.AI_APPS.APP_IMAGES TO ROLE APP_DEVELOPER;
GRANT WRITE ON IMAGE REPOSITORY APPS_DB.AI_APPS.APP_IMAGES TO ROLE APP_DEVELOPER;

-- Service role needs read access to pull images
GRANT USAGE ON IMAGE REPOSITORY APPS_DB.AI_APPS.APP_IMAGES TO ROLE APP_SERVICE;
GRANT READ ON IMAGE REPOSITORY APPS_DB.AI_APPS.APP_IMAGES TO ROLE APP_SERVICE;

-- Admin role gets full access
GRANT ALL PRIVILEGES ON IMAGE REPOSITORY APPS_DB.AI_APPS.APP_IMAGES TO ROLE APP_ADMIN;

-- =============================================
-- SECTION 6: Compute Pool Permissions
-- =============================================

-- Create compute pools if they don't exist
CREATE COMPUTE POOL IF NOT EXISTS APP_POOL
    MIN_NODES = 1
    MAX_NODES = 5
    INSTANCE_FAMILY = CPU_X64_XS
    AUTO_RESUME = TRUE
    AUTO_SUSPEND_SECS = 3600;

CREATE COMPUTE POOL IF NOT EXISTS STAGING_POOL
    MIN_NODES = 1
    MAX_NODES = 2
    INSTANCE_FAMILY = CPU_X64_XS
    AUTO_RESUME = TRUE
    AUTO_SUSPEND_SECS = 1800;

CREATE COMPUTE POOL IF NOT EXISTS DEV_POOL
    MIN_NODES = 1
    MAX_NODES = 1
    INSTANCE_FAMILY = CPU_X64_XS
    AUTO_RESUME = TRUE
    AUTO_SUSPEND_SECS = 900;

-- Grant compute pool usage permissions
GRANT USAGE ON COMPUTE POOL APP_POOL TO ROLE APP_DEVELOPER;
GRANT USAGE ON COMPUTE POOL STAGING_POOL TO ROLE APP_DEVELOPER;
GRANT USAGE ON COMPUTE POOL DEV_POOL TO ROLE APP_DEVELOPER;

-- Grant service creation permissions
GRANT CREATE SERVICE ON COMPUTE POOL APP_POOL TO ROLE APP_DEVELOPER;
GRANT CREATE SERVICE ON COMPUTE POOL STAGING_POOL TO ROLE APP_DEVELOPER;
GRANT CREATE SERVICE ON COMPUTE POOL DEV_POOL TO ROLE APP_DEVELOPER;

-- APP_ADMIN can manage compute pools
GRANT OPERATE ON COMPUTE POOL APP_POOL TO ROLE APP_ADMIN;
GRANT OPERATE ON COMPUTE POOL STAGING_POOL TO ROLE APP_ADMIN;
GRANT OPERATE ON COMPUTE POOL DEV_POOL TO ROLE APP_ADMIN;

-- =============================================
-- SECTION 7: Service Management Permissions
-- =============================================

-- Create procedure to grant service permissions to specific users
CREATE OR REPLACE PROCEDURE GRANT_SERVICE_PERMISSIONS(
    APP_NAME VARCHAR,
    COMPUTE_POOL_NAME VARCHAR DEFAULT 'APP_POOL'
)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    user_name VARCHAR;
    service_pattern VARCHAR;
BEGIN
    user_name := UPPER(:APP_NAME) || '_USER';
    service_pattern := :APP_NAME || '%';
    
    -- Grant compute pool usage
    EXECUTE IMMEDIATE 'GRANT USAGE ON COMPUTE POOL ' || :COMPUTE_POOL_NAME || ' TO USER ' || user_name;
    
    -- Note: Service-specific permissions are handled by the service itself
    -- The user will have access to their own service through the compute pool
    
    RETURN 'Service permissions granted to ' || user_name || ' on ' || :COMPUTE_POOL_NAME;
END;
$$;

-- =============================================
-- SECTION 8: Monitoring and Logging Permissions
-- =============================================

-- Grant ability to call system functions for monitoring
GRANT EXECUTE ON FUNCTION SYSTEM$GET_SERVICE_LOGS(VARCHAR, NUMBER, VARCHAR) TO ROLE APP_DEVELOPER;
GRANT EXECUTE ON FUNCTION SYSTEM$GET_SERVICE_STATUS(VARCHAR) TO ROLE APP_DEVELOPER;
GRANT EXECUTE ON FUNCTION SYSTEM$REGISTRY_HOSTNAME() TO ROLE APP_DEVELOPER;

-- Allow APP_SERVICE to log events
GRANT EXECUTE ON FUNCTION SYSTEM$GET_SERVICE_LOGS(VARCHAR, NUMBER, VARCHAR) TO ROLE APP_SERVICE;

-- =============================================
-- SECTION 9: Create User Management Procedures
-- =============================================

-- Procedure to setup complete app permissions
CREATE OR REPLACE PROCEDURE SETUP_APP_PERMISSIONS(
    APP_NAME VARCHAR,
    USER_PASSWORD VARCHAR DEFAULT NULL,
    ENVIRONMENT VARCHAR DEFAULT 'PROD'
)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    user_creation_result VARCHAR;
    stage_name VARCHAR;
    compute_pool VARCHAR;
    permission_result VARCHAR;
BEGIN
    -- Create app user
    CALL CREATE_APP_USER(:APP_NAME, :USER_PASSWORD);
    
    -- Create app-specific stage
    stage_name := UPPER(:APP_NAME) || '_STAGE';
    EXECUTE IMMEDIATE 'CREATE STAGE IF NOT EXISTS ' || stage_name || 
        ' DIRECTORY = ( ENABLE = TRUE )' ||
        ' COMMENT = ''Stage for ' || :APP_NAME || ' application files''';
    
    -- Grant stage permissions to app user
    EXECUTE IMMEDIATE 'GRANT USAGE ON STAGE ' || stage_name || ' TO USER ' || UPPER(:APP_NAME) || '_USER';
    EXECUTE IMMEDIATE 'GRANT READ, WRITE ON STAGE ' || stage_name || ' TO USER ' || UPPER(:APP_NAME) || '_USER';
    
    -- Determine compute pool based on environment
    IF (UPPER(:ENVIRONMENT) = 'DEV') THEN
        compute_pool := 'DEV_POOL';
    ELSEIF (UPPER(:ENVIRONMENT) = 'STAGING') THEN
        compute_pool := 'STAGING_POOL';
    ELSE
        compute_pool := 'APP_POOL';
    END IF;
    
    -- Grant service permissions
    CALL GRANT_SERVICE_PERMISSIONS(:APP_NAME, compute_pool);
    
    RETURN 'Complete setup completed for ' || :APP_NAME || ' in ' || :ENVIRONMENT || ' environment';
END;
$$;

-- Procedure to cleanup app resources
CREATE OR REPLACE PROCEDURE CLEANUP_APP_RESOURCES(
    APP_NAME VARCHAR,
    DELETE_USER BOOLEAN DEFAULT FALSE
)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    user_name VARCHAR;
    stage_name VARCHAR;
    service_pattern VARCHAR;
    cleanup_results VARCHAR DEFAULT '';
BEGIN
    user_name := UPPER(:APP_NAME) || '_USER';
    stage_name := UPPER(:APP_NAME) || '_STAGE';
    service_pattern := :APP_NAME || '%';
    
    -- Drop services
    FOR service_record IN (SELECT name FROM INFORMATION_SCHEMA.SERVICES WHERE name LIKE service_pattern) DO
        EXECUTE IMMEDIATE 'DROP SERVICE IF EXISTS ' || service_record.name;
        cleanup_results := cleanup_results || 'Dropped service: ' || service_record.name || '; ';
    END FOR;
    
    -- Drop app-specific tables
    FOR table_record IN (SELECT table_name FROM INFORMATION_SCHEMA.TABLES 
                         WHERE table_schema = 'AI_APPS' AND table_name LIKE UPPER(:APP_NAME) || '%') DO
        EXECUTE IMMEDIATE 'DROP TABLE IF EXISTS ' || table_record.table_name;
        cleanup_results := cleanup_results || 'Dropped table: ' || table_record.table_name || '; ';
    END FOR;
    
    -- Drop stage
    EXECUTE IMMEDIATE 'DROP STAGE IF EXISTS ' || stage_name;
    cleanup_results := cleanup_results || 'Dropped stage: ' || stage_name || '; ';
    
    -- Optionally drop user
    IF (:DELETE_USER) THEN
        EXECUTE IMMEDIATE 'DROP USER IF EXISTS ' || user_name;
        cleanup_results := cleanup_results || 'Dropped user: ' || user_name || '; ';
    END IF;
    
    RETURN 'Cleanup completed: ' || cleanup_results;
END;
$$;

-- =============================================
-- SECTION 10: Grant Procedure Usage
-- =============================================

-- Grant procedure usage to appropriate roles
GRANT USAGE ON PROCEDURE CREATE_APP_USER(VARCHAR, VARCHAR) TO ROLE APP_DEVELOPER;
GRANT USAGE ON PROCEDURE GRANT_SERVICE_PERMISSIONS(VARCHAR, VARCHAR) TO ROLE APP_DEVELOPER;
GRANT USAGE ON PROCEDURE SETUP_APP_PERMISSIONS(VARCHAR, VARCHAR, VARCHAR) TO ROLE APP_DEVELOPER;
GRANT USAGE ON PROCEDURE CLEANUP_APP_RESOURCES(VARCHAR, BOOLEAN) TO ROLE APP_ADMIN;

-- =============================================
-- SECTION 11: Role Hierarchy
-- =============================================

-- Grant roles to ACCOUNTADMIN for management
GRANT ROLE APP_DEVELOPER TO ROLE ACCOUNTADMIN;
GRANT ROLE APP_SERVICE TO ROLE ACCOUNTADMIN;
GRANT ROLE APP_ADMIN TO ROLE ACCOUNTADMIN;

-- APP_ADMIN inherits APP_DEVELOPER privileges
GRANT ROLE APP_DEVELOPER TO ROLE APP_ADMIN;
GRANT ROLE APP_SERVICE TO ROLE APP_ADMIN;

-- =============================================
-- SECTION 12: Display Setup Summary
-- =============================================

-- Show created roles
SELECT 'Permissions setup completed!' AS STATUS;

-- Display role information
SELECT 'Created Roles:' AS INFO
UNION ALL SELECT '  - APP_DEVELOPER: For application development and deployment'
UNION ALL SELECT '  - APP_SERVICE: For application service accounts'  
UNION ALL SELECT '  - APP_ADMIN: For managing applications and resources'
UNION ALL SELECT ''
UNION ALL SELECT 'Available Procedures:'
UNION ALL SELECT '  - CREATE_APP_USER(app_name, password): Create app-specific user'
UNION ALL SELECT '  - SETUP_APP_PERMISSIONS(app_name, password, env): Complete app setup'
UNION ALL SELECT '  - CLEANUP_APP_RESOURCES(app_name, delete_user): Cleanup app resources'
UNION ALL SELECT ''
UNION ALL SELECT 'Usage Examples:'
UNION ALL SELECT '  CALL SETUP_APP_PERMISSIONS(''my_app'', ''secure_password'', ''PROD'');'
UNION ALL SELECT '  CALL CLEANUP_APP_RESOURCES(''my_app'', FALSE);';

-- Show compute pool status
SHOW COMPUTE POOLS;