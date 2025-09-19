import streamlit as st
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """
    Main Streamlit application template.
    
    This template provides:
    - Basic page configuration
    - Navigation structure
    - Component integration points
    - Error handling patterns
    
    Customize this template for your specific AI application needs.
    """
    
    # Page configuration
    st.set_page_config(
        page_title="AI App Template",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_file = None
        st.session_state.analysis_results = None
    
    # Import components (after session state initialization)
    try:
        from components import sidebar, file_uploader, feedback_display
        from utils import snowflake_utils
    except ImportError as e:
        st.error(f"Failed to import components: {e}")
        st.info("Make sure all component files are present in the components/ and utils/ directories")
        return
    
    # Create sidebar navigation
    try:
        page = sidebar.create_navigation()
    except Exception as e:
        st.error(f"Navigation error: {e}")
        page = "Home"
    
    # Main content area
    if page == "Home":
        show_home_page()
    elif page == "Upload":
        show_upload_page()
    elif page == "Analysis":
        show_analysis_page()
    elif page == "Results":
        show_results_page()
    elif page == "Settings":
        show_settings_page()
    else:
        st.error(f"Unknown page: {page}")

def show_home_page():
    """Display the home page"""
    st.title("🤖 AI Application")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## Welcome to Your AI Application
        
        This application provides AI-powered functionality built on the 
        Snowflake AI App Framework. Key features include:
        
        - 📁 **File Upload & Processing**: Secure file handling with Snowflake stages
        - 🤖 **AI Analysis**: Powered by advanced language models
        - 📊 **Results Dashboard**: Interactive visualization of insights
        - 🔐 **Enterprise Security**: Built on Snowflake's secure platform
        
        ### Getting Started
        1. Navigate to **Upload** to add your files
        2. Go to **Analysis** to process with AI
        3. View **Results** for insights and exports
        4. Configure **Settings** as needed
        """)
    
    with col2:
        st.info("""
        **Quick Stats**
        
        📊 Files Processed: 0
        🤖 Analyses Complete: 0
        ✅ Success Rate: 100%
        
        **System Status**
        🟢 Application: Online
        🟢 Database: Connected
        🟢 AI Service: Ready
        """)

def show_upload_page():
    """Display the file upload page"""
    st.header("📁 File Upload")
    st.markdown("Upload files for AI analysis and processing.")
    
    try:
        from components.file_uploader import create_uploader
        from utils.stage_uploads import upload_to_stage
        
        # File uploader component
        uploaded_file = create_uploader()
        
        if uploaded_file is not None:
            st.session_state.current_file = uploaded_file
            
            # Display file information
            col1, col2 = st.columns(2)
            with col1:
                st.write("**File Details:**")
                st.write(f"- Name: {uploaded_file.name}")
                st.write(f"- Size: {uploaded_file.size:,} bytes")
                st.write(f"- Type: {uploaded_file.type}")
            
            with col2:
                if st.button("📤 Upload to Snowflake", type="primary"):
                    try:
                        with st.spinner("Uploading file..."):
                            result = upload_to_stage(uploaded_file)
                        st.success(f"✅ File uploaded successfully: {result}")
                    except Exception as e:
                        st.error(f"❌ Upload failed: {str(e)}")
    
    except ImportError as e:
        st.error(f"Component import error: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

def show_analysis_page():
    """Display the AI analysis page"""
    st.header("🤖 AI Analysis")
    st.markdown("Process uploaded files with AI-powered analysis.")
    
    if st.session_state.current_file is None:
        st.warning("⚠️ No file uploaded. Please go to the Upload page first.")
        return
    
    try:
        from utils.ai_analyzer import analyze_document
        
        st.write(f"**Analyzing:** {st.session_state.current_file.name}")
        
        # Analysis options
        analysis_type = st.selectbox(
            "Analysis Type:",
            ["Document Summary", "Content Classification", "Key Information Extraction", "Custom Analysis"]
        )
        
        if analysis_type == "Custom Analysis":
            custom_prompt = st.text_area(
                "Enter your analysis prompt:",
                placeholder="Analyze this document for..."
            )
        else:
            custom_prompt = None
        
        if st.button("🔍 Start Analysis", type="primary"):
            try:
                with st.spinner("Analyzing document..."):
                    results = analyze_document(
                        st.session_state.current_file,
                        analysis_type=analysis_type,
                        custom_prompt=custom_prompt
                    )
                
                st.session_state.analysis_results = results
                st.success("✅ Analysis complete!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
    
    except ImportError as e:
        st.error(f"AI analyzer not available: {e}")

def show_results_page():
    """Display analysis results"""
    st.header("📊 Analysis Results")
    
    if st.session_state.analysis_results is None:
        st.warning("⚠️ No analysis results available. Please complete an analysis first.")
        return
    
    try:
        from components.feedback_display import show_results
        
        # Display results
        show_results(st.session_state.analysis_results)
        
        # Export options
        st.markdown("---")
        st.subheader("📥 Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export PDF"):
                st.info("PDF export feature coming soon!")
        
        with col2:
            if st.button("📊 Export CSV"):
                st.info("CSV export feature coming soon!")
        
        with col3:
            if st.button("📋 Copy to Clipboard"):
                st.info("Clipboard feature coming soon!")
    
    except ImportError as e:
        st.error(f"Results display component error: {e}")

def show_settings_page():
    """Display application settings"""
    st.header("⚙️ Settings")
    
    # Connection settings
    st.subheader("🔗 Database Connection")
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Database", value="LICENSE_REVIEW", disabled=True)
        st.text_input("Schema", value="PUBLIC", disabled=True)
    
    with col2:
        st.text_input("Warehouse", value="QBCC_LOADING_WH", disabled=True)
        st.text_input("Role", value="APP_USERS", disabled=True)
    
    # Test connection
    if st.button("🔄 Test Connection"):
        try:
            from utils.snowflake_utils import get_session
            session = get_session()
            if session:
                st.success("✅ Database connection successful!")
            else:
                st.error("❌ Database connection failed!")
        except Exception as e:
            st.error(f"❌ Connection error: {e}")
    
    # AI settings
    st.subheader("🤖 AI Configuration")
    model_name = st.selectbox(
        "AI Model",
        ["mistral-large", "llama2-70b-chat", "reka-flash", "mixtral-8x7b"]
    )
    
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    max_tokens = st.number_input("Max Tokens", 100, 4000, 1000, 100)
    
    # Application info
    st.markdown("---")
    st.subheader("ℹ️ Application Info")
    st.info("""
    **Version:** 1.0.0
    **Framework:** Snowflake AI App Framework
    **Runtime:** Streamlit + Snowflake Container Services
    **Security:** Enterprise-grade with private key authentication
    """)

if __name__ == "__main__":
    main()