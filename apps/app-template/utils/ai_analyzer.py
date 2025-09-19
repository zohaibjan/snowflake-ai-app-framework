"""
AI Analysis Utilities - Snowflake Cortex AI Integration

Handles AI-powered document analysis using Snowflake Cortex AI models.
Provides functions for document analysis, feedback generation, and AI model management.
"""

import json
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Any
from snowflake.snowpark import Session

# Cortex AI Model Configuration
CORTEX_MODELS = {
    'mistral-large': {
        'description': 'Large multilingual model, best for complex analysis',
        'max_tokens': 8000,
        'recommended_use': 'Complex document analysis, detailed reviews'
    },
    'llama2-70b-chat': {
        'description': 'Meta Llama 2 70B chat model',
        'max_tokens': 4000,
        'recommended_use': 'Conversational analysis, Q&A'
    },
    'reka-flash': {
        'description': 'Fast and efficient model for quick analysis',
        'max_tokens': 2000,
        'recommended_use': 'Quick document scanning, basic feedback'
    },
    'mixtral-8x7b': {
        'description': 'Mixture of experts model, balanced performance',
        'max_tokens': 4000,
        'recommended_use': 'General purpose analysis, balanced speed/quality'
    }
}

# Default model configuration
DEFAULT_MODEL = 'mistral-large'
DEFAULT_TEMPERATURE = 0.1
DEFAULT_MAX_TOKENS = 4000

def get_available_models() -> Dict[str, Dict[str, Any]]:
    """
    Get list of available Cortex AI models with their configurations.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary of model configurations
    """
    return CORTEX_MODELS

def test_cortex_connection(session: Session) -> bool:
    """
    Test connection to Snowflake Cortex AI.
    
    Args:
        session (Session): Snowflake session
        
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        test_query = """
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'mistral-large',
            'Say hello in exactly 3 words.',
            {}
        ) as response
        """.format(json.dumps({"temperature": 0.1, "max_tokens": 10}))
        
        result = session.sql(test_query).collect()
        
        if result and len(result) > 0:
            response = result[0]['RESPONSE']
            st.success("✅ Cortex AI connection successful!")
            st.info(f"Test response: {response}")
            return True
        else:
            st.error("❌ No response from Cortex AI")
            return False
            
    except Exception as e:
        st.error(f"❌ Cortex AI connection failed: {str(e)}")
        return False

def analyze_document_content(
    content: str,
    analysis_type: str = "general",
    model: str = DEFAULT_MODEL,
    session: Session = None,
    custom_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze document content using Snowflake Cortex AI.
    
    Args:
        content (str): Document content to analyze
        analysis_type (str): Type of analysis to perform
        model (str): Cortex AI model to use
        session (Session): Snowflake session
        custom_prompt (str, optional): Custom analysis prompt
        
    Returns:
        Dict[str, Any]: Analysis results with feedback and metadata
    """
    
    if not session:
        st.error("❌ Snowflake session required for AI analysis")
        return {"error": "No Snowflake session provided"}
    
    if model not in CORTEX_MODELS:
        st.warning(f"⚠️ Model '{model}' not recognized, using default: {DEFAULT_MODEL}")
        model = DEFAULT_MODEL
    
    try:
        # Get analysis prompt
        prompt = custom_prompt or get_analysis_prompt(analysis_type, content)
        
        # Prepare Cortex AI parameters
        cortex_params = {
            "temperature": DEFAULT_TEMPERATURE,
            "max_tokens": min(DEFAULT_MAX_TOKENS, CORTEX_MODELS[model]['max_tokens'])
        }
        
        # Execute Cortex AI query
        cortex_query = """
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            '{}',
            '{}',
            {}
        ) as response
        """.format(
            model,
            prompt.replace("'", "\\'"),
            json.dumps(cortex_params)
        )
        
        with st.spinner(f"🤖 Analyzing with {model}..."):
            result = session.sql(cortex_query).collect()
        
        if result and len(result) > 0:
            ai_response = result[0]['RESPONSE']
            
            # Parse structured response if possible
            try:
                if ai_response.strip().startswith('{'):
                    parsed_response = json.loads(ai_response)
                else:
                    parsed_response = {
                        "analysis": ai_response,
                        "summary": ai_response[:200] + "..." if len(ai_response) > 200 else ai_response
                    }
            except json.JSONDecodeError:
                parsed_response = {
                    "analysis": ai_response,
                    "summary": ai_response[:200] + "..." if len(ai_response) > 200 else ai_response
                }
            
            # Add metadata
            analysis_result = {
                "success": True,
                "model_used": model,
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "content_length": len(content),
                "response": parsed_response
            }
            
            st.success(f"✅ Analysis completed using {model}")
            return analysis_result
            
        else:
            error_msg = "No response received from Cortex AI"
            st.error(f"❌ {error_msg}")
            return {"error": error_msg, "success": False}
            
    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        st.error(f"❌ {error_msg}")
        return {"error": error_msg, "success": False}

def get_analysis_prompt(analysis_type: str, content: str) -> str:
    """
    Generate analysis prompt based on type and content.
    
    Args:
        analysis_type (str): Type of analysis to perform
        content (str): Document content
        
    Returns:
        str: Formatted prompt for AI analysis
    """
    
    prompts = {
        "general": """
Analyze the following document and provide a comprehensive review:

{content}

Please provide your analysis in the following JSON format:
{{
    "summary": "Brief summary of the document",
    "key_points": ["list", "of", "key", "points"],
    "issues_found": ["any", "issues", "or", "concerns"],
    "recommendations": ["suggested", "improvements"],
    "overall_score": "score from 1-10",
    "confidence": "high/medium/low"
}}
""",
        
        "compliance": """
Review the following document for compliance and regulatory issues:

{content}

Analyze for:
1. Regulatory compliance
2. Missing required information
3. Potential legal issues
4. Risk assessment

Provide response in JSON format:
{{
    "compliance_score": "score from 1-10",
    "critical_issues": ["list", "of", "critical", "issues"],
    "minor_issues": ["list", "of", "minor", "issues"],
    "missing_elements": ["required", "elements", "not", "found"],
    "recommendations": ["compliance", "recommendations"],
    "risk_level": "high/medium/low"
}}
""",
        
        "quality": """
Assess the quality and completeness of the following document:

{content}

Evaluate:
1. Information completeness
2. Clarity and readability
3. Structure and organization
4. Data accuracy
5. Professional presentation

Provide response in JSON format:
{{
    "quality_score": "score from 1-10",
    "completeness": "percentage complete",
    "strengths": ["document", "strengths"],
    "weaknesses": ["areas", "for", "improvement"],
    "missing_info": ["missing", "information"],
    "suggestions": ["improvement", "suggestions"]
}}
""",
        
        "extraction": """
Extract key information from the following document:

{content}

Extract and structure the following information:
{{
    "document_type": "identified document type",
    "key_entities": {{"names": [], "dates": [], "amounts": [], "locations": []}},
    "important_fields": {{"field_name": "field_value"}},
    "action_items": ["extracted", "action", "items"],
    "deadlines": ["any", "deadlines", "found"],
    "contact_info": {{"emails": [], "phones": [], "addresses": []}}
}}
"""
    }
    
    return prompts.get(analysis_type, prompts["general"]).format(content=content[:8000])

def batch_analyze_documents(
    documents: List[Dict[str, str]],
    analysis_type: str = "general",
    model: str = DEFAULT_MODEL,
    session: Session = None
) -> List[Dict[str, Any]]:
    """
    Analyze multiple documents in batch.
    
    Args:
        documents (List[Dict[str, str]]): List of documents with 'name' and 'content'
        analysis_type (str): Type of analysis to perform
        model (str): Cortex AI model to use
        session (Session): Snowflake session
        
    Returns:
        List[Dict[str, Any]]: List of analysis results
    """
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, doc in enumerate(documents):
        status_text.text(f"Analyzing {doc['name']}... ({i+1}/{len(documents)})")
        
        result = analyze_document_content(
            content=doc['content'],
            analysis_type=analysis_type,
            model=model,
            session=session
        )
        
        result['document_name'] = doc['name']
        results.append(result)
        
        progress_bar.progress((i + 1) / len(documents))
    
    status_text.text("✅ Batch analysis complete!")
    return results

def generate_analysis_report(
    analysis_results: List[Dict[str, Any]],
    report_format: str = "summary"
) -> str:
    """
    Generate a formatted report from analysis results.
    
    Args:
        analysis_results (List[Dict[str, Any]]): List of analysis results
        report_format (str): Format of the report ('summary', 'detailed', 'json')
        
    Returns:
        str: Formatted report
    """
    
    if not analysis_results:
        return "No analysis results to report."
    
    if report_format == "json":
        return json.dumps(analysis_results, indent=2, default=str)
    
    report = []
    report.append("# AI Analysis Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Documents Analyzed: {len(analysis_results)}")
    report.append("")
    
    for i, result in enumerate(analysis_results, 1):
        doc_name = result.get('document_name', f'Document {i}')
        report.append(f"## {doc_name}")
        
        if result.get('success'):
            response = result.get('response', {})
            
            if report_format == "summary":
                report.append(f"**Summary**: {response.get('summary', 'N/A')}")
                report.append(f"**Score**: {response.get('overall_score', response.get('quality_score', response.get('compliance_score', 'N/A')))}")
                
            elif report_format == "detailed":
                for key, value in response.items():
                    if isinstance(value, list):
                        report.append(f"**{key.title()}**:")
                        for item in value:
                            report.append(f"- {item}")
                    else:
                        report.append(f"**{key.title()}**: {value}")
        else:
            report.append(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
        
        report.append("")
    
    return "\n".join(report)

def save_analysis_results(
    results: List[Dict[str, Any]],
    session: Session,
    table_name: str = "AI_ANALYSIS_RESULTS"
) -> bool:
    """
    Save analysis results to Snowflake table.
    
    Args:
        results (List[Dict[str, Any]]): Analysis results to save
        session (Session): Snowflake session
        table_name (str): Target table name
        
    Returns:
        bool: True if successful, False otherwise
    """
    
    try:
        # Create table if it doesn't exist
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            analysis_id VARCHAR(50),
            document_name VARCHAR(500),
            analysis_type VARCHAR(100),
            model_used VARCHAR(100),
            timestamp TIMESTAMP,
            content_length NUMBER,
            success BOOLEAN,
            response VARIANT,
            error_message VARCHAR(1000)
        )
        """
        
        session.sql(create_table_sql).collect()
        
        # Insert results
        for result in results:
            insert_sql = f"""
            INSERT INTO {table_name} (
                analysis_id, document_name, analysis_type, model_used,
                timestamp, content_length, success, response, error_message
            ) VALUES (
                '{result.get('analysis_id', 'N/A')}',
                '{result.get('document_name', 'N/A')}',
                '{result.get('analysis_type', 'N/A')}',
                '{result.get('model_used', 'N/A')}',
                '{result.get('timestamp', datetime.now().isoformat())}',
                {result.get('content_length', 0)},
                {result.get('success', False)},
                PARSE_JSON('{json.dumps(result.get('response', {}), default=str)}'),
                '{result.get('error', '')}'
            )
            """
            
            session.sql(insert_sql).collect()
        
        st.success(f"✅ Saved {len(results)} analysis results to {table_name}")
        return True
        
    except Exception as e:
        st.error(f"❌ Failed to save results: {str(e)}")
        return False

def get_model_recommendations(analysis_type: str, content_length: int) -> str:
    """
    Get model recommendations based on analysis type and content length.
    
    Args:
        analysis_type (str): Type of analysis
        content_length (int): Length of content to analyze
        
    Returns:
        str: Recommended model name
    """
    
    # For very long content, use models with higher token limits
    if content_length > 6000:
        return 'mistral-large'  # Highest token limit
    
    # For quick analysis, use faster models
    if analysis_type in ['extraction', 'quick']:
        return 'reka-flash'
    
    # For complex analysis, use powerful models
    if analysis_type in ['compliance', 'quality', 'detailed']:
        return 'mistral-large'
    
    # For general use, balanced model
    return 'mixtral-8x7b'

# UI Helper Functions

def create_model_selector() -> str:
    """
    Create Streamlit widget for model selection.
    
    Returns:
        str: Selected model name
    """
    
    st.subheader("🤖 AI Model Selection")
    
    # Model selection
    selected_model = st.selectbox(
        "Choose AI Model:",
        list(CORTEX_MODELS.keys()),
        index=list(CORTEX_MODELS.keys()).index(DEFAULT_MODEL)
    )
    
    # Display model information
    model_info = CORTEX_MODELS[selected_model]
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Description**: {model_info['description']}")
    with col2:
        st.info(f"**Max Tokens**: {model_info['max_tokens']:,}")
    
    st.info(f"**Recommended Use**: {model_info['recommended_use']}")
    
    return selected_model

def create_analysis_type_selector() -> str:
    """
    Create Streamlit widget for analysis type selection.
    
    Returns:
        str: Selected analysis type
    """
    
    analysis_types = {
        "general": "📋 General Analysis - Comprehensive document review",
        "compliance": "⚖️ Compliance Review - Regulatory and legal assessment",
        "quality": "✅ Quality Assessment - Completeness and accuracy check",
        "extraction": "📊 Information Extraction - Key data and entities"
    }
    
    st.subheader("📝 Analysis Type")
    
    selected_type = st.selectbox(
        "Choose Analysis Type:",
        list(analysis_types.keys()),
        format_func=lambda x: analysis_types[x]
    )
    
    return selected_type

def display_analysis_results(results: Dict[str, Any]):
    """
    Display analysis results in Streamlit interface.
    
    Args:
        results (Dict[str, Any]): Analysis results to display
    """
    
    if not results.get('success', False):
        st.error(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
        return
    
    response = results.get('response', {})
    
    # Display metadata
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Model Used", results.get('model_used', 'N/A'))
    with col2:
        st.metric("Analysis Type", results.get('analysis_type', 'N/A'))
    with col3:
        st.metric("Content Length", f"{results.get('content_length', 0):,} chars")
    
    # Display main results
    if isinstance(response, dict):
        for key, value in response.items():
            if key in ['summary', 'analysis']:
                st.subheader(f"📋 {key.title()}")
                st.write(value)
                
            elif isinstance(value, list) and value:
                st.subheader(f"📝 {key.replace('_', ' ').title()}")
                for item in value:
                    st.write(f"• {item}")
                    
            elif key in ['overall_score', 'quality_score', 'compliance_score']:
                st.subheader(f"📊 {key.replace('_', ' ').title()}")
                try:
                    score = float(value) if isinstance(value, str) else value
                    st.progress(score / 10.0)
                    st.write(f"Score: {score}/10")
                except:
                    st.write(value)
                    
            elif value and key not in ['timestamp']:
                st.subheader(f"ℹ️ {key.replace('_', ' ').title()}")
                st.write(value)
    else:
        st.subheader("📋 Analysis Results")
        st.write(response)
    
    # Display timestamp
    if results.get('timestamp'):
        st.caption(f"Analysis completed: {results['timestamp']}")