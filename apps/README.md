# 📱 Apps Directory

This directory contains example applications and templates built using the AI App Development Framework.

## 🎯 Available Templates

### [`app-template/`](./app-template/) - Complete Manual App Template
A fully functional template that users can copy and customize without needing an AI agent.

**Features:**
- ✅ Complete Streamlit application
- ✅ Snowflake Cortex AI integration
- ✅ File upload and processing
- ✅ Professional UI with navigation
- ✅ Data persistence in Snowflake
- ✅ Docker containerization
- ✅ Automated setup script

**Quick Start:**
```bash
# Copy the template
cp -r framework/apps/app-template/ ../apps/my-new-app/
cd ../apps/my-new-app/

# Customize app name
find . -name "*.py" -o -name "*.md" -o -name "Dockerfile" | xargs sed -i 's/{{APP_NAME}}/MY_NEW_APP/g'
find . -name "*.py" -o -name "*.md" -o -name "Dockerfile" | xargs sed -i 's/{{app_name}}/my_new_app/g'

# Setup and run
pip install -r requirements.txt
./setup-app.sh
streamlit run app.py
```

## 🚀 How to Use Templates

### Method 1: Manual Copy and Customize
```bash
# 1. Copy template to your apps directory
cp -r framework/apps/app-template/ ../apps/your-app-name/

# 2. Navigate to your app
cd ../apps/your-app-name/

# 3. Replace placeholders with your app name
sed -i 's/{{APP_NAME}}/YOUR_APP_NAME/g' *.py *.md *.sh Dockerfile
sed -i 's/{{app_name}}/your_app_name/g' *.py *.md *.sh Dockerfile

# 4. Follow the README.md in your app directory
```

### Method 2: Use AI Agent (if available)
If you have an AI agent like GitHub Copilot, you can ask it to create a new app based on these templates:

```
"Create a new app called 'document_classifier' based on the app-template, customized for document classification"
```

## 📁 Recommended App Structure

When creating apps, use this structure in your main `apps/` directory (outside the framework):

```
apps/
├── your-app-name/
│   ├── app.py                    # Main Streamlit app
│   ├── requirements.txt          # Dependencies  
│   ├── Dockerfile               # Container config
│   ├── README.md                # App documentation
│   ├── .env.example             # Environment template
│   ├── setup-app.sh             # Snowflake setup
│   ├── components/              # UI components
│   └── utils/                   # Utility functions
├── another-app/
│   └── ...
└── production-app/
    └── ...
```

## 🎨 Template Customization

### Common Customizations:

1. **App Name and Branding**:
   - Replace `{{APP_NAME}}` and `{{app_name}}` throughout
   - Update page titles and headers
   - Customize colors and styling

2. **AI Analysis Types**:
   - Modify prompts in `utils/ai_analyzer.py`
   - Add custom analysis workflows
   - Configure different Cortex AI models

3. **File Processing**:
   - Extend `utils/pdf_processor.py` for new file types
   - Add custom validation rules
   - Implement preprocessing pipelines

4. **Database Schema**:
   - Modify table structure in `setup-app.sh`
   - Add custom fields for your use case
   - Implement data relationships

5. **UI Components**:
   - Customize `components/` files
   - Add new pages and navigation
   - Implement custom visualizations

## 🔧 Development Workflow

### For New Apps:
```bash
# 1. Copy template
cp -r framework/apps/app-template/ ../apps/my-app/

# 2. Customize
cd ../apps/my-app/
# Edit files to match your requirements

# 3. Setup environment
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Snowflake details

# 4. Initialize Snowflake
./setup-app.sh

# 5. Test locally
streamlit run app.py

# 6. Deploy (optional)
# Use framework deployment templates
```

## 📝 Best Practices

### Development:
- ✅ Use virtual environments for each app
- ✅ Follow the established component structure
- ✅ Include comprehensive error handling
- ✅ Add logging and monitoring
- ✅ Write clear documentation

### Production:
- ✅ Use private key authentication
- ✅ Implement proper security measures
- ✅ Set up automated deployments
- ✅ Monitor performance and costs
- ✅ Regular backup and maintenance

### Code Quality:
- ✅ Follow consistent naming conventions
- ✅ Add docstrings and comments
- ✅ Implement unit tests
- ✅ Use type hints
- ✅ Regular code reviews

## 🚀 Example Use Cases

### Document Analysis Apps:
- Contract review systems
- Compliance checking tools
- Legal document analysis
- Medical record processing

### Data Processing Apps:
- Report generation tools
- Data transformation pipelines
- Analytics dashboards
- Automated insights

### AI-Powered Tools:
- Content generation
- Text classification
- Sentiment analysis
- Question answering systems

## 📚 Additional Resources

- **Framework Documentation**: [`../INSTRUCTIONS.md`](../INSTRUCTIONS.md)
- **Agent Guidelines**: [`../AGENTS.md`](../AGENTS.md)
- **Templates**: [`../templates/`](../templates/)
- **Deployment Helpers**: [`../helpers/`](../helpers/)
- **Troubleshooting**: [`../helpers/snowflake/README.md`](../helpers/snowflake/README.md)

## 🆘 Getting Help

### Common Issues:
1. **Template not working**: Check placeholder replacement
2. **Snowflake errors**: Run `./setup-app.sh test`
3. **Import errors**: Verify all dependencies installed
4. **Deployment issues**: Use framework troubleshooting tools

### Support Resources:
- Framework troubleshooting tools
- Snowflake documentation
- Streamlit community
- AI model documentation

---

**Happy Building!** 🚀

These templates provide a solid foundation for creating professional AI-powered applications with minimal setup time.