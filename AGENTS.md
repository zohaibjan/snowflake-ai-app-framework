# AGENTS.md - AI Agent Implementation Guide

## 🤖 For AI Agents Building Apps

This file provides specific instructions for AI agents (like GitHub Copilot, Claude, ChatGPT) to build applications using this framework.

## 🎯 Core Implementation Patterns

### App Creation Workflow
1. **Read Context**: Always read `INSTRUCTIONS.md` first
2. **Understand Requirements**: Parse user requirements carefully
3. **Create Structure**: Set up app folder in `apps/[app-name]/`
4. **Copy Templates**: Use templates as starting points
5. **Customize**: Adapt to specific requirements
6. **Test**: Ensure functionality works
7. **Document**: Create clear documentation

### Required File Structure for Every App
```python
# Every app MUST have these files:
apps/[app-name]/
├── app.py                 # Main Streamlit app
├── requirements.txt       # Dependencies
├── Dockerfile            # Container config
├── README.md             # App-specific docs
├── .env.example          # Environment template
├── components/           # UI components
│   ├── __init__.py
│   ├── sidebar.py
│   ├── file_uploader.py
│   └── feedback_display.py
└── utils/               # Utility functions
    ├── __init__.py
    ├── snowflake_utils.py
    ├── ai_analyzer.py
    └── stage_uploads.py
```

## 📋 Implementation Checklist

### ✅ Phase 1: Setup
- [ ] Create app folder in `apps/`
- [ ] Copy base template files
- [ ] Update app name throughout files
- [ ] Set up proper imports

### ✅ Phase 2: Core Functionality
- [ ] Implement main app logic in `app.py`
- [ ] Set up Snowflake connection in utils
- [ ] Create AI analysis functions
- [ ] Implement file upload/processing

### ✅ Phase 3: UI Components
- [ ] Customize sidebar navigation
- [ ] Implement file uploader with validation
- [ ] Create feedback/results display
- [ ] Add loading states and progress

### ✅ Phase 4: Integration
- [ ] Connect to Snowflake stages
- [ ] Integrate AI models (OpenAI, etc.)
- [ ] Implement data persistence
- [ ] Add export functionality

### ✅ Phase 5: Deployment
- [ ] Test containerization
- [ ] Update GitHub workflow
- [ ] Configure SPCS deployment
- [ ] Validate end-to-end functionality

## 🧩 Code Templates and Patterns

### Main App Structure (app.py)
```python
import streamlit as st
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from components import sidebar, file_uploader, feedback_display
from utils import snowflake_utils, ai_analyzer, stage_uploads

# Page config
st.set_page_config(
    page_title="Your App Name",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Sidebar navigation
    page = sidebar.create_navigation()
    
    # Main content based on page
    if page == "Upload":
        handle_upload_page()
    elif page == "Analysis":
        handle_analysis_page()
    elif page == "Results":
        handle_results_page()

def handle_upload_page():
    st.header("📁 File Upload")
    
    # File uploader component
    uploaded_file = file_uploader.create_uploader(
        accepted_types=[".pdf", ".docx", ".txt"]
    )
    
    if uploaded_file:
        try:
            # Process upload
            result = stage_uploads.upload_to_stage(uploaded_file, "YOUR_STAGE")
            feedback_display.show_success(f"File uploaded: {result}")
        except Exception as e:
            feedback_display.show_error(f"Upload failed: {str(e)}")

if __name__ == "__main__":
    main()
```

### Snowflake Utils Template
```python
import os
import streamlit as st
from snowflake.snowpark import Session
from pathlib import Path

@st.cache_resource
def get_snowflake_session():
    """Get cached Snowflake session"""
    try:
        # Try private key first
        if os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH"):
            return create_session_with_key()
        # Fallback to password
        elif os.getenv("SNOWFLAKE_PASSWORD"):
            return create_session_with_password()
        else:
            raise ValueError("No valid authentication method found")
    except Exception as e:
        st.error(f"Snowflake connection failed: {e}")
        return None

def create_session_with_key():
    """Create session with private key authentication"""
    # Implementation from templates/utils/snowflake_utils.py
    pass

def create_session_with_password():
    """Create session with password authentication"""
    # Implementation from templates/utils/snowflake_utils.py
    pass
```

### Component Template (components/sidebar.py)
```python
import streamlit as st

def create_navigation(pages=None):
    """Create sidebar navigation"""
    if pages is None:
        pages = ["Upload", "Analysis", "Results", "Settings"]
    
    with st.sidebar:
        st.title("🤖 Your App")
        st.markdown("---")
        
        # Navigation
        page = st.selectbox("Navigate to:", pages)
        
        st.markdown("---")
        
        # App info
        st.info("Built with AI App Framework")
        
        return page
```

## 🎨 UI Design Patterns

### Consistent Styling
```python
# Use these CSS classes consistently
st.markdown("""
<style>
.success-box { background-color: #d4edda; padding: 1rem; border-radius: 0.5rem; }
.error-box { background-color: #f8d7da; padding: 1rem; border-radius: 0.5rem; }
.info-box { background-color: #d1ecf1; padding: 1rem; border-radius: 0.5rem; }
</style>
""", unsafe_allow_html=True)
```

### Loading States
```python
def show_loading_state(message="Processing..."):
    """Show consistent loading state"""
    with st.spinner(message):
        progress_bar = st.progress(0)
        status_text = st.empty()
        return progress_bar, status_text
```

### Error Handling
```python
def handle_error(error, context=""):
    """Consistent error handling"""
    error_msg = f"Error in {context}: {str(error)}"
    st.error(error_msg)
    # Log to Snowflake or external service
    log_error(error_msg)
```

## 🔧 Required Dependencies

### requirements.txt Template
```txt
streamlit>=1.28.0
snowflake-snowpark-python>=1.9.0
pandas>=2.0.0
openai>=1.0.0
python-dotenv>=1.0.0
Pillow>=10.0.0
PyPDF2>=3.0.0
python-docx>=0.8.11
plotly>=5.17.0
```

### Dockerfile Template
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Create necessary directories
RUN mkdir -p /tmp /app/templates

EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

## 🚀 Deployment Configuration

### GitHub Workflow Template
```yaml
name: Deploy [APP_NAME] to SPCS

on:
  push:
    branches: [ main ]
    paths: [ 'apps/[app-name]/**' ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    # Copy from helpers/github/deploy-spcs-template.yml
```

## 🎯 AI Agent Decision Tree

### When User Says: "Build an AI app that..."

1. **Parse Requirements**:
   - What type of AI functionality? (analysis, generation, classification)
   - What data sources? (files, databases, APIs)
   - What output format? (dashboard, report, export)

2. **Choose Templates**:
   - Document analysis → Use forms_review pattern
   - Data visualization → Use dashboard pattern
   - File processing → Use upload/stage pattern

3. **Implementation Order**:
   - Core functionality first
   - UI components second
   - Integration and deployment last

### Common App Types and Patterns

#### Document Analysis App
- Use: file_uploader + ai_analyzer + stage_uploads
- Pattern: Upload → Process → Analyze → Display Results
- Templates: document_analyzer_template.py

#### Data Dashboard App
- Use: data_connector + visualization + sidebar
- Pattern: Connect → Query → Visualize → Export
- Templates: dashboard_template.py

#### AI Chat/Assistant App
- Use: chat_interface + ai_connector + session_state
- Pattern: Input → Process → Respond → History
- Templates: chat_template.py

## ⚠️ Important Constraints

### Must Follow These Rules:
1. **Always use the framework structure** - don't create custom folder layouts
2. **Copy from templates first** - don't write from scratch
3. **Use established patterns** - follow existing component interfaces
4. **Include proper error handling** - use feedback_display for all user messages
5. **Test with dummy data** - provide sample data for testing
6. **Document thoroughly** - include docstrings and README.md
7. **Follow security practices** - never hardcode credentials

### Never Do These:
- ❌ Create apps outside the `apps/` folder
- ❌ Hardcode credentials or API keys
- ❌ Skip error handling or user feedback
- ❌ Use inconsistent naming conventions
- ❌ Create custom authentication patterns
- ❌ Ignore the established component interfaces

## 🔍 Quality Checklist

Before marking an app complete, verify:

### Functionality
- [ ] App runs without errors
- [ ] All main features work as expected
- [ ] Error handling covers edge cases
- [ ] Loading states provide user feedback

### Code Quality
- [ ] Follows established patterns
- [ ] Proper imports and structure
- [ ] Comprehensive docstrings
- [ ] Clean, readable code

### User Experience
- [ ] Intuitive navigation
- [ ] Clear feedback messages
- [ ] Consistent styling
- [ ] Responsive design

### Deployment
- [ ] Containerizes successfully
- [ ] Environment variables documented
- [ ] GitHub workflow configured
- [ ] SPCS deployment ready

## 🎓 Learning from Examples

Study these example apps:
- `apps/forms_review/` - Document analysis with AI
- `apps/data_dashboard/` - Data visualization
- `apps/chat_assistant/` - Conversational AI

Each example demonstrates:
- Proper folder structure
- Component usage
- Error handling
- Deployment configuration

## 🚀 Quick Start Commands

```bash
# Create new app (replace [app-name] with actual name)
cp -r templates/ apps/[app-name]/
cd apps/[app-name]/
# Customize files as needed

# Test locally
streamlit run app.py

# Build container
docker build -t [app-name] .

# Deploy to SPCS
# Follow GitHub Actions workflow
```

Remember: The goal is rapid, consistent, high-quality app development using established patterns!