""""""

AI Analysis Utilities - Snowflake Cortex AI IntegrationAI Analysis Utilities



Handles AI-powered document analysis using Snowflake Cortex AI models.Handles AI-powered document analysis and feedback generation using various AI providers.

""""""



import jsonimport json

import streamlit as stimport requests

from datetime import datetimeimport streamlit as st

from typing import Dict, List, Optional, Anyfrom datetime import datetime

from snowflake.snowpark import Sessionfrom typing import Dict, List, Optional, Any



# Cortex AI Model Configuration# AI Provider Configuration

CORTEX_MODELS = {SUPPORTED_PROVIDERS = {

    'mistral-large': {    'openai': {

        'description': 'Large multilingual model, best for complex analysis',        'base_url': 'https://api.openai.com/v1',

        'max_tokens': 8000,        'default_model': 'gpt-4',

        'recommended_use': 'Complex document analysis, detailed reviews'        'env_key': 'OPENAI_API_KEY'

    },    },

    'llama2-70b-chat': {    'anthropic': {

        'description': 'Meta Llama 2 70B chat model',        'base_url': 'https://api.anthropic.com/v1',

        'max_tokens': 4000,        'default_model': 'claude-3-sonnet-20240229',

        'recommended_use': 'Conversational analysis, Q&A'        'env_key': 'ANTHROPIC_API_KEY'

    },    },

    'reka-flash': {    'azure': {

        'description': 'Fast and efficient model for quick analysis',        'base_url': None,  # Set via environment

        'max_tokens': 2000,        'default_model': 'gpt-4',

        'recommended_use': 'Quick summaries, simple analysis'        'env_key': 'AZURE_OPENAI_API_KEY'

    },    }

    'mixtral-8x7b': {}

        'description': 'Mixture of experts model for specialized tasks',

        'max_tokens': 4000,def get_ai_provider_config(provider='openai'):

        'recommended_use': 'Specialized analysis, technical documents'    """

    }    Get configuration for AI provider.

}    

    Args:

def get_snowflake_session():        provider (str): AI provider name

    """        

    Get Snowflake session for Cortex AI operations.    Returns:

    Uses the same session configuration as other Snowflake utilities.        dict: Provider configuration

    """    """

    try:    

        # Import from project's Snowflake utils    if provider not in SUPPORTED_PROVIDERS:

        from utils.snowflake_utils import get_snowflake_session        raise ValueError(f"Unsupported provider: {provider}. Supported: {list(SUPPORTED_PROVIDERS.keys())}")

        return get_snowflake_session()    

    except ImportError:    config = SUPPORTED_PROVIDERS[provider].copy()

        # Fallback if direct import fails    

        if 'snowflake_session' in st.session_state:    # Get API key from environment or Streamlit secrets

            return st.session_state.snowflake_session    api_key = None

        else:    env_key = config['env_key']

            st.error("Snowflake session not available. Please check connection.")    

            return None    # Try Streamlit secrets first

    if hasattr(st, 'secrets') and env_key.lower() in st.secrets:

def test_cortex_connection():        api_key = st.secrets[env_key.lower()]

    """    

    Test connection to Snowflake Cortex AI.    # Fallback to environment variable

        if not api_key:

    Returns:        import os

        dict: Test results        api_key = os.getenv(env_key)

    """    

    try:    config['api_key'] = api_key

        session = get_snowflake_session()    config['available'] = bool(api_key)

        if not session:    

            return {    return config

                'success': False,

                'error': 'Unable to get Snowflake session'def analyze_document_content(text_content, analysis_type="general", provider="openai", custom_prompt=None):

            }    """

            Analyze document content using AI.

        # Test with simple Cortex AI call    

        test_query = "SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large', 'Hello, this is a test. Please respond with: Test successful.') as test_response"    Args:

                text_content (str): Document text to analyze

        result = session.sql(test_query).collect()        analysis_type (str): Type of analysis ('general', 'compliance', 'summary', 'quality')

                provider (str): AI provider to use

        if result and len(result) > 0:        custom_prompt (str): Custom analysis prompt

            response = result[0]['TEST_RESPONSE']        

            return {    Returns:

                'success': True,        dict: Analysis results

                'response': response,    """

                'models_available': list(CORTEX_MODELS.keys())    

            }    try:

        else:        # Get provider configuration

            return {        config = get_ai_provider_config(provider)

                'success': False,        

                'error': 'No response from Cortex AI'        if not config['available']:

            }            return {

                            'success': False,

    except Exception as e:                'error': f'API key not available for {provider}',

        return {                'analysis': None

            'success': False,            }

            'error': f'Cortex AI connection test failed: {str(e)}'        

        }        # Select analysis prompt

        if custom_prompt:

def analyze_document_content(text_content, analysis_type="general", model="mistral-large", custom_prompt=None):            prompt = custom_prompt

    """        else:

    Analyze document content using Snowflake Cortex AI.            prompt = get_analysis_prompt(analysis_type)

            

    Args:        # Prepare the full prompt

        text_content (str): Document text to analyze        full_prompt = f"{prompt}\n\nDocument Content:\n{text_content}"

        analysis_type (str): Type of analysis ('general', 'compliance', 'summary', 'quality')        

        model (str): Cortex AI model to use        # Make API call based on provider

        custom_prompt (str): Custom analysis prompt        if provider == 'openai':

                    result = call_openai_api(config, full_prompt)

    Returns:        elif provider == 'anthropic':

        dict: Analysis results            result = call_anthropic_api(config, full_prompt)

    """        elif provider == 'azure':

                result = call_azure_api(config, full_prompt)

    try:        else:

        # Get Snowflake session            return {

        session = get_snowflake_session()                'success': False,

        if not session:                'error': f'Provider {provider} not implemented',

            return {                'analysis': None

                'success': False,            }

                'error': 'Snowflake session not available',        

                'analysis': None        if result['success']:

            }            # Parse structured response if possible

                    analysis_text = result['content']

        # Validate model            structured_analysis = parse_analysis_response(analysis_text, analysis_type)

        if model not in CORTEX_MODELS:            

            model = 'mistral-large'  # Default fallback            return {

                        'success': True,

        # Select analysis prompt                'analysis': structured_analysis,

        if custom_prompt:                'raw_response': analysis_text,

            prompt = custom_prompt                'metadata': {

        else:                    'provider': provider,

            prompt = get_analysis_prompt(analysis_type)                    'model': config['default_model'],

                            'analysis_type': analysis_type,

        # Prepare the full prompt                    'timestamp': datetime.now().isoformat(),

        full_prompt = f"{prompt}\n\nDocument Content:\n{text_content}"                    'input_length': len(text_content),

                            'output_length': len(analysis_text)

        # Truncate if too long for model                }

        max_chars = CORTEX_MODELS[model]['max_tokens'] * 3  # Rough estimate            }

        if len(full_prompt) > max_chars:        else:

            # Keep prompt and truncate document content            return {

            prompt_length = len(prompt) + 50                'success': False,

            available_length = max_chars - prompt_length                'error': result['error'],

            truncated_content = text_content[:available_length] + "\n\n[Document truncated for analysis]"                'analysis': None

            full_prompt = f"{prompt}\n\nDocument Content:\n{truncated_content}"            }

                    

        # Escape single quotes for SQL    except Exception as e:

        escaped_prompt = full_prompt.replace("'", "''")        return {

                    'success': False,

        # Call Cortex AI            'error': f'Analysis failed: {str(e)}',

        cortex_query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}') as analysis_result"            'analysis': None

                }

        result = session.sql(cortex_query).collect()

        def get_analysis_prompt(analysis_type):

        if result and len(result) > 0:    """

            analysis_text = result[0]['ANALYSIS_RESULT']    Get analysis prompt template based on type.

                

            # Parse structured response    Args:

            structured_analysis = parse_analysis_response(analysis_text, analysis_type)        analysis_type (str): Type of analysis

                    

            return {    Returns:

                'success': True,        str: Analysis prompt

                'analysis': structured_analysis,    """

                'raw_response': analysis_text,    

                'metadata': {    prompts = {

                    'provider': 'snowflake-cortex',        'general': """

                    'model': model,        Please analyze this document and provide a comprehensive review including:

                    'analysis_type': analysis_type,        1. Document summary and purpose

                    'timestamp': datetime.now().isoformat(),        2. Key findings or important information

                    'input_length': len(text_content),        3. Potential issues or concerns

                    'output_length': len(analysis_text),        4. Recommendations for improvement

                    'truncated': len(full_prompt) > max_chars        5. Overall assessment

                }        

            }        Structure your response with clear sections and bullet points where appropriate.

        else:        """,

            return {        

                'success': False,        'compliance': """

                'error': 'No response from Cortex AI',        Please analyze this document for compliance and regulatory considerations:

                'analysis': None        1. Identify any compliance requirements mentioned

            }        2. Check for missing required information

                    3. Assess completeness of required sections

    except Exception as e:        4. Flag potential compliance risks

        error_msg = str(e)        5. Provide recommendations for compliance improvements

                

        # Handle common Cortex AI errors        Focus on accuracy, completeness, and regulatory adherence.

        if "CORTEX" in error_msg.upper():        """,

            if "not found" in error_msg.lower():        

                error_msg = "Cortex AI not available in this Snowflake account. Please enable Cortex AI features."        'summary': """

            elif "permission" in error_msg.lower():        Please provide a concise summary of this document including:

                error_msg = "Insufficient permissions for Cortex AI. Please grant USAGE on CORTEX functions."        1. Main purpose and objective

                2. Key points and findings (3-5 bullet points)

        return {        3. Important dates, numbers, or references

            'success': False,        4. Action items or next steps (if any)

            'error': f'Analysis failed: {error_msg}',        5. Overall conclusion

            'analysis': None        

        }        Keep the summary focused and actionable.

        """,

def get_analysis_prompt(analysis_type):        

    """        'quality': """

    Get analysis prompt template based on type.        Please assess the quality of this document considering:

            1. Clarity and readability

    Args:        2. Organization and structure

        analysis_type (str): Type of analysis        3. Completeness of information

                4. Accuracy and consistency

    Returns:        5. Professional presentation

        str: Analysis prompt        6. Suggestions for improvement

    """        

            Provide specific feedback on strengths and areas for improvement.

    prompts = {        """,

        'general': """        

        Please analyze this document and provide a comprehensive review including:        'forms_review': """

        1. Document summary and purpose        Please review this form document with focus on:

        2. Key findings or important information        1. Form completeness and required fields

        3. Potential issues or concerns        2. Data accuracy and consistency

        4. Recommendations for improvement        3. Compliance with regulations or standards

        5. Overall assessment        4. Missing information or incomplete sections

                5. Recommendations for corrections or improvements

        Structure your response with clear sections and bullet points where appropriate.        

        """,        Provide actionable feedback for form improvement and compliance.

                """

        'compliance': """    }

        Please analyze this document for compliance and regulatory considerations:    

        1. Identify any compliance requirements mentioned    return prompts.get(analysis_type, prompts['general'])

        2. Check for missing required information

        3. Assess completeness of required sectionsdef call_openai_api(config, prompt):

        4. Flag potential compliance risks    """

        5. Provide recommendations for compliance improvements    Make API call to OpenAI.

            

        Focus on accuracy, completeness, and regulatory adherence.    Args:

        """,        config (dict): Provider configuration

                prompt (str): Analysis prompt

        'summary': """        

        Please provide a concise summary of this document including:    Returns:

        1. Main purpose and objective        dict: API response

        2. Key points and findings (3-5 bullet points)    """

        3. Important dates, numbers, or references    

        4. Action items or next steps (if any)    try:

        5. Overall conclusion        headers = {

                    'Authorization': f"Bearer {config['api_key']}",

        Keep the summary focused and actionable.            'Content-Type': 'application/json'

        """,        }

                

        'quality': """        data = {

        Please assess the quality of this document considering:            'model': config['default_model'],

        1. Clarity and readability            'messages': [

        2. Organization and structure                {'role': 'system', 'content': 'You are an expert document analyst. Provide detailed, structured analysis.'},

        3. Completeness of information                {'role': 'user', 'content': prompt}

        4. Accuracy and consistency            ],

        5. Professional presentation            'max_tokens': 2000,

        6. Suggestions for improvement            'temperature': 0.3

                }

        Provide specific feedback on strengths and areas for improvement.        

        """,        response = requests.post(

                    f"{config['base_url']}/chat/completions",

        'forms_review': """            headers=headers,

        Please review this form document with focus on:            json=data,

        1. Form completeness and required fields            timeout=60

        2. Data accuracy and consistency        )

        3. Compliance with regulations or standards        

        4. Missing information or incomplete sections        if response.status_code == 200:

        5. Recommendations for corrections or improvements            result = response.json()

                    return {

        Provide actionable feedback for form improvement and compliance.                'success': True,

        """                'content': result['choices'][0]['message']['content'],

    }                'usage': result.get('usage', {})

                }

    return prompts.get(analysis_type, prompts['general'])        else:

            return {

def get_available_models():                'success': False,

    """                'error': f'API call failed: {response.status_code} - {response.text}'

    Get list of available Cortex AI models.            }

                

    Returns:    except Exception as e:

        dict: Available models with descriptions        return {

    """            'success': False,

                'error': f'OpenAI API call failed: {str(e)}'

    try:        }

        session = get_snowflake_session()

        if not session:def call_anthropic_api(config, prompt):

            return CORTEX_MODELS  # Return default list    """

            Make API call to Anthropic Claude.

        # Try to get actual available models from Snowflake    

        try:    Args:

            # This query checks if Cortex functions are available        config (dict): Provider configuration

            test_query = "SHOW FUNCTIONS LIKE 'SNOWFLAKE.CORTEX.%'"        prompt (str): Analysis prompt

            result = session.sql(test_query).collect()        

                Returns:

            # If Cortex is available, return our model list        dict: API response

            if result:    """

                return CORTEX_MODELS    

            else:    try:

                return {}        headers = {

                            'x-api-key': config['api_key'],

        except Exception:            'Content-Type': 'application/json',

            # If query fails, return default models            'anthropic-version': '2023-06-01'

            return CORTEX_MODELS        }

                    

    except Exception:        data = {

        return CORTEX_MODELS            'model': config['default_model'],

            'max_tokens': 2000,

def parse_analysis_response(response_text, analysis_type):            'messages': [

    """                {'role': 'user', 'content': prompt}

    Parse AI response into structured format.            ]

            }

    Args:        

        response_text (str): Raw AI response        response = requests.post(

        analysis_type (str): Type of analysis            f"{config['base_url']}/messages",

                    headers=headers,

    Returns:            json=data,

        dict: Structured analysis results            timeout=60

    """        )

            

    try:        if response.status_code == 200:

        # Try to identify sections in the response            result = response.json()

        sections = {}            return {

        current_section = "overview"                'success': True,

        current_content = []                'content': result['content'][0]['text'],

                        'usage': result.get('usage', {})

        lines = response_text.split('\n')            }

                else:

        for line in lines:            return {

            line = line.strip()                'success': False,

            if not line:                'error': f'API call failed: {response.status_code} - {response.text}'

                continue            }

                            

            # Check if line is a section header (starts with number or bullet)    except Exception as e:

            if any(line.startswith(prefix) for prefix in ['1.', '2.', '3.', '4.', '5.', '##', '**']):        return {

                # Save previous section            'success': False,

                if current_content:            'error': f'Anthropic API call failed: {str(e)}'

                    sections[current_section] = '\n'.join(current_content)        }

                

                # Start new sectiondef call_azure_api(config, prompt):

                current_section = line.lower().replace('.', '').replace('#', '').replace('*', '').strip()    """

                current_content = [line]    Make API call to Azure OpenAI.

            else:    

                current_content.append(line)    Args:

                config (dict): Provider configuration

        # Save last section        prompt (str): Analysis prompt

        if current_content:        

            sections[current_section] = '\n'.join(current_content)    Returns:

                dict: API response

        # Create structured result    """

        structured = {    

            'raw_text': response_text,    try:

            'sections': sections,        # Azure requires additional configuration

            'analysis_type': analysis_type        azure_endpoint = st.secrets.get('azure_openai_endpoint') or os.getenv('AZURE_OPENAI_ENDPOINT')

        }        deployment_name = st.secrets.get('azure_deployment_name') or os.getenv('AZURE_DEPLOYMENT_NAME')

                api_version = st.secrets.get('azure_api_version', '2023-12-01-preview')

        # Add specific parsing for different analysis types        

        if analysis_type == 'summary':        if not azure_endpoint or not deployment_name:

            structured['key_points'] = extract_bullet_points(response_text)            return {

        elif analysis_type == 'compliance':                'success': False,

            structured['compliance_issues'] = extract_compliance_issues(response_text)                'error': 'Azure endpoint or deployment name not configured'

        elif analysis_type == 'quality':            }

            structured['recommendations'] = extract_recommendations(response_text)        

                headers = {

        return structured            'api-key': config['api_key'],

                    'Content-Type': 'application/json'

    except Exception as e:        }

        # Fallback to simple structure        

        return {        data = {

            'raw_text': response_text,            'messages': [

            'sections': {'analysis': response_text},                {'role': 'system', 'content': 'You are an expert document analyst. Provide detailed, structured analysis.'},

            'analysis_type': analysis_type,                {'role': 'user', 'content': prompt}

            'parsing_error': str(e)            ],

        }            'max_tokens': 2000,

            'temperature': 0.3

def extract_bullet_points(text):        }

    """Extract bullet points from text."""        

    bullet_points = []        url = f"{azure_endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"

    lines = text.split('\n')        

            response = requests.post(url, headers=headers, json=data, timeout=60)

    for line in lines:        

        line = line.strip()        if response.status_code == 200:

        if line.startswith(('•', '-', '*', '▪')) or (line and line[0].isdigit() and '.' in line):            result = response.json()

            bullet_points.append(line)            return {

                    'success': True,

    return bullet_points                'content': result['choices'][0]['message']['content'],

                'usage': result.get('usage', {})

def extract_compliance_issues(text):            }

    """Extract compliance-related issues from text."""        else:

    issues = []            return {

    lines = text.split('\n')                'success': False,

                    'error': f'API call failed: {response.status_code} - {response.text}'

    keywords = ['missing', 'required', 'incomplete', 'compliance', 'violation', 'risk']            }

                

    for line in lines:    except Exception as e:

        line_lower = line.lower()        return {

        if any(keyword in line_lower for keyword in keywords):            'success': False,

            issues.append(line.strip())            'error': f'Azure API call failed: {str(e)}'

            }

    return issues

def parse_analysis_response(response_text, analysis_type):

def extract_recommendations(text):    """

    """Extract recommendations from text."""    Parse AI response into structured format.

    recommendations = []    

    lines = text.split('\n')    Args:

            response_text (str): Raw AI response

    keywords = ['recommend', 'suggest', 'should', 'improve', 'consider', 'advice']        analysis_type (str): Type of analysis

            

    for line in lines:    Returns:

        line_lower = line.lower()        dict: Structured analysis results

        if any(keyword in line_lower for keyword in keywords):    """

            recommendations.append(line.strip())    

        try:

    return recommendations        # Try to identify sections in the response

        sections = {}

def generate_analysis_summary(analysis_results):        current_section = "overview"

    """        current_content = []

    Generate a concise summary from detailed analysis results.        

            lines = response_text.split('\n')

    Args:        

        analysis_results (dict): Full analysis results        for line in lines:

                    line = line.strip()

    Returns:            if not line:

        dict: Summary information                continue

    """                

                # Check if line is a section header (starts with number or bullet)

    try:            if any(line.startswith(prefix) for prefix in ['1.', '2.', '3.', '4.', '5.', '##', '**']):

        if not analysis_results.get('success') or not analysis_results.get('analysis'):                # Save previous section

            return {                if current_content:

                'success': False,                    sections[current_section] = '\n'.join(current_content)

                'error': 'No analysis results to summarize'                

            }                # Start new section

                        current_section = line.lower().replace('.', '').replace('#', '').replace('*', '').strip()

        analysis = analysis_results['analysis']                current_content = [line]

        metadata = analysis_results.get('metadata', {})            else:

                        current_content.append(line)

        # Extract key information        

        summary = {        # Save last section

            'analysis_type': metadata.get('analysis_type', 'general'),        if current_content:

            'provider': metadata.get('provider', 'snowflake-cortex'),            sections[current_section] = '\n'.join(current_content)

            'model': metadata.get('model', 'mistral-large'),        

            'timestamp': metadata.get('timestamp'),        # Create structured result

            'document_length': metadata.get('input_length', 0),        structured = {

            'response_length': metadata.get('output_length', 0),            'raw_text': response_text,

            'truncated': metadata.get('truncated', False)            'sections': sections,

        }            'analysis_type': analysis_type

                }

        # Get first few sentences as overview        

        raw_text = analysis.get('raw_text', '')        # Add specific parsing for different analysis types

        sentences = raw_text.split('. ')        if analysis_type == 'summary':

        summary['overview'] = '. '.join(sentences[:2]) + '.' if sentences else 'No summary available'            structured['key_points'] = extract_bullet_points(response_text)

                elif analysis_type == 'compliance':

        # Count sections            structured['compliance_issues'] = extract_compliance_issues(response_text)

        sections = analysis.get('sections', {})        elif analysis_type == 'quality':

        summary['sections_count'] = len(sections)            structured['recommendations'] = extract_recommendations(response_text)

        summary['sections'] = list(sections.keys())        

                return structured

        # Extract specific items based on analysis type        

        if analysis.get('key_points'):    except Exception as e:

            summary['key_points_count'] = len(analysis['key_points'])        # Fallback to simple structure

                return {

        if analysis.get('compliance_issues'):            'raw_text': response_text,

            summary['compliance_issues_count'] = len(analysis['compliance_issues'])            'sections': {'analysis': response_text},

                    'analysis_type': analysis_type,

        if analysis.get('recommendations'):            'parsing_error': str(e)

            summary['recommendations_count'] = len(analysis['recommendations'])        }

        

        return {def extract_bullet_points(text):

            'success': True,    """Extract bullet points from text."""

            'summary': summary    bullet_points = []

        }    lines = text.split('\n')

            

    except Exception as e:    for line in lines:

        return {        line = line.strip()

            'success': False,        if line.startswith(('•', '-', '*', '▪')) or (line and line[0].isdigit() and '.' in line):

            'error': f'Summary generation failed: {str(e)}'            bullet_points.append(line)

        }    

    return bullet_points

def batch_analyze_documents(documents, analysis_type="general", model="mistral-large"):

    """def extract_compliance_issues(text):

    Analyze multiple documents in batch using Cortex AI.    """Extract compliance-related issues from text."""

        issues = []

    Args:    lines = text.split('\n')

        documents (list): List of document texts    

        analysis_type (str): Type of analysis    keywords = ['missing', 'required', 'incomplete', 'compliance', 'violation', 'risk']

        model (str): Cortex AI model to use    

            for line in lines:

    Returns:        line_lower = line.lower()

        dict: Batch analysis results        if any(keyword in line_lower for keyword in keywords):

    """            issues.append(line.strip())

        

    try:    return issues

        results = []

        failed_analyses = []def extract_recommendations(text):

            """Extract recommendations from text."""

        # Create progress tracking    recommendations = []

        total_docs = len(documents)    lines = text.split('\n')

        if 'st' in globals():    

            progress_bar = st.progress(0)    keywords = ['recommend', 'suggest', 'should', 'improve', 'consider', 'advice']

            status_text = st.empty()    

        else:    for line in lines:

            progress_bar = None        line_lower = line.lower()

            status_text = None        if any(keyword in line_lower for keyword in keywords):

                    recommendations.append(line.strip())

        for i, doc_text in enumerate(documents):    

            try:    return recommendations

                # Update progress

                if progress_bar:def generate_analysis_summary(analysis_results):

                    progress_bar.progress((i + 1) / total_docs)    """

                if status_text:    Generate a concise summary from detailed analysis results.

                    status_text.text(f"Analyzing document {i+1}/{total_docs} with {model}")    

                    Args:

                # Analyze document        analysis_results (dict): Full analysis results

                result = analyze_document_content(doc_text, analysis_type, model)        

                    Returns:

                if result['success']:        dict: Summary information

                    result['document_index'] = i    """

                    results.append(result)    

                else:    try:

                    failed_analyses.append({        if not analysis_results.get('success') or not analysis_results.get('analysis'):

                        'document_index': i,            return {

                        'error': result['error']                'success': False,

                    })                'error': 'No analysis results to summarize'

                                }

            except Exception as e:        

                failed_analyses.append({        analysis = analysis_results['analysis']

                    'document_index': i,        metadata = analysis_results.get('metadata', {})

                    'error': str(e)        

                })        # Extract key information

                summary = {

        # Clear progress indicators            'analysis_type': metadata.get('analysis_type', 'general'),

        if progress_bar:            'provider': metadata.get('provider', 'unknown'),

            progress_bar.empty()            'timestamp': metadata.get('timestamp'),

        if status_text:            'document_length': metadata.get('input_length', 0),

            status_text.empty()            'response_length': metadata.get('output_length', 0)

                }

        return {        

            'success': True,        # Get first few sentences as overview

            'total_documents': total_docs,        raw_text = analysis.get('raw_text', '')

            'successful_analyses': len(results),        sentences = raw_text.split('. ')

            'failed_analyses': len(failed_analyses),        summary['overview'] = '. '.join(sentences[:2]) + '.' if sentences else 'No summary available'

            'results': results,        

            'failures': failed_analyses,        # Count sections

            'analysis_type': analysis_type,        sections = analysis.get('sections', {})

            'model': model,        summary['sections_count'] = len(sections)

            'provider': 'snowflake-cortex'        summary['sections'] = list(sections.keys())

        }        

                # Extract specific items based on analysis type

    except Exception as e:        if analysis.get('key_points'):

        return {            summary['key_points_count'] = len(analysis['key_points'])

            'success': False,        

            'error': f'Batch analysis failed: {str(e)}'        if analysis.get('compliance_issues'):

        }            summary['compliance_issues_count'] = len(analysis['compliance_issues'])

        

def save_analysis_results(analysis_results, file_name=None):        if analysis.get('recommendations'):

    """            summary['recommendations_count'] = len(analysis['recommendations'])

    Save analysis results to file or session state.        

            return {

    Args:            'success': True,

        analysis_results (dict): Analysis results to save            'summary': summary

        file_name (str): Optional file name for saving        }

                

    Returns:    except Exception as e:

        dict: Save operation results        return {

    """            'success': False,

                'error': f'Summary generation failed: {str(e)}'

    try:        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        def batch_analyze_documents(documents, analysis_type="general", provider="openai"):

        if not file_name:    """

            file_name = f"cortex_analysis_{timestamp}.json"    Analyze multiple documents in batch.

            

        # Prepare data for saving    Args:

        save_data = {        documents (list): List of document texts

            'timestamp': datetime.now().isoformat(),        analysis_type (str): Type of analysis

            'analysis_results': analysis_results,        provider (str): AI provider

            'file_name': file_name,        

            'provider': 'snowflake-cortex'    Returns:

        }        dict: Batch analysis results

            """

        # Save to session state if available    

        if 'st' in globals() and hasattr(st, 'session_state'):    try:

            if 'saved_analyses' not in st.session_state:        results = []

                st.session_state.saved_analyses = {}        failed_analyses = []

                    

            st.session_state.saved_analyses[file_name] = save_data        # Create progress tracking

                total_docs = len(documents)

        # Create downloadable JSON        progress_bar = st.progress(0) if 'st' in globals() else None

        json_str = json.dumps(save_data, indent=2, default=str)        status_text = st.empty() if 'st' in globals() else None

                

        return {        for i, doc_text in enumerate(documents):

            'success': True,            try:

            'file_name': file_name,                # Update progress

            'json_content': json_str,                if progress_bar:

            'size': len(json_str)                    progress_bar.progress((i + 1) / total_docs)

        }                if status_text:

                            status_text.text(f"Analyzing document {i+1}/{total_docs}")

    except Exception as e:                

        return {                # Analyze document

            'success': False,                result = analyze_document_content(doc_text, analysis_type, provider)

            'error': f'Save failed: {str(e)}'                

        }                if result['success']:

                    result['document_index'] = i

def get_cortex_model_info(model_name):                    results.append(result)

    """                else:

    Get information about a specific Cortex AI model.                    failed_analyses.append({

                            'document_index': i,

    Args:                        'error': result['error']

        model_name (str): Name of the model                    })

                            

    Returns:            except Exception as e:

        dict: Model information                failed_analyses.append({

    """                    'document_index': i,

                        'error': str(e)

    return CORTEX_MODELS.get(model_name, {                })

        'description': 'Unknown model',        

        'max_tokens': 2000,        # Clear progress indicators

        'recommended_use': 'General analysis'        if progress_bar:

    })            progress_bar.empty()
        if status_text:
            status_text.empty()
        
        return {
            'success': True,
            'total_documents': total_docs,
            'successful_analyses': len(results),
            'failed_analyses': len(failed_analyses),
            'results': results,
            'failures': failed_analyses,
            'analysis_type': analysis_type,
            'provider': provider
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Batch analysis failed: {str(e)}'
        }

def save_analysis_results(analysis_results, file_name=None):
    """
    Save analysis results to file or session state.
    
    Args:
        analysis_results (dict): Analysis results to save
        file_name (str): Optional file name for saving
        
    Returns:
        dict: Save operation results
    """
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not file_name:
            file_name = f"analysis_results_{timestamp}.json"
        
        # Prepare data for saving
        save_data = {
            'timestamp': datetime.now().isoformat(),
            'analysis_results': analysis_results,
            'file_name': file_name
        }
        
        # Save to session state if available
        if 'st' in globals() and hasattr(st, 'session_state'):
            if 'saved_analyses' not in st.session_state:
                st.session_state.saved_analyses = {}
            
            st.session_state.saved_analyses[file_name] = save_data
        
        # Create downloadable JSON
        json_str = json.dumps(save_data, indent=2, default=str)
        
        return {
            'success': True,
            'file_name': file_name,
            'json_content': json_str,
            'size': len(json_str)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Save failed: {str(e)}'
        }