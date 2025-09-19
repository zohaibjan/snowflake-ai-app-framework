"""
Feedback Display Component

Provides consistent user feedback, results display, and status messages.
"""

import streamlit as st
import json
from datetime import datetime
import pandas as pd

def show_success(message, details=None):
    """
    Display success message with optional details.
    
    Args:
        message (str): Success message to display
        details (str, optional): Additional details
    """
    st.success(f"✅ {message}")
    
    if details:
        with st.expander("📋 Details"):
            if isinstance(details, dict):
                st.json(details)
            else:
                st.text(details)

def show_error(message, error=None, show_details=False):
    """
    Display error message with optional error details.
    
    Args:
        message (str): Error message to display
        error (Exception, optional): Exception object
        show_details (bool): Whether to show error details
    """
    st.error(f"❌ {message}")
    
    if error and show_details:
        with st.expander("🔍 Error Details"):
            st.code(str(error))

def show_warning(message, details=None):
    """
    Display warning message with optional details.
    
    Args:
        message (str): Warning message
        details (str, optional): Additional details
    """
    st.warning(f"⚠️ {message}")
    
    if details:
        with st.expander("📋 Details"):
            st.text(details)

def show_info(message, details=None):
    """
    Display info message with optional details.
    
    Args:
        message (str): Info message
        details (str, optional): Additional details
    """
    st.info(f"ℹ️ {message}")
    
    if details:
        with st.expander("📋 Details"):
            st.text(details)

def show_results(results, title="Analysis Results", show_raw=False):
    """
    Display analysis results in a structured format.
    
    Args:
        results (dict): Results dictionary
        title (str): Title for results section
        show_raw (bool): Whether to show raw JSON data
    """
    st.subheader(f"📊 {title}")
    
    if not results:
        st.warning("No results to display")
        return
    
    # Main results display
    if isinstance(results, dict):
        display_dict_results(results)
    elif isinstance(results, list):
        display_list_results(results)
    else:
        st.text(str(results))
    
    # Raw data option
    if show_raw:
        with st.expander("🔍 Raw Data"):
            st.json(results)

def display_dict_results(results_dict):
    """
    Display dictionary results in organized format.
    
    Args:
        results_dict (dict): Results dictionary
    """
    for key, value in results_dict.items():
        if key.lower() in ['summary', 'conclusion', 'analysis']:
            st.markdown(f"**{key.replace('_', ' ').title()}:**")
            st.markdown(value)
            st.markdown("---")
        
        elif key.lower() in ['score', 'confidence', 'rating']:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{key.replace('_', ' ').title()}**")
            with col2:
                if isinstance(value, (int, float)):
                    st.metric("", f"{value:.2f}" if isinstance(value, float) else str(value))
                else:
                    st.write(value)
        
        elif isinstance(value, list):
            st.markdown(f"**{key.replace('_', ' ').title()}:**")
            for item in value:
                st.write(f"• {item}")
            st.markdown("---")
        
        elif isinstance(value, dict):
            with st.expander(f"📋 {key.replace('_', ' ').title()}"):
                display_dict_results(value)
        
        else:
            st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

def display_list_results(results_list):
    """
    Display list results in organized format.
    
    Args:
        results_list (list): Results list
    """
    for i, item in enumerate(results_list, 1):
        with st.expander(f"📋 Result {i}"):
            if isinstance(item, dict):
                display_dict_results(item)
            else:
                st.write(item)

def create_results_summary(results, metrics=None):
    """
    Create a summary dashboard for results.
    
    Args:
        results (dict): Results data
        metrics (dict): Key metrics to highlight
    """
    st.subheader("📈 Results Summary")
    
    # Metrics row
    if metrics:
        cols = st.columns(len(metrics))
        for i, (metric_name, metric_value) in enumerate(metrics.items()):
            with cols[i]:
                st.metric(metric_name, metric_value)
    
    # Results breakdown
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if 'summary' in results:
            st.markdown("**Key Findings:**")
            st.markdown(results['summary'])
        
        if 'recommendations' in results:
            st.markdown("**Recommendations:**")
            for rec in results['recommendations']:
                st.write(f"• {rec}")
    
    with col2:
        # Status indicators
        if 'status' in results:
            status = results['status'].lower()
            if status == 'success':
                st.success("✅ Completed")
            elif status == 'warning':
                st.warning("⚠️ Completed with Issues")
            elif status == 'error':
                st.error("❌ Failed")
            else:
                st.info(f"ℹ️ {results['status']}")
        
        # Timestamp
        if 'timestamp' in results:
            st.write(f"**Completed:** {results['timestamp']}")
        else:
            st.write(f"**Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def show_processing_status(status, progress=None, details=None):
    """
    Show processing status with progress indicator.
    
    Args:
        status (str): Current status message
        progress (float): Progress value (0.0 to 1.0)
        details (str): Additional details
    """
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if progress is not None:
            st.progress(progress)
            st.text(f"{status} ({int(progress * 100)}%)")
        else:
            with st.spinner(status):
                pass
    
    with col2:
        if details:
            with st.expander("Details"):
                st.text(details)

def create_comparison_display(results_list, labels=None):
    """
    Create a comparison display for multiple results.
    
    Args:
        results_list (list): List of results to compare
        labels (list): Labels for each result
    """
    if not labels:
        labels = [f"Result {i+1}" for i in range(len(results_list))]
    
    st.subheader("🔄 Results Comparison")
    
    # Create tabs for each result
    tabs = st.tabs(labels)
    
    for i, (tab, result) in enumerate(zip(tabs, results_list)):
        with tab:
            show_results(result, title=f"{labels[i]} Details")

def export_results(results, filename=None, format='json'):
    """
    Provide export functionality for results.
    
    Args:
        results (dict): Results to export
        filename (str): Filename for export
        format (str): Export format ('json', 'csv', 'txt')
    
    Returns:
        str: Download link or data
    """
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"results_{timestamp}.{format}"
    
    if format == 'json':
        data = json.dumps(results, indent=2)
        mime_type = 'application/json'
    
    elif format == 'csv' and isinstance(results, dict):
        # Convert dict to DataFrame if possible
        try:
            if all(isinstance(v, list) for v in results.values()):
                df = pd.DataFrame(results)
                data = df.to_csv(index=False)
            else:
                # Flatten dict for CSV
                flattened = {}
                for k, v in results.items():
                    if isinstance(v, (str, int, float)):
                        flattened[k] = [v]
                    elif isinstance(v, list):
                        flattened[k] = v
                
                df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in flattened.items()]))
                data = df.to_csv(index=False)
            
            mime_type = 'text/csv'
        except:
            st.error("Cannot convert results to CSV format")
            return None
    
    elif format == 'txt':
        if isinstance(results, dict):
            data = "\n".join([f"{k}: {v}" for k, v in results.items()])
        else:
            data = str(results)
        mime_type = 'text/plain'
    
    else:
        st.error(f"Unsupported export format: {format}")
        return None
    
    # Create download button
    st.download_button(
        label=f"📥 Download {format.upper()}",
        data=data,
        file_name=filename,
        mime=mime_type
    )
    
    return data

def show_data_table(data, title="Data Table", searchable=True):
    """
    Display data in an interactive table format.
    
    Args:
        data (pd.DataFrame or dict): Data to display
        title (str): Table title
        searchable (bool): Enable search functionality
    """
    st.subheader(f"📊 {title}")
    
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    else:
        df = data
    
    # Search functionality
    if searchable and not df.empty:
        search_term = st.text_input("🔍 Search table:", key=f"search_{title}")
        if search_term:
            # Search across all columns
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            df = df[mask]
    
    # Display table
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.caption(f"Showing {len(df)} rows")
    else:
        st.warning("No data to display")

def create_alert_banner(message, alert_type="info", dismissible=True):
    """
    Create alert banners for important messages.
    
    Args:
        message (str): Alert message
        alert_type (str): Type of alert (info, success, warning, error)
        dismissible (bool): Whether alert can be dismissed
    """
    alert_key = f"alert_{hash(message)}"
    
    if dismissible and st.session_state.get(f"{alert_key}_dismissed", False):
        return
    
    col1, col2 = st.columns([10, 1]) if dismissible else st.columns([1])
    
    with col1:
        if alert_type == "success":
            st.success(message)
        elif alert_type == "warning":
            st.warning(message)
        elif alert_type == "error":
            st.error(message)
        else:
            st.info(message)
    
    if dismissible:
        with col2:
            if st.button("✕", key=f"{alert_key}_dismiss"):
                st.session_state[f"{alert_key}_dismissed"] = True
                st.rerun()