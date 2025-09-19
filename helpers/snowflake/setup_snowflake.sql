-- Comprehensive Snowflake Setup Script
-- Creates all necessary objects for SPCS deployment and application development

-- =============================================
-- SECTION 1: Basic Setup
-- =============================================

-- Set context (modify as needed)
USE ROLE ACCOUNTADMIN;
USE WAREHOUSE COMPUTE_WH;

-- =============================================
-- SECTION 2: Create Database and Schema
-- =============================================

-- Create application database
CREATE DATABASE IF NOT EXISTS APPS_DB
    COMMENT = 'Database for Streamlit applications and AI services';

-- Create application schema
CREATE SCHEMA IF NOT EXISTS APPS_DB.AI_APPS
    COMMENT = 'Schema for AI application deployments';

-- Set context
USE DATABASE APPS_DB;
USE SCHEMA AI_APPS;

-- =============================================
-- SECTION 3: Create Stages for File Storage
-- =============================================

-- Default stage for file uploads
CREATE STAGE IF NOT EXISTS DEFAULT_STAGE
    DIRECTORY = ( ENABLE = TRUE )
    COMMENT = 'Default stage for application file uploads';

-- Documents stage for PDF and document processing
CREATE STAGE IF NOT EXISTS DOCUMENTS_STAGE
    DIRECTORY = ( ENABLE = TRUE )
    FILE_FORMAT = ( TYPE = 'JSON' STRIP_OUTER_ARRAY = TRUE )
    COMMENT = 'Stage for document processing applications';

-- Models stage for AI model artifacts
CREATE STAGE IF NOT EXISTS MODELS_STAGE
    DIRECTORY = ( ENABLE = TRUE )
    COMMENT = 'Stage for AI model storage and artifacts';

-- =============================================
-- SECTION 4: Create Image Repository
-- =============================================

-- Image repository for container images
CREATE IMAGE REPOSITORY IF NOT EXISTS APP_IMAGES
    COMMENT = 'Repository for application container images';

-- Show repository URL for reference
SHOW IMAGE REPOSITORIES;

-- =============================================
-- SECTION 5: Create Compute Pools
-- =============================================

-- Production compute pool
CREATE COMPUTE POOL IF NOT EXISTS APP_POOL
    MIN_NODES = 1
    MAX_NODES = 5
    INSTANCE_FAMILY = CPU_X64_XS
    AUTO_RESUME = TRUE
    AUTO_SUSPEND_SECS = 3600
    COMMENT = 'Production compute pool for applications';

-- Staging compute pool (smaller)
CREATE COMPUTE POOL IF NOT EXISTS STAGING_POOL
    MIN_NODES = 1
    MAX_NODES = 2
    INSTANCE_FAMILY = CPU_X64_XS
    AUTO_RESUME = TRUE
    AUTO_SUSPEND_SECS = 1800
    COMMENT = 'Staging compute pool for testing';

-- Development compute pool (minimal)
CREATE COMPUTE POOL IF NOT EXISTS DEV_POOL
    MIN_NODES = 1
    MAX_NODES = 1
    INSTANCE_FAMILY = CPU_X64_XS
    AUTO_RESUME = TRUE
    AUTO_SUSPEND_SECS = 900
    COMMENT = 'Development compute pool for quick testing';

-- =============================================
-- SECTION 6: Create Application Tables
-- =============================================

-- User feedback table
CREATE TABLE IF NOT EXISTS USER_FEEDBACK (
    ID NUMBER AUTOINCREMENT PRIMARY KEY,
    APP_NAME VARCHAR(100) NOT NULL,
    USER_SESSION VARCHAR(100),
    FEEDBACK_TYPE VARCHAR(50) NOT NULL,
    FEEDBACK_TEXT TEXT,
    RATING NUMBER(1,0) CHECK (RATING BETWEEN 1 AND 5),
    METADATA VARIANT,
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(100) DEFAULT CURRENT_USER()
);

-- Document analysis results table
CREATE TABLE IF NOT EXISTS DOCUMENT_ANALYSIS (
    ID NUMBER AUTOINCREMENT PRIMARY KEY,
    APP_NAME VARCHAR(100) NOT NULL,
    DOCUMENT_NAME VARCHAR(500) NOT NULL,
    DOCUMENT_STAGE_PATH VARCHAR(1000),
    ANALYSIS_TYPE VARCHAR(100) NOT NULL,
    ANALYSIS_PROVIDER VARCHAR(50),
    ANALYSIS_RESULTS VARIANT,
    PROCESSING_TIME_SECONDS NUMBER(10,2),
    STATUS VARCHAR(50) DEFAULT 'COMPLETED',
    ERROR_MESSAGE TEXT,
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(100) DEFAULT CURRENT_USER()
);

-- Application logs table
CREATE TABLE IF NOT EXISTS APP_LOGS (
    ID NUMBER AUTOINCREMENT PRIMARY KEY,
    APP_NAME VARCHAR(100) NOT NULL,
    SERVICE_NAME VARCHAR(100),
    LOG_LEVEL VARCHAR(20) NOT NULL,
    LOG_MESSAGE TEXT NOT NULL,
    LOG_DATA VARIANT,
    USER_SESSION VARCHAR(100),
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =============================================
-- SECTION 7: Create Views for Monitoring
-- =============================================

-- Recent feedback view
CREATE OR REPLACE VIEW RECENT_FEEDBACK AS
SELECT 
    APP_NAME,
    FEEDBACK_TYPE,
    AVG(RATING) AS AVG_RATING,
    COUNT(*) AS FEEDBACK_COUNT,
    MAX(CREATED_AT) AS LAST_FEEDBACK
FROM USER_FEEDBACK
WHERE CREATED_AT >= DATEADD('day', -30, CURRENT_TIMESTAMP())
GROUP BY APP_NAME, FEEDBACK_TYPE
ORDER BY LAST_FEEDBACK DESC;

-- Document processing summary
CREATE OR REPLACE VIEW DOCUMENT_PROCESSING_STATS AS
SELECT 
    APP_NAME,
    ANALYSIS_TYPE,
    ANALYSIS_PROVIDER,
    COUNT(*) AS DOCUMENTS_PROCESSED,
    AVG(PROCESSING_TIME_SECONDS) AS AVG_PROCESSING_TIME,
    COUNT(CASE WHEN STATUS = 'COMPLETED' THEN 1 END) AS SUCCESSFUL_ANALYSES,
    COUNT(CASE WHEN STATUS = 'FAILED' THEN 1 END) AS FAILED_ANALYSES,
    MAX(CREATED_AT) AS LAST_ANALYSIS
FROM DOCUMENT_ANALYSIS
WHERE CREATED_AT >= DATEADD('day', -7, CURRENT_TIMESTAMP())
GROUP BY APP_NAME, ANALYSIS_TYPE, ANALYSIS_PROVIDER
ORDER BY DOCUMENTS_PROCESSED DESC;

-- Application error summary
CREATE OR REPLACE VIEW ERROR_SUMMARY AS
SELECT 
    APP_NAME,
    SERVICE_NAME,
    LOG_LEVEL,
    COUNT(*) AS ERROR_COUNT,
    MAX(CREATED_AT) AS LAST_ERROR,
    ARRAY_AGG(DISTINCT SUBSTR(LOG_MESSAGE, 1, 100)) AS SAMPLE_MESSAGES
FROM APP_LOGS
WHERE LOG_LEVEL IN ('ERROR', 'CRITICAL')
    AND CREATED_AT >= DATEADD('hour', -24, CURRENT_TIMESTAMP())
GROUP BY APP_NAME, SERVICE_NAME, LOG_LEVEL
ORDER BY ERROR_COUNT DESC;

-- =============================================
-- SECTION 8: Create Functions for Common Operations
-- =============================================

-- Function to clean old logs
CREATE OR REPLACE PROCEDURE CLEANUP_OLD_LOGS(DAYS_TO_KEEP NUMBER)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    deleted_count NUMBER;
BEGIN
    DELETE FROM APP_LOGS 
    WHERE CREATED_AT < DATEADD('day', -:DAYS_TO_KEEP, CURRENT_TIMESTAMP());
    
    deleted_count := SQLROWCOUNT;
    RETURN 'Deleted ' || deleted_count || ' log entries older than ' || DAYS_TO_KEEP || ' days';
END;
$$;

-- Function to get app health status
CREATE OR REPLACE FUNCTION GET_APP_HEALTH_STATUS(APP_NAME_PARAM VARCHAR)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
SELECT OBJECT_CONSTRUCT(
    'app_name', APP_NAME_PARAM,
    'recent_errors', (
        SELECT COUNT(*) 
        FROM APP_LOGS 
        WHERE APP_NAME = APP_NAME_PARAM 
            AND LOG_LEVEL = 'ERROR' 
            AND CREATED_AT >= DATEADD('hour', -1, CURRENT_TIMESTAMP())
    ),
    'recent_feedback_count', (
        SELECT COUNT(*) 
        FROM USER_FEEDBACK 
        WHERE APP_NAME = APP_NAME_PARAM 
            AND CREATED_AT >= DATEADD('day', -1, CURRENT_TIMESTAMP())
    ),
    'avg_rating', (
        SELECT AVG(RATING) 
        FROM USER_FEEDBACK 
        WHERE APP_NAME = APP_NAME_PARAM 
            AND CREATED_AT >= DATEADD('day', -7, CURRENT_TIMESTAMP())
    ),
    'last_activity', (
        SELECT MAX(CREATED_AT) 
        FROM APP_LOGS 
        WHERE APP_NAME = APP_NAME_PARAM
    )
)
$$;

-- =============================================
-- SECTION 9: Create Notification Procedures
-- =============================================

-- Procedure to log application events
CREATE OR REPLACE PROCEDURE LOG_APP_EVENT(
    APP_NAME_PARAM VARCHAR,
    SERVICE_NAME_PARAM VARCHAR,
    LOG_LEVEL_PARAM VARCHAR,
    MESSAGE_PARAM VARCHAR,
    DATA_PARAM VARIANT DEFAULT NULL,
    SESSION_PARAM VARCHAR DEFAULT NULL
)
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    INSERT INTO APP_LOGS (APP_NAME, SERVICE_NAME, LOG_LEVEL, LOG_MESSAGE, LOG_DATA, USER_SESSION)
    VALUES (:APP_NAME_PARAM, :SERVICE_NAME_PARAM, :LOG_LEVEL_PARAM, :MESSAGE_PARAM, :DATA_PARAM, :SESSION_PARAM);
    
    RETURN 'Event logged successfully';
END;
$$;

-- =============================================
-- SECTION 10: Set up File Formats
-- =============================================

-- JSON file format for structured data
CREATE FILE FORMAT IF NOT EXISTS JSON_FORMAT
    TYPE = JSON
    STRIP_OUTER_ARRAY = TRUE
    COMMENT = 'Standard JSON format for application data';

-- CSV file format for tabular data
CREATE FILE FORMAT IF NOT EXISTS CSV_FORMAT
    TYPE = CSV
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    NULL_IF = ('', 'NULL', 'null')
    EMPTY_FIELD_AS_NULL = TRUE
    COMMENT = 'Standard CSV format with headers';

-- =============================================
-- SECTION 11: Grant Basic Permissions
-- =============================================

-- Create application role if it doesn't exist
CREATE ROLE IF NOT EXISTS APP_DEVELOPER;

-- Grant basic permissions to the application role
GRANT USAGE ON DATABASE APPS_DB TO ROLE APP_DEVELOPER;
GRANT USAGE ON SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT ALL PRIVILEGES ON ALL STAGES IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT ALL PRIVILEGES ON ALL FILE FORMATS IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT ALL PRIVILEGES ON ALL PROCEDURES IN SCHEMA APPS_DB.AI_APPS TO ROLE APP_DEVELOPER;
GRANT USAGE ON IMAGE REPOSITORY APPS_DB.AI_APPS.APP_IMAGES TO ROLE APP_DEVELOPER;

-- Grant compute pool usage
GRANT USAGE ON COMPUTE POOL APP_POOL TO ROLE APP_DEVELOPER;
GRANT USAGE ON COMPUTE POOL STAGING_POOL TO ROLE APP_DEVELOPER;
GRANT USAGE ON COMPUTE POOL DEV_POOL TO ROLE APP_DEVELOPER;

-- Grant service creation privileges
GRANT CREATE SERVICE ON COMPUTE POOL APP_POOL TO ROLE APP_DEVELOPER;
GRANT CREATE SERVICE ON COMPUTE POOL STAGING_POOL TO ROLE APP_DEVELOPER;
GRANT CREATE SERVICE ON COMPUTE POOL DEV_POOL TO ROLE APP_DEVELOPER;

-- =============================================
-- SECTION 12: Display Setup Summary
-- =============================================

-- Show created objects
SELECT 'Setup completed successfully!' AS STATUS;

-- Display key information
SELECT 'Database: APPS_DB' AS INFO
UNION ALL SELECT 'Schema: AI_APPS'
UNION ALL SELECT 'Stages: DEFAULT_STAGE, DOCUMENTS_STAGE, MODELS_STAGE'
UNION ALL SELECT 'Compute Pools: APP_POOL, STAGING_POOL, DEV_POOL'
UNION ALL SELECT 'Image Repository: APP_IMAGES'
UNION ALL SELECT 'Tables: USER_FEEDBACK, DOCUMENT_ANALYSIS, APP_LOGS'
UNION ALL SELECT 'Role Created: APP_DEVELOPER';

-- Show compute pool status
SHOW COMPUTE POOLS;

-- Show image repository details
SELECT REPOSITORY_URL FROM INFORMATION_SCHEMA.IMAGE_REPOSITORIES WHERE REPOSITORY_NAME = 'APP_IMAGES';