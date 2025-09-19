# {{APP_NAME}} - Manual App Template

This is a complete application template that you can copy and customize manually without needing an AI agent.

## 🚀 Quick Start

### 1. Copy This Template
```bash
# Copy the entire app-template directory to your main apps folder
cp -r framework/apps/app-template/ ../apps/your-app-name/
cd ../apps/your-app-name/
```

### 2. Customize Your App
Replace all instances of `{{APP_NAME}}` with your actual app name:

```bash
# Find and replace app name placeholders
find . -name "*.py" -o -name "*.md" -o -name "*.yml" -o -name "Dockerfile" | xargs sed -i 's/{{APP_NAME}}/YOUR_APP_NAME/g'
find . -name "*.py" -o -name "*.md" -o -name "*.yml" -o -name "Dockerfile" | xargs sed -i 's/{{app_name}}/your_app_name/g'
```

### 3. Set Up Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Snowflake
Create a `.env` file in your app directory:

```bash
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your-account.region.cloud
SNOWFLAKE_USER=your-username
SNOWFLAKE_PASSWORD=your-password  # or use private key
SNOWFLAKE_DATABASE=YOUR_APP_DB
SNOWFLAKE_SCHEMA=AI_APPS
SNOWFLAKE_WAREHOUSE=COMPUTE_WH

# Private Key Authentication (recommended for production)
# SNOWFLAKE_PRIVATE_KEY_PATH=/path/to/private_key.p8

# Application Specific
APP_NAME=your-app-name
CORTEX_MODEL=mistral-large
```

### 5. Initialize Snowflake Objects
Run the setup script to create necessary Snowflake objects:

```bash
# This will create:
# - App-specific user and role
# - Database and schema
# - File upload stage
# - Analysis results table
./setup-app.sh
```

### 6. Test Your App
```bash
# Run locally
streamlit run app.py

# Build and test container
docker build -t your-app-name .
docker run -p 8501:8501 your-app-name
```

## 📁 Template Structure

```
app-template/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── README.md                # This file
├── .env.example             # Environment variables template
├── setup-app.sh             # Snowflake setup script
├── components/              # UI components
│   ├── __init__.py
│   ├── sidebar.py           # Navigation sidebar
│   ├── file_uploader.py     # File upload component
│   └── feedback_display.py  # Results display component
└── utils/                   # Utility functions
    ├── __init__.py
    ├── snowflake_utils.py   # Snowflake connection
    ├── ai_analyzer.py       # Cortex AI integration
    ├── pdf_processor.py     # Document processing
    └── stage_uploads.py     # File upload to Snowflake
```

## ✨ Features Included

### 🤖 AI-Powered Analysis
- **Snowflake Cortex AI Integration**: Multiple model support (mistral-large, llama2-70b-chat, reka-flash, mixtral-8x7b)
- **Document Analysis**: Extract insights from PDFs, DOCX, TXT files
- **Batch Processing**: Analyze multiple documents at once
- **Configurable Prompts**: Customize analysis types (general, compliance, summary, quality)

### 📁 File Management
- **Multi-format Support**: PDF, DOCX, DOC, TXT files
- **Snowflake Stage Upload**: Direct upload to Snowflake stages
- **File Processing**: Text extraction and preprocessing
- **Upload Validation**: File type and size validation

### 📊 Data & Analytics
- **Results Storage**: Save analysis results in Snowflake tables
- **Data Visualization**: Charts and metrics for analysis results
- **Export Capabilities**: Download results as CSV, JSON, or Markdown reports
- **Session Management**: Maintain state across user interactions

### 🎨 Professional UI
- **Responsive Design**: Works on desktop and mobile
- **Navigation Sidebar**: Easy page switching
- **Progress Tracking**: Visual feedback for long operations
- **Error Handling**: User-friendly error messages
- **Custom Styling**: Professional appearance with custom CSS

### 🔧 Configuration & Settings
- **Environment Variables**: Secure configuration management
- **Model Selection**: Choose between different Cortex AI models
- **Connection Testing**: Verify Snowflake connectivity
- **Settings Page**: Manage app configuration

## 🎯 Customization Guide

### Adding New Analysis Types
Edit `utils/ai_analyzer.py` to add custom prompts:

```python
prompts = {
    'your_custom_type': """
    Your custom analysis prompt here...
    """,
    # ... existing prompts
}
```

### Adding New File Types
Extend `utils/pdf_processor.py` to support additional formats:

```python
def extract_text_from_file(file):
    if file.type == "application/your-new-type":
        return extract_your_format(file)
    # ... existing extractors
```

### Custom UI Components
Add new components in the `components/` directory:

```python
# components/your_component.py
import streamlit as st

def create_your_component():
    # Your component logic here
    return component_data
```

### Database Schema Customization
Modify the table structure in `setup-app.sh`:

```sql
CREATE TABLE IF NOT EXISTS YOUR_APP_ANALYSES (
    ANALYSIS_ID STRING PRIMARY KEY,
    -- Add your custom columns here
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

## 🔧 Advanced Configuration

### Model Selection
Configure available Cortex AI models in `utils/ai_analyzer.py`:

```python
CORTEX_MODELS = {
    'mistral-large': {
        'description': 'Large multilingual model',
        'max_tokens': 8000,
        'recommended_use': 'Complex document analysis'
    },
    # Add custom model configurations
}
```

### Performance Optimization
- **Caching**: Use `@st.cache_data` for expensive operations
- **Session State**: Minimize data stored in session state
- **Batch Processing**: Process multiple files efficiently
- **Connection Pooling**: Reuse Snowflake connections

### Security Best Practices
- **Environment Variables**: Never hardcode credentials
- **Private Key Auth**: Use private key authentication for production
- **Input Validation**: Validate all user inputs
- **Error Handling**: Don't expose sensitive information in errors

## 🚀 Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Docker Container
```bash
docker build -t your-app-name .
docker run -p 8501:8501 --env-file .env your-app-name
```

### Snowflake Container Services (SPCS)
Use the framework's deployment templates in `framework/templates/deployment/` to deploy to SPCS with automated CI/CD.

## 📝 Next Steps

1. **Customize the UI**: Modify colors, layout, and styling in `app.py`
2. **Add Features**: Implement additional document processing capabilities
3. **Integrate APIs**: Connect to external services or databases
4. **Set Up Monitoring**: Add logging and error tracking
5. **Deploy to Production**: Use SPCS deployment templates

## 🆘 Getting Help

- **Framework Documentation**: See `framework/INSTRUCTIONS.md`
- **Troubleshooting**: Use `framework/helpers/snowflake/troubleshoot.py`
- **Examples**: Check other apps in the `apps/` directory
- **Snowflake Docs**: [Cortex AI Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex)

## 📄 License

This template is part of the AI App Development Framework. Customize and use according to your needs.

---

**Happy Building!** 🚀

This template provides everything you need to create a professional AI-powered application with Snowflake Cortex AI integration.