"""
Stage Upload Utilities

Handles file uploads to Snowflake stages with progress tracking and validation.
"""

import os
import tempfile
import streamlit as st
from pathlib import Path
from .snowflake_utils import get_session, create_stage_if_not_exists

def upload_to_stage(uploaded_file, stage_name="DEFAULT_STAGE", file_prefix=""):
    """
    Upload a Streamlit uploaded file to Snowflake stage.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        stage_name (str): Target stage name
        file_prefix (str): Optional prefix for the uploaded file
        
    Returns:
        str: Stage path of uploaded file
        
    Raises:
        Exception: If upload fails
    """
    
    # Validate inputs
    if not uploaded_file:
        raise ValueError("No file provided for upload")
    
    if not stage_name:
        raise ValueError("Stage name is required")
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            # Write uploaded file content to temporary file
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Create stage if it doesn't exist
        create_stage_if_not_exists(stage_name)
        
        # Get Snowflake session
        session = get_session()
        if not session:
            raise Exception("Failed to establish Snowflake connection")
        
        # Construct filename with optional prefix
        original_filename = uploaded_file.name
        if file_prefix:
            filename = f"{file_prefix}_{original_filename}"
        else:
            filename = original_filename
        
        # Upload to stage using PUT command
        put_command = f"PUT file://{tmp_file_path} @{stage_name} AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
        
        print(f"🔄 Uploading {original_filename} to stage {stage_name}...")
        result = session.sql(put_command).collect()
        
        # Cleanup temporary file
        os.unlink(tmp_file_path)
        
        # Construct stage path for return
        stage_path = f"@{stage_name}/{original_filename}"
        
        # Log success
        print(f"✅ File uploaded successfully to {stage_path}")
        
        return stage_path
        
    except Exception as e:
        # Cleanup temporary file if it exists
        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        
        print(f"❌ Upload failed: {e}")
        raise Exception(f"Failed to upload file to stage: {str(e)}")

def upload_multiple_files(uploaded_files, stage_name="DEFAULT_STAGE", file_prefix=""):
    """
    Upload multiple files to Snowflake stage with progress tracking.
    
    Args:
        uploaded_files (list): List of Streamlit UploadedFile objects
        stage_name (str): Target stage name
        file_prefix (str): Optional prefix for uploaded files
        
    Returns:
        list: List of stage paths for uploaded files
    """
    
    if not uploaded_files:
        raise ValueError("No files provided for upload")
    
    uploaded_paths = []
    failed_uploads = []
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                # Update progress
                progress = (i + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                status_text.text(f"Uploading {uploaded_file.name} ({i+1}/{len(uploaded_files)})")
                
                # Upload individual file
                stage_path = upload_to_stage(uploaded_file, stage_name, file_prefix)
                uploaded_paths.append(stage_path)
                
            except Exception as e:
                print(f"❌ Failed to upload {uploaded_file.name}: {e}")
                failed_uploads.append({"file": uploaded_file.name, "error": str(e)})
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Report results
        if failed_uploads:
            st.warning(f"⚠️ {len(failed_uploads)} files failed to upload:")
            for failure in failed_uploads:
                st.error(f"- {failure['file']}: {failure['error']}")
        
        if uploaded_paths:
            st.success(f"✅ {len(uploaded_paths)} files uploaded successfully")
        
        return uploaded_paths
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        raise Exception(f"Batch upload failed: {str(e)}")

def list_stage_files(stage_name, pattern=""):
    """
    List files in a Snowflake stage.
    
    Args:
        stage_name (str): Stage name to list
        pattern (str): Optional file pattern filter
        
    Returns:
        list: List of file information dictionaries
    """
    
    try:
        session = get_session()
        if not session:
            raise Exception("Failed to establish Snowflake connection")
        
        # Construct LIST command
        list_command = f"LIST @{stage_name}"
        if pattern:
            list_command += f" PATTERN='{pattern}'"
        
        # Execute LIST command
        result = session.sql(list_command).collect()
        
        # Parse results
        files = []
        for row in result:
            file_info = {
                "name": row[0],  # File name
                "size": row[1],  # File size
                "md5": row[2],   # MD5 hash
                "last_modified": row[3]  # Last modified timestamp
            }
            files.append(file_info)
        
        print(f"✅ Listed {len(files)} files in stage {stage_name}")
        return files
        
    except Exception as e:
        print(f"❌ Failed to list stage files: {e}")
        raise Exception(f"Failed to list files in stage {stage_name}: {str(e)}")

def delete_stage_file(stage_path):
    """
    Delete a file from Snowflake stage.
    
    Args:
        stage_path (str): Full path to file in stage (e.g., @STAGE_NAME/file.txt)
        
    Returns:
        bool: True if deletion was successful
    """
    
    try:
        session = get_session()
        if not session:
            raise Exception("Failed to establish Snowflake connection")
        
        # Execute REMOVE command
        remove_command = f"REMOVE {stage_path}"
        result = session.sql(remove_command).collect()
        
        print(f"✅ File deleted from stage: {stage_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to delete stage file: {e}")
        raise Exception(f"Failed to delete file {stage_path}: {str(e)}")

def get_stage_file_content(stage_path, encoding="utf-8"):
    """
    Get content of a text file from Snowflake stage.
    
    Args:
        stage_path (str): Path to file in stage
        encoding (str): Text encoding to use
        
    Returns:
        str: File content
    """
    
    try:
        session = get_session()
        if not session:
            raise Exception("Failed to establish Snowflake connection")
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download file from stage
            get_command = f"GET {stage_path} file://{temp_dir}"
            session.sql(get_command).collect()
            
            # Find downloaded file
            downloaded_files = os.listdir(temp_dir)
            if not downloaded_files:
                raise Exception("No file was downloaded")
            
            # Read file content
            file_path = os.path.join(temp_dir, downloaded_files[0])
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
        
        print(f"✅ Retrieved content from stage file: {stage_path}")
        return content
        
    except Exception as e:
        print(f"❌ Failed to get stage file content: {e}")
        raise Exception(f"Failed to retrieve content from {stage_path}: {str(e)}")

def copy_stage_file(source_stage_path, target_stage_path):
    """
    Copy a file from one stage location to another.
    
    Args:
        source_stage_path (str): Source file path in stage
        target_stage_path (str): Target file path in stage
        
    Returns:
        bool: True if copy was successful
    """
    
    try:
        session = get_session()
        if not session:
            raise Exception("Failed to establish Snowflake connection")
        
        # Use SQL COPY command
        copy_command = f"COPY FILES INTO {target_stage_path} FROM {source_stage_path}"
        result = session.sql(copy_command).collect()
        
        print(f"✅ File copied from {source_stage_path} to {target_stage_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to copy stage file: {e}")
        raise Exception(f"Failed to copy file: {str(e)}")

def validate_stage_access(stage_name):
    """
    Validate that the current user has access to the specified stage.
    
    Args:
        stage_name (str): Stage name to validate
        
    Returns:
        dict: Validation results
    """
    
    try:
        session = get_session()
        if not session:
            raise Exception("Failed to establish Snowflake connection")
        
        # Try to list the stage
        try:
            result = session.sql(f"LIST @{stage_name}").collect()
            file_count = len(result)
            
            return {
                "accessible": True,
                "message": f"Stage accessible with {file_count} files",
                "file_count": file_count
            }
            
        except Exception as list_error:
            # Try to show the stage instead
            try:
                result = session.sql(f"SHOW STAGES LIKE '{stage_name}'").collect()
                if result:
                    return {
                        "accessible": False,
                        "message": "Stage exists but no read access",
                        "file_count": 0
                    }
                else:
                    return {
                        "accessible": False,
                        "message": "Stage does not exist",
                        "file_count": 0
                    }
                    
            except Exception as show_error:
                return {
                    "accessible": False,
                    "message": f"Cannot access stage: {str(show_error)}",
                    "file_count": 0
                }
                
    except Exception as e:
        return {
            "accessible": False,
            "message": f"Validation failed: {str(e)}",
            "file_count": 0
        }

def create_upload_session(stage_name, session_id=None):
    """
    Create an upload session for tracking multiple file uploads.
    
    Args:
        stage_name (str): Target stage name
        session_id (str): Optional session identifier
        
    Returns:
        dict: Upload session information
    """
    
    import uuid
    from datetime import datetime
    
    if not session_id:
        session_id = str(uuid.uuid4())[:8]
    
    session_info = {
        "session_id": session_id,
        "stage_name": stage_name,
        "created_at": datetime.now().isoformat(),
        "uploaded_files": [],
        "failed_files": [],
        "status": "active"
    }
    
    # Store in Streamlit session state
    if 'upload_sessions' not in st.session_state:
        st.session_state.upload_sessions = {}
    
    st.session_state.upload_sessions[session_id] = session_info
    
    return session_info

def get_upload_session(session_id):
    """
    Retrieve an upload session by ID.
    
    Args:
        session_id (str): Session identifier
        
    Returns:
        dict: Upload session information or None
    """
    
    if 'upload_sessions' not in st.session_state:
        return None
    
    return st.session_state.upload_sessions.get(session_id)

def close_upload_session(session_id):
    """
    Close an upload session.
    
    Args:
        session_id (str): Session identifier
        
    Returns:
        dict: Final session summary
    """
    
    session_info = get_upload_session(session_id)
    if not session_info:
        return None
    
    session_info["status"] = "closed"
    session_info["closed_at"] = datetime.now().isoformat()
    
    return {
        "session_id": session_id,
        "total_files": len(session_info["uploaded_files"]) + len(session_info["failed_files"]),
        "successful_uploads": len(session_info["uploaded_files"]),
        "failed_uploads": len(session_info["failed_files"]),
        "stage_name": session_info["stage_name"]
    }