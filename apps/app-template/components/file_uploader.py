"""
File Uploader Component

Provides secure file upload functionality with validation and progress tracking.
"""

import streamlit as st
import io
from pathlib import Path
import mimetypes

def create_uploader(
    accepted_types=None,
    max_file_size=200,
    multiple_files=False,
    label="Choose a file to upload",
    help_text=None
):
    """
    Create a file uploader with validation and user feedback.
    
    Args:
        accepted_types (list): List of accepted file extensions (e.g., [".pdf", ".txt"])
        max_file_size (int): Maximum file size in MB
        multiple_files (bool): Allow multiple file uploads
        label (str): Upload button label
        help_text (str): Help text to display
    
    Returns:
        UploadedFile or list: Uploaded file(s) or None
    """
    
    if accepted_types is None:
        accepted_types = [".pdf", ".txt", ".docx", ".csv", ".json"]
    
    # Display accepted formats
    st.markdown(f"**Accepted formats:** {', '.join(accepted_types)}")
    st.markdown(f"**Maximum file size:** {max_file_size} MB")
    
    # File uploader
    uploaded_files = st.file_uploader(
        label,
        type=[ext.lstrip('.') for ext in accepted_types],
        accept_multiple_files=multiple_files,
        help=help_text
    )
    
    if uploaded_files is not None:
        # Handle single file
        if not multiple_files:
            return validate_and_process_file(uploaded_files, max_file_size, accepted_types)
        
        # Handle multiple files
        validated_files = []
        for file in uploaded_files:
            validated_file = validate_and_process_file(file, max_file_size, accepted_types)
            if validated_file:
                validated_files.append(validated_file)
        
        return validated_files if validated_files else None
    
    return None

def validate_and_process_file(uploaded_file, max_file_size, accepted_types):
    """
    Validate and process a single uploaded file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        max_file_size (int): Maximum file size in MB
        accepted_types (list): List of accepted file extensions
    
    Returns:
        UploadedFile: Validated file or None if invalid
    """
    
    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > max_file_size:
        st.error(f"❌ File too large: {file_size_mb:.1f} MB (max: {max_file_size} MB)")
        return None
    
    # Check file extension
    file_extension = Path(uploaded_file.name).suffix.lower()
    if file_extension not in accepted_types:
        st.error(f"❌ Unsupported file type: {file_extension}")
        return None
    
    # Display file info
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ **{uploaded_file.name}**")
        st.write(f"Size: {file_size_mb:.2f} MB")
        st.write(f"Type: {file_extension}")
    
    with col2:
        # File preview for supported types
        if file_extension in ['.txt', '.json', '.csv']:
            try:
                content_preview = str(uploaded_file.read(500), 'utf-8')
                uploaded_file.seek(0)  # Reset file pointer
                
                with st.expander("📄 Preview"):
                    st.text(content_preview + "..." if len(content_preview) == 500 else content_preview)
            except:
                st.info("Preview not available")
        else:
            st.info(f"File ready for processing")
    
    return uploaded_file

def create_drag_drop_uploader(accepted_types=None, max_file_size=200):
    """
    Create a drag-and-drop file uploader with visual feedback.
    
    Args:
        accepted_types (list): List of accepted file extensions
        max_file_size (int): Maximum file size in MB
    
    Returns:
        UploadedFile: Uploaded file or None
    """
    
    if accepted_types is None:
        accepted_types = [".pdf", ".txt", ".docx"]
    
    # Custom CSS for drag-and-drop styling
    st.markdown("""
    <style>
    .uploadedFile {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin: 20px 0;
    }
    .uploadedFile:hover {
        border-color: #007bff;
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="uploadedFile">', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📁 Drag and drop your file here, or click to browse",
        type=[ext.lstrip('.') for ext in accepted_types],
        help=f"Supported formats: {', '.join(accepted_types)} (max {max_file_size} MB)"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file:
        return validate_and_process_file(uploaded_file, max_file_size, accepted_types)
    
    return None

def create_batch_uploader(accepted_types=None, max_files=10):
    """
    Create a batch file uploader for processing multiple files.
    
    Args:
        accepted_types (list): List of accepted file extensions
        max_files (int): Maximum number of files
    
    Returns:
        list: List of uploaded files
    """
    
    st.subheader("📁 Batch File Upload")
    
    uploaded_files = st.file_uploader(
        f"Upload up to {max_files} files",
        type=[ext.lstrip('.') for ext in accepted_types] if accepted_types else None,
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if len(uploaded_files) > max_files:
            st.error(f"❌ Too many files: {len(uploaded_files)} (max: {max_files})")
            return None
        
        st.success(f"✅ {len(uploaded_files)} files uploaded")
        
        # Display file list
        with st.expander("📋 File List"):
            for i, file in enumerate(uploaded_files, 1):
                st.write(f"{i}. {file.name} ({file.size:,} bytes)")
        
        return uploaded_files
    
    return None

def save_uploaded_file(uploaded_file, save_directory="temp"):
    """
    Save uploaded file to local directory.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        save_directory (str): Directory to save the file
    
    Returns:
        str: Path to saved file
    """
    
    # Create directory if it doesn't exist
    save_path = Path(save_directory)
    save_path.mkdir(exist_ok=True)
    
    # Save file
    file_path = save_path / uploaded_file.name
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return str(file_path)

def get_file_info(uploaded_file):
    """
    Get detailed information about an uploaded file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        dict: File information
    """
    
    file_extension = Path(uploaded_file.name).suffix.lower()
    mime_type, _ = mimetypes.guess_type(uploaded_file.name)
    
    return {
        "name": uploaded_file.name,
        "size": uploaded_file.size,
        "size_mb": uploaded_file.size / (1024 * 1024),
        "type": uploaded_file.type,
        "extension": file_extension,
        "mime_type": mime_type
    }

def create_upload_progress(total_files, current_file=0):
    """
    Create a progress bar for file uploads.
    
    Args:
        total_files (int): Total number of files to upload
        current_file (int): Current file being processed
    
    Returns:
        streamlit.progress: Progress bar object
    """
    
    progress = st.progress(0)
    status = st.empty()
    
    if current_file > 0:
        progress_value = current_file / total_files
        progress.progress(progress_value)
        status.text(f"Processing file {current_file} of {total_files}")
    
    return progress, status