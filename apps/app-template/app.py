"""
{{APP_NAME}} - AI-Powered Streamlit Application

This is a template Streamlit application that can be customized for various AI-powered use cases.
Replace {{APP_NAME}} with your actual app name throughout the codebase.

Features:
- File upload and processing
- Snowflake Cortex AI integration
- Document analysis and feedback
- Data persistence in Snowflake
- Professional UI with sidebar navigation
"""

import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime
import traceback

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import components and utilities
try:
    from components import sidebar, file_uploader, feedback_display
    from utils import snowflake_utils, ai_analyzer, stage_uploads
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all required modules are in the components/ and utils/ directories")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="{{APP_NAME}}",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "AI-powered document analysis application built with Streamlit and Snowflake Cortex AI"
    }
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .metrics-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
    }
    .stButton > button {
        width: 100%;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
    
    if 'snowflake_connected' not in st.session_state:
        st.session_state.snowflake_connected = False
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Upload"

def check_snowflake_connection():
    """Check and display Snowflake connection status"""
    try:
        session = snowflake_utils.get_snowflake_session()
        if session:
            st.session_state.snowflake_connected = True
            return True
        else:
            st.session_state.snowflake_connected = False
            return False
    except Exception as e:
        st.session_state.snowflake_connected = False
        st.error(f"Snowflake connection failed: {str(e)}")
        return False

def main():
    """Main application function"""
    
    # Initialize session state
    initialize_session_state()
    
    # Check Snowflake connection
    snowflake_available = check_snowflake_connection()
    
    # Create sidebar navigation
    page = sidebar.create_navigation([
        "📁 Upload", 
        "🔍 Analysis", 
        "📊 Results", 
        "⚙️ Settings"
    ])
    
    # Store current page
    st.session_state.current_page = page.replace("📁 ", "").replace("🔍 ", "").replace("📊 ", "").replace("⚙️ ", "")
    
    # Display connection status in sidebar
    with st.sidebar:
        st.markdown("---")
        if snowflake_available:
            st.success("🔗 Snowflake Connected")
        else:
            st.error("❌ Snowflake Disconnected")
        
        # Model selection
        st.markdown("### AI Model")
        available_models = ai_analyzer.get_available_models()
        if available_models:
            selected_model = st.selectbox(
                "Cortex AI Model",
                options=list(available_models.keys()),
                index=0,
                help="Choose the AI model for document analysis"
            )
            
            # Display model info
            model_info = ai_analyzer.get_cortex_model_info(selected_model)
            st.info(f"**{model_info['description']}**\n\n{model_info['recommended_use']}")
        else:
            st.warning("No Cortex AI models available")
            selected_model = "mistral-large"
    
    # Main content area
    if st.session_state.current_page == "Upload":
        handle_upload_page(snowflake_available, selected_model)
    elif st.session_state.current_page == "Analysis":
        handle_analysis_page(snowflake_available, selected_model)
    elif st.session_state.current_page == "Results":
        handle_results_page()
    elif st.session_state.current_page == "Settings":
        handle_settings_page()
    else:
        handle_upload_page(snowflake_available, selected_model)

def handle_upload_page(snowflake_available, selected_model):
    """Handle file upload page"""
    st.markdown('<div class="main-header">📁 File Upload</div>', unsafe_allow_html=True)
    
    if not snowflake_available:
        st.error("⚠️ Snowflake connection required for file upload. Please check your configuration.")
        st.info("Configure your Snowflake connection in the `.env` file or environment variables.")
        return
    
    st.markdown("Upload your documents for AI-powered analysis using Snowflake Cortex AI.")
    
    # File upload section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = file_uploader.create_uploader(
            accepted_types=[".pdf", ".txt", ".docx", ".doc"],
            max_files=5,
            help_text="Supported formats: PDF, TXT, DOCX, DOC (Max 5 files)"
        )
        
        if uploaded_files:
            st.success(f"📄 {len(uploaded_files)} file(s) uploaded successfully!")
            
            # Display uploaded files
            for i, file in enumerate(uploaded_files):
                with st.expander(f"📄 {file.name} ({file.size:,} bytes)"):
                    col_preview, col_actions = st.columns([3, 1])
                    
                    with col_preview:
                        # Show file preview
                        if file.type == "text/plain":
                            content = str(file.read(), "utf-8")
                            st.text_area("Content Preview", content[:500] + "...", height=100)
                        else:
                            st.info("Binary file - processing required for preview")
                    
                    with col_actions:
                        if st.button(f"Analyze Now", key=f"analyze_{i}"):
                            analyze_single_file(file, selected_model)
            
            # Batch processing
            if len(uploaded_files) > 1:
                st.markdown("### Batch Processing")
                col_batch1, col_batch2 = st.columns(2)
                
                with col_batch1:
                    if st.button("🔄 Analyze All Files", type="primary"):
                        process_batch_files(uploaded_files, selected_model)
                
                with col_batch2:
                    if st.button("💾 Upload to Snowflake Stage"):
                        upload_to_stage(uploaded_files)
    
    with col2:
        # Upload instructions
        st.markdown("### 📋 Instructions")
        st.markdown("""
        1. **Choose Files**: Select documents to analyze
        2. **Upload**: Files are processed automatically
        3. **Analyze**: AI analysis using Cortex AI
        4. **Review**: Check results in the Analysis tab
        5. **Export**: Download analysis results
        """)
        
        # Upload statistics
        st.markdown("### 📊 Upload Stats")
        if st.session_state.uploaded_files:
            total_files = len(st.session_state.uploaded_files)
            total_size = sum(f.get('size', 0) for f in st.session_state.uploaded_files)
            
            st.metric("Total Files", total_files)
            st.metric("Total Size", f"{total_size:,} bytes")
        else:
            st.info("No files uploaded yet")

def analyze_single_file(file, model):
    """Analyze a single uploaded file"""
    try:
        with st.spinner(f"Analyzing {file.name} with {model}..."):
            # Process file content
            from utils.pdf_processor import extract_text_from_file
            
            text_content = extract_text_from_file(file)
            
            if not text_content or len(text_content.strip()) < 10:
                st.error("⚠️ Could not extract meaningful text from the file")
                return
            
            # Perform AI analysis
            analysis_result = ai_analyzer.analyze_document_content(
                text_content=text_content,
                analysis_type="general",
                model=model
            )
            
            if analysis_result['success']:
                # Store results
                file_key = f"{file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.session_state.analysis_results[file_key] = {
                    'file_name': file.name,
                    'analysis': analysis_result,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Display results
                feedback_display.show_analysis_results(analysis_result)
                
                # Save to Snowflake
                try:
                    save_result_to_snowflake(file_key, analysis_result)
                    st.success("✅ Analysis saved to Snowflake")
                except Exception as e:
                    st.warning(f"⚠️ Could not save to Snowflake: {str(e)}")
                
            else:
                st.error(f"❌ Analysis failed: {analysis_result.get('error', 'Unknown error')}")
                
    except Exception as e:
        st.error(f"❌ Error analyzing file: {str(e)}")
        if st.checkbox("Show technical details"):
            st.code(traceback.format_exc())

def process_batch_files(files, model):
    """Process multiple files in batch"""
    try:
        st.markdown("### 🔄 Batch Processing Results")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = []
        
        for i, file in enumerate(files):
            status_text.text(f"Processing {file.name} ({i+1}/{len(files)})")
            progress_bar.progress((i + 1) / len(files))
            
            try:
                # Extract text
                from utils.pdf_processor import extract_text_from_file
                text_content = extract_text_from_file(file)
                
                if text_content and len(text_content.strip()) >= 10:
                    # Analyze with AI
                    analysis_result = ai_analyzer.analyze_document_content(
                        text_content=text_content,
                        analysis_type="general",
                        model=model
                    )
                    
                    results.append({
                        'file_name': file.name,
                        'success': analysis_result['success'],
                        'analysis': analysis_result if analysis_result['success'] else None,
                        'error': analysis_result.get('error') if not analysis_result['success'] else None
                    })
                else:
                    results.append({
                        'file_name': file.name,
                        'success': False,
                        'analysis': None,
                        'error': 'Could not extract text content'
                    })
                    
            except Exception as e:
                results.append({
                    'file_name': file.name,
                    'success': False,
                    'analysis': None,
                    'error': str(e)
                })
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Display batch results
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Files", len(results))
        with col2:
            st.metric("Successful", successful, delta=None if successful == 0 else f"+{successful}")
        with col3:
            st.metric("Failed", failed, delta=None if failed == 0 else f"-{failed}")
        
        # Store successful results
        for result in results:
            if result['success']:
                file_key = f"{result['file_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.session_state.analysis_results[file_key] = {
                    'file_name': result['file_name'],
                    'analysis': result['analysis'],
                    'timestamp': datetime.now().isoformat()
                }
        
        if successful > 0:
            st.success(f"✅ Successfully analyzed {successful} file(s)")
        if failed > 0:
            st.error(f"❌ Failed to analyze {failed} file(s)")
            
            # Show failed files
            with st.expander("View Failed Files"):
                for result in results:
                    if not result['success']:
                        st.error(f"**{result['file_name']}**: {result['error']}")
        
    except Exception as e:
        st.error(f"❌ Batch processing failed: {str(e)}")

def upload_to_stage(files):
    """Upload files to Snowflake stage"""
    try:
        with st.spinner("Uploading files to Snowflake stage..."):
            results = []
            
            for file in files:
                try:
                    # Upload to stage using stage_uploads utility
                    result = stage_uploads.upload_to_stage(file, "{{APP_NAME}}_STAGE")
                    results.append({
                        'file_name': file.name,
                        'success': True,
                        'stage_path': result.get('stage_path', 'Unknown')
                    })
                except Exception as e:
                    results.append({
                        'file_name': file.name,
                        'success': False,
                        'error': str(e)
                    })
            
            # Display results
            successful_uploads = sum(1 for r in results if r['success'])
            
            if successful_uploads > 0:
                st.success(f"✅ Successfully uploaded {successful_uploads} file(s) to Snowflake stage")
                
                with st.expander("View Upload Details"):
                    for result in results:
                        if result['success']:
                            st.info(f"**{result['file_name']}** → {result['stage_path']}")
                        else:
                            st.error(f"**{result['file_name']}**: {result['error']}")
            else:
                st.error("❌ No files were uploaded successfully")
            
    except Exception as e:
        st.error(f"❌ Upload to stage failed: {str(e)}")

def handle_analysis_page(snowflake_available, selected_model):
    """Handle analysis page"""
    st.markdown('<div class="main-header">🔍 Document Analysis</div>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_results:
        st.info("📄 No analysis results available. Please upload and analyze documents first.")
        if st.button("Go to Upload Page"):
            st.session_state.current_page = "Upload"
            st.experimental_rerun()
        return
    
    # Analysis results overview
    st.markdown("### 📊 Analysis Overview")
    
    total_analyses = len(st.session_state.analysis_results)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Analyses", total_analyses)
    with col2:
        successful = sum(1 for r in st.session_state.analysis_results.values() 
                        if r['analysis']['success'])
        st.metric("Successful", successful)
    with col3:
        recent = sum(1 for r in st.session_state.analysis_results.values() 
                    if (datetime.now() - datetime.fromisoformat(r['timestamp'])).days == 0)
        st.metric("Today", recent)
    
    # Individual analysis results
    st.markdown("### 📋 Analysis Results")
    
    for key, result in st.session_state.analysis_results.items():
        with st.expander(f"📄 {result['file_name']} - {result['timestamp'][:16]}"):
            
            if result['analysis']['success']:
                # Display successful analysis
                analysis = result['analysis']['analysis']
                metadata = result['analysis']['metadata']
                
                # Metadata
                col_meta1, col_meta2 = st.columns(2)
                with col_meta1:
                    st.info(f"**Model**: {metadata.get('model', 'Unknown')}")
                    st.info(f"**Analysis Type**: {metadata.get('analysis_type', 'general')}")
                with col_meta2:
                    st.info(f"**Input Length**: {metadata.get('input_length', 0):,} chars")
                    st.info(f"**Response Length**: {metadata.get('output_length', 0):,} chars")
                
                # Analysis sections
                if 'sections' in analysis:
                    for section_name, section_content in analysis['sections'].items():
                        st.markdown(f"**{section_name.title()}**")
                        st.markdown(section_content)
                        st.markdown("---")
                
                # Action buttons
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button(f"📥 Download", key=f"download_{key}"):
                        download_analysis(result)
                with col_btn2:
                    if st.button(f"🔄 Re-analyze", key=f"reanalyze_{key}"):
                        st.info("Re-analysis feature - implement based on your needs")
                with col_btn3:
                    if st.button(f"🗑️ Delete", key=f"delete_{key}"):
                        del st.session_state.analysis_results[key]
                        st.experimental_rerun()
            
            else:
                # Display failed analysis
                st.error(f"❌ Analysis failed: {result['analysis'].get('error', 'Unknown error')}")

def handle_results_page():
    """Handle results page with data visualization"""
    st.markdown('<div class="main-header">📊 Results & Analytics</div>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_results:
        st.info("📄 No analysis results available for visualization.")
        return
    
    # Results analytics
    results_data = []
    for key, result in st.session_state.analysis_results.items():
        if result['analysis']['success']:
            metadata = result['analysis']['metadata']
            results_data.append({
                'File Name': result['file_name'],
                'Model': metadata.get('model', 'Unknown'),
                'Analysis Type': metadata.get('analysis_type', 'general'),
                'Input Length': metadata.get('input_length', 0),
                'Output Length': metadata.get('output_length', 0),
                'Timestamp': result['timestamp'][:16],
                'Success': True
            })
        else:
            results_data.append({
                'File Name': result['file_name'],
                'Model': 'N/A',
                'Analysis Type': 'N/A',
                'Input Length': 0,
                'Output Length': 0,
                'Timestamp': result['timestamp'][:16],
                'Success': False
            })
    
    df = pd.DataFrame(results_data)
    
    if not df.empty:
        # Summary metrics
        st.markdown("### 📈 Summary Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Documents", len(df))
        with col2:
            success_rate = df['Success'].mean() * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        with col3:
            avg_input = df[df['Success']]['Input Length'].mean()
            st.metric("Avg Input Length", f"{avg_input:,.0f}" if not pd.isna(avg_input) else "0")
        with col4:
            avg_output = df[df['Success']]['Output Length'].mean()
            st.metric("Avg Output Length", f"{avg_output:,.0f}" if not pd.isna(avg_output) else "0")
        
        # Data table
        st.markdown("### 📋 Results Table")
        st.dataframe(df, use_container_width=True)
        
        # Export options
        st.markdown("### 💾 Export Options")
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            if st.button("📥 Download CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV File",
                    data=csv,
                    file_name=f"{{app_name}}_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col_exp2:
            if st.button("📊 Generate Report"):
                generate_analysis_report(df)

def handle_settings_page():
    """Handle settings and configuration page"""
    st.markdown('<div class="main-header">⚙️ Settings & Configuration</div>', unsafe_allow_html=True)
    
    # Connection settings
    st.markdown("### 🔗 Snowflake Connection")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.snowflake_connected:
            st.success("✅ Connected to Snowflake")
        else:
            st.error("❌ Not connected to Snowflake")
    
    with col2:
        if st.button("🔄 Test Connection"):
            if check_snowflake_connection():
                st.success("Connection successful!")
            else:
                st.error("Connection failed. Check your configuration.")
    
    # AI model settings
    st.markdown("### 🤖 AI Model Settings")
    
    available_models = ai_analyzer.get_available_models()
    if available_models:
        st.success(f"✅ {len(available_models)} Cortex AI models available")
        
        with st.expander("Available Models"):
            for model_name, model_info in available_models.items():
                st.markdown(f"**{model_name}**")
                st.markdown(f"- {model_info['description']}")
                st.markdown(f"- Max tokens: {model_info['max_tokens']:,}")
                st.markdown(f"- Use case: {model_info['recommended_use']}")
                st.markdown("---")
    else:
        st.warning("⚠️ No Cortex AI models available. Check your Snowflake account settings.")
    
    # Application settings
    st.markdown("### 🔧 Application Settings")
    
    # Clear data option
    if st.button("🗑️ Clear All Analysis Results", type="secondary"):
        if st.checkbox("I confirm I want to delete all analysis results"):
            st.session_state.analysis_results = {}
            st.success("✅ All analysis results cleared")
    
    # Export settings
    if st.session_state.analysis_results:
        st.markdown("### 💾 Data Export")
        if st.button("📥 Export All Results"):
            export_all_results()

def save_result_to_snowflake(file_key, analysis_result):
    """Save analysis result to Snowflake table"""
    try:
        session = snowflake_utils.get_snowflake_session()
        if not session:
            raise Exception("No Snowflake session available")
        
        # Prepare data for insertion
        insert_data = {
            'ANALYSIS_ID': file_key,
            'FILE_NAME': st.session_state.analysis_results[file_key]['file_name'],
            'ANALYSIS_TYPE': analysis_result['metadata']['analysis_type'],
            'MODEL_USED': analysis_result['metadata']['model'],
            'ANALYSIS_RESULT': analysis_result['raw_response'],
            'INPUT_LENGTH': analysis_result['metadata']['input_length'],
            'OUTPUT_LENGTH': analysis_result['metadata']['output_length'],
            'CREATED_AT': datetime.now(),
            'SUCCESS': analysis_result['success']
        }
        
        # Insert into table (table should be created by setup script)
        table_name = "{{APP_NAME}}_ANALYSES"
        
        df = pd.DataFrame([insert_data])
        
        # Write to Snowflake
        session.write_pandas(
            df, 
            table_name, 
            auto_create_table=True,
            overwrite=False
        )
        
    except Exception as e:
        raise Exception(f"Failed to save to Snowflake: {str(e)}")

def download_analysis(result):
    """Download analysis result as JSON"""
    import json
    
    download_data = {
        'file_name': result['file_name'],
        'timestamp': result['timestamp'],
        'analysis': result['analysis']
    }
    
    json_str = json.dumps(download_data, indent=2, default=str)
    
    st.download_button(
        label=f"Download {result['file_name']} Analysis",
        data=json_str,
        file_name=f"{result['file_name']}_analysis.json",
        mime="application/json"
    )

def export_all_results():
    """Export all analysis results"""
    try:
        import json
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_results': len(st.session_state.analysis_results),
            'results': st.session_state.analysis_results
        }
        
        json_str = json.dumps(export_data, indent=2, default=str)
        
        st.download_button(
            label="📥 Download All Results (JSON)",
            data=json_str,
            file_name=f"{{app_name}}_all_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
        st.success("✅ Export ready for download")
        
    except Exception as e:
        st.error(f"❌ Export failed: {str(e)}")

def generate_analysis_report(df):
    """Generate a comprehensive analysis report"""
    try:
        report = f"""
# {{APP_NAME}} Analysis Report

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics

- **Total Documents Analyzed:** {len(df)}
- **Success Rate:** {df['Success'].mean() * 100:.1f}%
- **Average Input Length:** {df[df['Success']]['Input Length'].mean():,.0f} characters
- **Average Output Length:** {df[df['Success']]['Output Length'].mean():,.0f} characters

## Model Usage

{df[df['Success']].groupby('Model').size().to_string() if not df.empty else 'No successful analyses'}

## Analysis Types

{df[df['Success']].groupby('Analysis Type').size().to_string() if not df.empty else 'No successful analyses'}

## Files Processed

{chr(10).join(f"- {row['File Name']} ({'✅' if row['Success'] else '❌'})" for _, row in df.iterrows())}

---
*Generated by {{APP_NAME}} - AI-Powered Document Analysis*
        """
        
        st.download_button(
            label="📊 Download Analysis Report",
            data=report,
            file_name=f"{{app_name}}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
        
        st.success("✅ Report ready for download")
        
    except Exception as e:
        st.error(f"❌ Report generation failed: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error("❌ Application Error")
        st.error(f"Error: {str(e)}")
        
        if st.checkbox("Show Technical Details"):
            st.code(traceback.format_exc())