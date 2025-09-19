# AI App Development Framework

## 🚀 Quick Start for AI Agents

This framework enables rapid development of AI-powered Streamlit applications with Snowflake integration. Follow these instructions to build new apps efficiently.

## 📁 Framework Structure

```
framework/                    # THIS REPOSITORY - Framework code and templates  
├── INSTRUCTIONS.md          # This file - main guidance for AI agents
├── AGENTS.md               # Specific agent instructions and patterns
├── README.md               # Human-readable documentation
├── apps/                   # 📋 TEMPLATES AND EXAMPLES
│   ├── app-template/       # Complete manual app template
│   └── README.md           # Apps directory documentation
├── templates/              # Reusable templates and patterns
│   ├── components/         # UI components (sidebar, file_uploader, etc.)
│   ├── utils/             # Utility functions (snowflake, AI, etc.)
│   ├── app_template.py    # Base Streamlit app template
│   ├── deployment/        # SPCS deployment templates
│   ├── Dockerfile         # Container template
│   └── requirements.txt   # Python dependencies
├── helpers/               # Helper scripts and utilities
│   ├── docker/           # Docker-related helpers
│   ├── github/           # GitHub workflow templates
│   ├── snowflake/        # Snowflake setup and utilities
│   └── deployment/       # SPCS deployment helpers
└── .github/
    └── workflows/        # CI/CD pipeline templates

../apps/                      # YOUR ACTUAL APPS GO HERE (outside framework)
├── my-first-app/           # Copy app-template here and customize
├── document-analyzer/      # Another app
├── data-processor/         # Another app
└── production-app/         # Production-ready app
```

## 🎯 Building a New App

### Method 1: Use the Complete Template (Recommended)
1. **Copy the app template**:
   ```bash
   cp -r framework/apps/app-template/ ../apps/your-app-name/
   cd ../apps/your-app-name/
   ```

2. **Customize app name** (replace all placeholders):
   ```bash
   find . -name "*.py" -o -name "*.md" -o -name "*.sh" -o -name "Dockerfile" | xargs sed -i 's/{{APP_NAME}}/YOUR_APP_NAME/g'
   find . -name "*.py" -o -name "*.md" -o -name "*.sh" -o -name "Dockerfile" | xargs sed -i 's/{{app_name}}/your_app_name/g'
   ```

3. **Follow the README.md** in your new app directory for complete setup instructions

### Method 2: Build from Individual Templates
1. Create a new folder in `../apps/` with your app name (e.g., `../apps/my-ai-app/`)
2. Copy the base template structure from `templates/`
3. Customize for your specific use case

### Essential Files Every App Needs
```
../apps/your-app-name/         # Your app (copied from framework/apps/app-template/)
├── app.py                     # Main Streamlit application  
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container configuration
├── README.md                  # App-specific documentation
├── .env.example              # Environment variables template
├── setup-app.sh              # Automated Snowflake setup script
├── components/               # UI components 
│   ├── __init__.py
│   ├── sidebar.py           # Navigation sidebar
│   ├── file_uploader.py     # File upload component
│   └── feedback_display.py  # Results display component
└── utils/                   # Utility functions
    ├── __init__.py
    ├── snowflake_utils.py   # Snowflake connection utilities
    ├── ai_analyzer.py       # Cortex AI integration
    ├── pdf_processor.py     # Document processing
    └── stage_uploads.py     # File upload to Snowflake stages
```
│   ├── file_uploader.py
│   └── feedback_display.py
├── utils/               # Utility functions (copied from framework)
│   ├── __init__.py
│   ├── snowflake_utils.py
│   ├── stage_uploads.py
│   ├── pdf_processor.py
│   └── ai_analyzer.py
└── setup/              # App-specific setup scripts
    ├── setup-app.sh    # Snowflake objects creation
    └── cleanup-app.sh  # Cleanup script
```

### 🏗️ App-Specific Snowflake Objects

Each app automatically creates:
- **Stage**: `{APP_NAME}_STAGE` for file storage
- **User**: `{APP_NAME}_USER` for service authentication  
- **Tables**: `{APP_NAME}_LOGS`, `{APP_NAME}_FEEDBACK`, `{APP_NAME}_ANALYSIS`
- **Service**: `{APP_NAME}-{environment}` in appropriate compute pool
- **Procedures**: `LOG_{APP_NAME}_EVENT`, `CLEANUP_{APP_NAME}_DATA`
- **View**: `{APP_NAME}_HEALTH_VIEW` for monitoring

## 🚀 Automated SPCS Deployment

### 1. Initial SPCS Setup (One-time)
```bash
# Run the interactive SPCS setup tool
cd framework/helpers/snowflake
./spcs-setup.sh

# Or run complete setup non-interactively
./spcs-setup.sh --complete
```

This creates:
- Compute pools (APP_POOL, STAGING_POOL, DEV_POOL)
- Image repository (APP_IMAGES)
- Database and schema (APPS_DB.AI_APPS)
- Roles and permissions (APP_DEVELOPER, APP_SERVICE)

### 2. App-Specific Setup (Per App)
```bash
# Navigate to your app directory
cd apps/your-app-name

# Customize the setup script with your app name
sed 's/{{APP_NAME}}/your-app-name/g' ../../framework/templates/deployment/setup-app.sh.template > setup/setup-app.sh
chmod +x setup/setup-app.sh

# Run app setup
./setup/setup-app.sh
```

This creates:
- App-specific stage: `YOUR_APP_NAME_STAGE`
- App service user: `YOUR_APP_NAME_USER`  
- App tables: `YOUR_APP_NAME_LOGS`, `YOUR_APP_NAME_FEEDBACK`, `YOUR_APP_NAME_ANALYSIS`
- Monitoring views and procedures

### 3. GitHub Actions Configuration

Required GitHub Secrets:
```
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PRIVATE_KEY=your_private_key_content
SNOWFLAKE_DATABASE=APPS_DB
SNOWFLAKE_SCHEMA=AI_APPS
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
APP_USER_PASSWORD=generated_app_user_password
```

### 4. Deployment Process

```bash
# Customize deployment templates
cd apps/your-app-name

# Create Dockerfile from template
sed 's/{{APP_NAME}}/your-app-name/g' ../../framework/templates/deployment/Dockerfile.template > Dockerfile

# Create GitHub workflow
mkdir -p .github/workflows
sed 's/{{APP_NAME}}/your-app-name/g' ../../framework/templates/deployment/deploy-app.yml.template > .github/workflows/deploy.yml

# Commit and push to trigger deployment
git add .
git commit -m "Deploy your-app-name"
git push origin main
```

### 5. Multi-Environment Support

Deploy to different environments:
```bash
# Deploy to staging
gh workflow run deploy.yml -f environment=staging

# Deploy to development  
gh workflow run deploy.yml -f environment=development

# Production deployment happens automatically on main branch push
```

### 6. Monitoring and Management

```sql
-- Check app health
SELECT * FROM YOUR_APP_NAME_HEALTH_VIEW;

-- View recent logs
SELECT * FROM YOUR_APP_NAME_LOGS 
WHERE CREATED_AT >= DATEADD('hour', -1, CURRENT_TIMESTAMP())
ORDER BY CREATED_AT DESC;

-- Get service status
SHOW SERVICES LIKE 'your-app-name%';

-- View service logs
SELECT SYSTEM$GET_SERVICE_LOGS('your-app-name-prod', 0, 'your-app-name-container');
```

### Step 3: Key Patterns to Follow

#### Authentication Pattern
- Use Snowflake private key authentication for production
- Support both password and key-based auth in utils
- Store credentials securely in environment variables

#### UI Components Pattern
- Reusable sidebar with consistent navigation
- File uploader with validation and progress tracking
- Feedback display with clear success/error states
- Loading states and progress indicators

#### Data Processing Pattern
- Stage-based file management in Snowflake
- AI analysis with proper error handling
- Results storage and retrieval
- Export capabilities (PDF, CSV, etc.)

## 🔧 Using the Framework

### For AI Agents:
1. Read `AGENTS.md` for specific implementation patterns
2. Use templates as starting points - don't reinvent
3. Follow the established folder structure
4. Implement proper error handling and logging
5. Include comprehensive docstrings and comments

### For Humans:
1. Clone this repository
2. Navigate to `apps/` folder
3. Create your new app folder
4. Copy templates and customize
5. Follow deployment instructions in `README.md`

## 🏗️ Architecture Principles

### 1. Modularity
- Each app is self-contained in `apps/` folder
- Shared utilities in `templates/` and `helpers/`
- Components are reusable across apps

### 2. Standardization
- Consistent file structure across all apps
- Standard naming conventions
- Unified error handling patterns

### 3. Deployment Ready
- Docker containerization for all apps
- SPCS (Snowflake Container Services) deployment
- CI/CD pipelines with GitHub Actions

### 4. AI-First Design
- Built for AI agent development
- Clear patterns and examples
- Comprehensive documentation

## 📋 Required Environment Variables

```bash
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your-account-id
SNOWFLAKE_USER=your-username
SNOWFLAKE_PASSWORD=your-password  # OR use private key
SNOWFLAKE_PRIVATE_KEY=your-private-key
SNOWFLAKE_ROLE=your-role
SNOWFLAKE_WAREHOUSE=your-warehouse
SNOWFLAKE_DATABASE=your-database
SNOWFLAKE_SCHEMA=your-schema

# Application Specific
APP_NAME=your-app-name
CORTEX_MODEL=mistral-large
```

## 🔐 Security Best Practices

1. **Never commit credentials** to version control
2. Use **environment variables** for all sensitive data
3. Use **private key authentication** for production
4. Implement proper **error handling** without exposing secrets
5. Use **least privilege** principle for database roles

## 🚀 Deployment Process

1. **Development**: Test locally with `streamlit run app.py`
2. **Containerization**: Build with `docker build -t app .`
3. **Registry**: Push to Snowflake image registry
4. **SPCS Deployment**: Create service in Snowflake Container Services
5. **Monitoring**: Check logs and endpoints

## 📚 Common Patterns

### File Processing
```python
# Upload to Snowflake stage
stage_uploader.upload_file(file, "STAGE_NAME")

# Process with AI
ai_analyzer.analyze_document(file_path, prompt)

# Store results
snowflake_utils.save_results(results, table_name)
```

### UI Components
```python
# Sidebar navigation
sidebar.create_navigation(pages)

# File upload with validation
file_uploader.create_uploader(accepted_types=[".pdf", ".txt"])

# Results display
feedback_display.show_results(results, success=True)
```

### Error Handling
```python
try:
    # Operation
    result = process_data()
    feedback_display.show_success("Operation completed!")
except Exception as e:
    logger.error(f"Operation failed: {e}")
    feedback_display.show_error("Something went wrong. Please try again.")
```

## 🎯 Success Criteria

Your app should:
- ✅ Follow the established folder structure
- ✅ Use reusable components from templates
- ✅ Handle errors gracefully with user feedback
- ✅ Include proper logging and monitoring
- ✅ Be containerized and deployment-ready
- ✅ Have comprehensive documentation
- ✅ Follow security best practices

## 🆘 Troubleshooting

### Snowflake Connection Issues
- Verify account identifier format
- Check private key permissions  
- Validate user exists and has proper roles
- Test connection with `snowsql`

### SPCS Deployment Issues
- **Service Failed to Start**: Check service logs with `SYSTEM$GET_SERVICE_LOGS()`
- **Image Pull Errors**: Verify image exists in repository and user has access
- **Permission Denied**: Ensure app user has required privileges on compute pool
- **Resource Limits**: Check compute pool capacity and instance availability
- **Network Issues**: Validate endpoint configuration and port settings

### App-Specific Troubleshooting
```bash
# Use the troubleshooting tool
cd framework/helpers/snowflake
./spcs-setup.sh  # Choose option 9 for diagnosis

# Manual diagnosis commands
snow sql -q "SHOW SERVICES LIKE 'your-app-name%';"
snow sql -q "SHOW COMPUTE POOLS;"
snow sql -q "SHOW STAGES LIKE 'YOUR_APP_NAME_STAGE';"
snow sql -q "SHOW USERS LIKE 'YOUR_APP_NAME_USER';"
```

### GitHub Actions Deployment Failures
- **Authentication Errors**: Verify GitHub secrets are correctly set
- **Build Failures**: Check Dockerfile syntax and requirements.txt
- **Push Failures**: Validate image repository access and credentials  
- **Service Creation Errors**: Review compute pool permissions and resource availability

Common issues and solutions are documented in each helper module. Check:
- `helpers/snowflake/troubleshooting.md`
- `helpers/docker/common-issues.md`
- `helpers/deployment/debugging.md`

## 📞 Support

For issues or questions:
1. Check the troubleshooting guides
2. Review example apps in `apps/` folder
3. Examine templates and helpers
4. Refer to `AGENTS.md` for implementation details