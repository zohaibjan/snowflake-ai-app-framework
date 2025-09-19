"""
Sidebar Navigation Component

Provides consistent navigation across all AI applications.
"""

import streamlit as st

def create_navigation(app_name="AI Application", pages=None):
    """
    Create sidebar navigation with consistent branding and functionality.
    
    Args:
        app_name (str): Name of the application
        pages (list): List of page names for navigation
    
    Returns:
        str: Selected page name
    """
    
    if pages is None:
        pages = ["Home", "Upload", "Analysis", "Results", "Settings"]
    
    with st.sidebar:
        # App branding
        st.title(f"🤖 {app_name}")
        st.markdown("---")
        
        # Navigation menu
        st.subheader("📋 Navigation")
        selected_page = st.selectbox(
            "Go to:",
            pages,
            key="navigation_selectbox"
        )
        
        st.markdown("---")
        
        # Quick stats (if available in session state)
        if hasattr(st.session_state, 'stats'):
            st.subheader("📊 Quick Stats")
            stats = st.session_state.stats
            st.metric("Files Processed", stats.get('files_processed', 0))
            st.metric("Analyses Complete", stats.get('analyses_complete', 0))
            st.metric("Success Rate", f"{stats.get('success_rate', 100)}%")
            st.markdown("---")
        
        # System status
        st.subheader("🔋 System Status")
        
        # Check database connection (if available)
        try:
            from utils.snowflake_utils import get_session
            session = get_session()
            if session:
                st.success("🟢 Database Connected")
            else:
                st.error("🔴 Database Disconnected")
        except:
            st.warning("🟡 Database Status Unknown")
        
        # AI service status (placeholder)
        st.success("🟢 AI Service Ready")
        
        st.markdown("---")
        
        # Framework info
        st.info("""
        **Built with**
        
        🏗️ AI App Framework
        
        ❄️ Snowflake SPCS
        
        🎈 Streamlit
        """)
        
        # Help section
        with st.expander("❓ Help & Support"):
            st.markdown("""
            **Quick Help:**
            1. Upload files in the Upload section
            2. Analyze with AI in Analysis
            3. View results in Results section
            4. Configure settings as needed
            
            **Troubleshooting:**
            - Check system status above
            - Verify file formats are supported
            - Contact admin if issues persist
            """)
    
    return selected_page

def create_simple_navigation(pages):
    """
    Create simple navigation without branding (for minimal UIs).
    
    Args:
        pages (list): List of page names
        
    Returns:
        str: Selected page name
    """
    with st.sidebar:
        st.subheader("Navigation")
        return st.selectbox("Page:", pages)

def add_sidebar_info(title, content, info_type="info"):
    """
    Add information box to sidebar.
    
    Args:
        title (str): Title of the info box
        content (str): Content to display
        info_type (str): Type of info box (info, success, warning, error)
    """
    with st.sidebar:
        if info_type == "info":
            st.info(f"**{title}**\n\n{content}")
        elif info_type == "success":
            st.success(f"**{title}**\n\n{content}")
        elif info_type == "warning":
            st.warning(f"**{title}**\n\n{content}")
        elif info_type == "error":
            st.error(f"**{title}**\n\n{content}")

def add_sidebar_metrics(metrics_dict):
    """
    Add metrics to sidebar.
    
    Args:
        metrics_dict (dict): Dictionary of metric name: value pairs
    """
    with st.sidebar:
        st.subheader("📊 Metrics")
        
        for metric_name, metric_value in metrics_dict.items():
            st.metric(metric_name, metric_value)

def create_collapsible_nav(sections):
    """
    Create collapsible navigation sections.
    
    Args:
        sections (dict): Dictionary of section_name: [pages] pairs
        
    Returns:
        tuple: (selected_section, selected_page)
    """
    with st.sidebar:
        selected_section = None
        selected_page = None
        
        for section_name, pages in sections.items():
            with st.expander(f"📁 {section_name}"):
                selected_page = st.radio(
                    f"Pages in {section_name}:",
                    pages,
                    key=f"nav_{section_name}"
                )
                if selected_page:
                    selected_section = section_name
                    break
        
        return selected_section, selected_page