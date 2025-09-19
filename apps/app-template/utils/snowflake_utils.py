"""
Snowflake Utilities

Provides Snowflake connection management with flexible authentication options.
Based on the working patterns from the forms review application.
"""

import os
import tempfile
import base64
from snowflake.snowpark import Session
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
import streamlit as st
import re

load_dotenv()

def _load_private_key():
    """
    Load private key from file path or environment variable.
    
    Returns:
        bytes: Private key in DER format
        
    Raises:
        Exception: If no private key is found
    """
    print(f"🔍 Current working directory: {os.getcwd()}")
    print(f"🔍 Environment check:")
    print(f"   - SNOWFLAKE_PRIVATE_KEY_PATH: {'SET' if os.getenv('SNOWFLAKE_PRIVATE_KEY_PATH') else 'NOT SET'}")
    print(f"   - SNOWFLAKE_PRIVATE_KEY: {'SET' if os.getenv('SNOWFLAKE_PRIVATE_KEY') else 'NOT SET'}")

    # Try file path first (for SPCS containers)
    key_path = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")
    if key_path:
        print(f"🔑 Attempting to load private key from file: {key_path}")
        if os.path.exists(key_path):
            print(f"✅ Private key file exists: {key_path}")
            try:
                passphrase = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE", "").encode() or None
                with open(key_path, "rb") as f:
                    private_key = serialization.load_pem_private_key(
                        f.read(),
                        password=passphrase,
                    )
                print("✅ Private key loaded successfully from file")
                return private_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            except Exception as e:
                print(f"❌ Failed to load private key from file: {e}")
        else:
            print(f"❌ Private key file does not exist: {key_path}")
            # List directory contents for debugging
            key_dir = os.path.dirname(key_path)
            if os.path.exists(key_dir):
                print(f"🔍 Contents of {key_dir}:")
                try:
                    for item in os.listdir(key_dir):
                        item_path = os.path.join(key_dir, item)
                        print(f"   - {item} ({'dir' if os.path.isdir(item_path) else 'file'})")
                except Exception as e:
                    print(f"   Error listing directory: {e}")
            else:
                print(f"❌ Directory does not exist: {key_dir}")

    # Try environment variable second (for other deployments)
    private_key_content = os.getenv("SNOWFLAKE_PRIVATE_KEY")
    if private_key_content:
        print("🔑 Loading private key from environment variable")

        try:
            # Check if the key is base64 encoded (from some deployment methods)
            if not private_key_content.startswith('-----BEGIN'):
                print("🔑 Detected non-PEM format, trying base64 decode...")
                try:
                    # Try to decode as base64 first
                    decoded_key = base64.b64decode(private_key_content)
                    print("🔑 Successfully decoded base64 private key")

                    # Load the decoded key
                    passphrase = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE", "").encode() or None
                    private_key = serialization.load_pem_private_key(
                        decoded_key,
                        password=passphrase,
                    )
                    print("✅ Private key loaded successfully from environment variable (base64)")

                    return private_key.private_bytes(
                        encoding=serialization.Encoding.DER,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    )

                except Exception as base64_error:
                    print(f"⚠️ Base64 decoding failed: {base64_error}")
                    # If base64 decoding fails, treat as regular content
                    private_key_content = f"-----BEGIN PRIVATE KEY-----\n{private_key_content}\n-----END PRIVATE KEY-----"
            
            # Load the private key directly from string (PEM format)
            print("🔑 Loading as PEM format")
            passphrase = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE", "").encode() or None
            private_key = serialization.load_pem_private_key(
                private_key_content.encode('utf-8'),
                password=passphrase,
            )
            print("✅ Private key loaded successfully from environment variable (PEM)")

            return private_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

        except Exception as e:
            print(f"❌ Failed to load private key from environment variable: {e}")

    # No private key found
    raise Exception(
        "❌ No private key found. Set SNOWFLAKE_PRIVATE_KEY or SNOWFLAKE_PRIVATE_KEY_PATH")

@st.cache_resource
def get_session():
    """
    Create Snowflake session with password or private key authentication.
    
    Returns:
        Session: Snowflake session object or None if connection fails
    """
    print("🔍 Environment variables check:")
    for key in ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_ROLE",
                "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA"]:
        value = os.getenv(key)
        print(f"  {key}: {'SET' if value else 'NOT SET'}")

    # Check authentication methods
    has_password = bool(os.getenv("SNOWFLAKE_PASSWORD"))
    has_private_key_path = bool(os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH"))
    has_private_key = bool(os.getenv("SNOWFLAKE_PRIVATE_KEY"))
    
    print(f"  SNOWFLAKE_PASSWORD: {'SET' if has_password else 'NOT SET'}")
    print(f"  SNOWFLAKE_PRIVATE_KEY_PATH: {'SET' if has_private_key_path else 'NOT SET'}")
    print(f"  SNOWFLAKE_PRIVATE_KEY: {'SET' if has_private_key else 'NOT SET'}")

    conn = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "role": os.getenv("SNOWFLAKE_ROLE"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA"),
    }

    # Try password authentication first (for SPCS containers)
    if has_password:
        print("🔐 Using password authentication")
        conn["password"] = os.getenv("SNOWFLAKE_PASSWORD")
        
        # Remove None values
        conn = {k: v for k, v in conn.items() if v is not None}
        
        try:
            print(f"🔗 Connecting with password: {conn.get('user')}@{conn.get('account')}")
            session = Session.builder.configs(conn).create()
            print("✅ Snowflake session created successfully with password")
            return session
        except Exception as e:
            print(f"❌ Password authentication failed: {e}")
            # Fall back to private key if available
    
    # Try private key authentication as fallback
    if has_private_key_path or has_private_key:
        print("🔑 Falling back to private key authentication")
        try:
            pkb = _load_private_key()
            conn["private_key"] = pkb
            
            # Remove password if it was added above
            conn.pop("password", None)
            # Remove None values
            conn = {k: v for k, v in conn.items() if v is not None}

            print(f"🔗 Connecting with private key: {conn.get('user')}@{conn.get('account')}")
            session = Session.builder.configs(conn).create()
            print("✅ Snowflake session created successfully with private key")
            return session
        except Exception as e:
            print(f"❌ Private key authentication failed: {e}")

    # No valid authentication method found
    print("❌ No valid authentication method available")
    print("Available environment variables:")
    for key in ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_ROLE", "SNOWFLAKE_WAREHOUSE",
                "SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA", "SNOWFLAKE_PASSWORD"]:
        value = os.getenv(key)
        print(f"  {key}: {'SET' if value else 'NOT SET'}")
    
    raise Exception("❌ Failed to create Snowflake session. Need either SNOWFLAKE_PASSWORD or private key authentication.")

def verify_file_exists(session, stage_path):
    """
    Verify file exists in stage before analysis.
    
    Args:
        session: Snowflake session
        stage_path (str): Path to file in stage
        
    Returns:
        bool: True if file exists, False otherwise
    """
    try:
        list_result = session.sql(f"LIST '{stage_path}'").collect()
        if list_result:
            print(f"✅ File verified in stage: {stage_path}")
            return True
        else:
            print(f"❌ File not found in stage: {stage_path}")
            return False
    except Exception as e:
        print(f"❌ Error checking file in stage: {e}")
        return False

def clean_surrogates(text: str) -> str:
    """
    Clean surrogate characters from text.
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    return text.encode('utf-16', 'surrogatepass').decode('utf-16')

def execute_query(query, params=None):
    """
    Execute a Snowflake query with error handling.
    
    Args:
        query (str): SQL query to execute
        params (dict, optional): Query parameters
        
    Returns:
        pandas.DataFrame: Query results
    """
    try:
        session = get_session()
        if not session:
            raise Exception("Failed to get Snowflake session")
        
        if params:
            # Replace parameters in query
            for key, value in params.items():
                query = query.replace(f":{key}", str(value))
        
        result = session.sql(query).to_pandas()
        print(f"✅ Query executed successfully, returned {len(result)} rows")
        return result
        
    except Exception as e:
        print(f"❌ Query execution failed: {e}")
        raise

def create_stage_if_not_exists(stage_name, stage_type="internal"):
    """
    Create a Snowflake stage if it doesn't exist.
    
    Args:
        stage_name (str): Name of the stage
        stage_type (str): Type of stage (internal, external)
        
    Returns:
        bool: True if stage exists or was created successfully
    """
    try:
        session = get_session()
        
        # Check if stage exists
        result = session.sql(f"SHOW STAGES LIKE '{stage_name}'").collect()
        
        if result:
            print(f"✅ Stage {stage_name} already exists")
            return True
        
        # Create stage
        if stage_type == "internal":
            session.sql(f"CREATE STAGE {stage_name}").collect()
        else:
            # For external stages, additional configuration would be needed
            print(f"⚠️ External stage creation not implemented")
            return False
        
        print(f"✅ Stage {stage_name} created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create stage {stage_name}: {e}")
        return False

def upload_file_to_stage(file_path, stage_name, overwrite=True):
    """
    Upload a file to a Snowflake stage.
    
    Args:
        file_path (str): Local path to file
        stage_name (str): Name of the target stage
        overwrite (bool): Whether to overwrite existing files
        
    Returns:
        str: Stage path of uploaded file
    """
    try:
        session = get_session()
        
        # Construct PUT command
        put_command = f"PUT file://{file_path} @{stage_name}"
        if overwrite:
            put_command += " OVERWRITE=TRUE"
        
        # Execute PUT command
        result = session.sql(put_command).collect()
        
        # Extract filename for stage path
        filename = os.path.basename(file_path)
        stage_path = f"@{stage_name}/{filename}"
        
        print(f"✅ File uploaded to stage: {stage_path}")
        return stage_path
        
    except Exception as e:
        print(f"❌ Failed to upload file to stage: {e}")
        raise

def download_file_from_stage(stage_path, local_directory="/tmp"):
    """
    Download a file from a Snowflake stage.
    
    Args:
        stage_path (str): Path to file in stage
        local_directory (str): Local directory to download to
        
    Returns:
        str: Local path of downloaded file
    """
    try:
        session = get_session()
        
        # Construct GET command
        get_command = f"GET {stage_path} file://{local_directory}"
        
        # Execute GET command
        result = session.sql(get_command).collect()
        
        # Construct local file path
        filename = os.path.basename(stage_path.replace('@', '').split('/')[-1])
        local_path = os.path.join(local_directory, filename)
        
        print(f"✅ File downloaded from stage: {local_path}")
        return local_path
        
    except Exception as e:
        print(f"❌ Failed to download file from stage: {e}")
        raise

def save_results_to_table(results_df, table_name, mode="append"):
    """
    Save results DataFrame to Snowflake table.
    
    Args:
        results_df (pandas.DataFrame): Results to save
        table_name (str): Target table name
        mode (str): Write mode (append, overwrite, replace)
        
    Returns:
        bool: True if successful
    """
    try:
        session = get_session()
        
        # Convert pandas DataFrame to Snowpark DataFrame
        snowpark_df = session.create_dataframe(results_df)
        
        # Save to table
        if mode == "overwrite":
            snowpark_df.write.mode("overwrite").save_as_table(table_name)
        elif mode == "replace":
            snowpark_df.write.mode("replace").save_as_table(table_name)
        else:  # append
            snowpark_df.write.mode("append").save_as_table(table_name)
        
        print(f"✅ Results saved to table {table_name} ({len(results_df)} rows)")
        return True
        
    except Exception as e:
        print(f"❌ Failed to save results to table: {e}")
        return False

def get_connection_status():
    """
    Get current connection status and details.
    
    Returns:
        dict: Connection status information
    """
    try:
        session = get_session()
        
        # Get connection details
        current_info = session.sql("""
            SELECT 
                CURRENT_USER() as user,
                CURRENT_ROLE() as role,
                CURRENT_DATABASE() as database,
                CURRENT_SCHEMA() as schema,
                CURRENT_WAREHOUSE() as warehouse,
                CURRENT_ACCOUNT() as account
        """).collect()[0]
        
        return {
            "status": "connected",
            "user": current_info[0],
            "role": current_info[1],
            "database": current_info[2],
            "schema": current_info[3],
            "warehouse": current_info[4],
            "account": current_info[5]
        }
        
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e)
        }

def test_connection():
    """
    Test the Snowflake connection and return status.
    
    Returns:
        dict: Test results
    """
    try:
        session = get_session()
        
        # Simple test query
        result = session.sql("SELECT 1 as test").collect()
        
        if result and result[0][0] == 1:
            connection_info = get_connection_status()
            return {
                "success": True,
                "message": "Connection successful",
                "details": connection_info
            }
        else:
            return {
                "success": False,
                "message": "Connection test failed",
                "details": None
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection failed: {str(e)}",
            "details": None
        }