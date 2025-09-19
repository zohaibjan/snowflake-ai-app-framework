"""
PDF Processing Utilities

Handles PDF file processing for text extraction, page analysis, and document validation.
"""

import io
import tempfile
import streamlit as st
from pathlib import Path

# Handle PyPDF2 import with fallback
try:
    import PyPDF2
    PDF_LIBRARY = "PyPDF2"
except ImportError:
    try:
        import pypdf
        import pypdf as PyPDF2  # Alias for compatibility
        PDF_LIBRARY = "pypdf"
    except ImportError:
        PDF_LIBRARY = None

def extract_text_from_pdf(uploaded_file):
    """
    Extract text content from a PDF file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object or file path
        
    Returns:
        dict: Extraction results with text content and metadata
    """
    
    if PDF_LIBRARY is None:
        raise ImportError("PDF processing library not available. Install PyPDF2 or pypdf.")
    
    try:
        # Handle different input types
        if hasattr(uploaded_file, 'read'):
            # Streamlit UploadedFile
            pdf_bytes = uploaded_file.read()
            file_name = getattr(uploaded_file, 'name', 'unknown.pdf')
            # Reset file pointer for potential reuse
            if hasattr(uploaded_file, 'seek'):
                uploaded_file.seek(0)
        elif isinstance(uploaded_file, (str, Path)):
            # File path
            with open(uploaded_file, 'rb') as f:
                pdf_bytes = f.read()
            file_name = Path(uploaded_file).name
        else:
            # Assume bytes
            pdf_bytes = uploaded_file
            file_name = 'unknown.pdf'
        
        # Create PDF reader
        pdf_stream = io.BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_stream)
        
        # Extract metadata
        metadata = {
            'num_pages': len(pdf_reader.pages),
            'file_name': file_name,
            'file_size': len(pdf_bytes),
            'encrypted': pdf_reader.is_encrypted
        }
        
        # Handle encrypted PDFs
        if pdf_reader.is_encrypted:
            return {
                'success': False,
                'error': 'PDF is password protected',
                'metadata': metadata,
                'text': '',
                'pages': []
            }
        
        # Extract text from each page
        pages = []
        full_text = ""
        
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                pages.append({
                    'page_number': page_num + 1,
                    'text': page_text,
                    'char_count': len(page_text),
                    'word_count': len(page_text.split())
                })
                full_text += page_text + "\n"
                
            except Exception as page_error:
                pages.append({
                    'page_number': page_num + 1,
                    'text': '',
                    'char_count': 0,
                    'word_count': 0,
                    'error': str(page_error)
                })
        
        # Add text statistics to metadata
        metadata.update({
            'total_chars': len(full_text),
            'total_words': len(full_text.split()),
            'extractable_pages': len([p for p in pages if p.get('text')])
        })
        
        return {
            'success': True,
            'text': full_text.strip(),
            'pages': pages,
            'metadata': metadata,
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"PDF processing failed: {str(e)}",
            'text': '',
            'pages': [],
            'metadata': {'file_name': file_name if 'file_name' in locals() else 'unknown.pdf'}
        }

def validate_pdf_file(uploaded_file):
    """
    Validate that a file is a valid PDF.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        dict: Validation results
    """
    
    try:
        # Check file extension
        file_name = getattr(uploaded_file, 'name', '')
        if not file_name.lower().endswith('.pdf'):
            return {
                'valid': False,
                'error': 'File does not have .pdf extension',
                'file_name': file_name
            }
        
        # Check file size
        file_size = len(uploaded_file.getvalue())
        max_size = 50 * 1024 * 1024  # 50MB limit
        
        if file_size > max_size:
            return {
                'valid': False,
                'error': f'File too large ({file_size / 1024 / 1024:.1f}MB). Maximum size is {max_size / 1024 / 1024}MB.',
                'file_name': file_name,
                'file_size': file_size
            }
        
        # Try to read PDF structure
        if PDF_LIBRARY is None:
            return {
                'valid': True,
                'warning': 'PDF library not available for deep validation',
                'file_name': file_name,
                'file_size': file_size
            }
        
        pdf_bytes = uploaded_file.getvalue()
        pdf_stream = io.BytesIO(pdf_bytes)
        
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            num_pages = len(pdf_reader.pages)
            
            # Reset file pointer
            uploaded_file.seek(0)
            
            return {
                'valid': True,
                'file_name': file_name,
                'file_size': file_size,
                'num_pages': num_pages,
                'encrypted': pdf_reader.is_encrypted
            }
            
        except Exception as pdf_error:
            # Reset file pointer
            uploaded_file.seek(0)
            
            return {
                'valid': False,
                'error': f'Invalid PDF structure: {str(pdf_error)}',
                'file_name': file_name,
                'file_size': file_size
            }
        
    except Exception as e:
        return {
            'valid': False,
            'error': f'Validation failed: {str(e)}',
            'file_name': getattr(uploaded_file, 'name', 'unknown')
        }

def split_pdf_pages(uploaded_file, page_range=None):
    """
    Split PDF into individual pages or extract specific pages.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        page_range: List of page numbers to extract (1-indexed) or None for all
        
    Returns:
        dict: Split results with individual page data
    """
    
    if PDF_LIBRARY is None:
        raise ImportError("PDF processing library not available. Install PyPDF2 or pypdf.")
    
    try:
        pdf_bytes = uploaded_file.getvalue()
        pdf_stream = io.BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_stream)
        
        if pdf_reader.is_encrypted:
            return {
                'success': False,
                'error': 'Cannot split encrypted PDF',
                'pages': []
            }
        
        total_pages = len(pdf_reader.pages)
        
        # Determine which pages to extract
        if page_range:
            # Validate page range
            invalid_pages = [p for p in page_range if p < 1 or p > total_pages]
            if invalid_pages:
                return {
                    'success': False,
                    'error': f'Invalid page numbers: {invalid_pages}. PDF has {total_pages} pages.',
                    'pages': []
                }
            pages_to_extract = sorted(set(page_range))
        else:
            pages_to_extract = list(range(1, total_pages + 1))
        
        extracted_pages = []
        
        for page_num in pages_to_extract:
            try:
                # Create new PDF with single page
                writer = PyPDF2.PdfWriter()
                writer.add_page(pdf_reader.pages[page_num - 1])
                
                # Write to bytes
                page_stream = io.BytesIO()
                writer.write(page_stream)
                page_bytes = page_stream.getvalue()
                page_stream.close()
                
                extracted_pages.append({
                    'page_number': page_num,
                    'pdf_bytes': page_bytes,
                    'size': len(page_bytes)
                })
                
            except Exception as page_error:
                extracted_pages.append({
                    'page_number': page_num,
                    'error': str(page_error),
                    'pdf_bytes': None,
                    'size': 0
                })
        
        return {
            'success': True,
            'total_pages': total_pages,
            'extracted_pages': len([p for p in extracted_pages if p.get('pdf_bytes')]),
            'pages': extracted_pages,
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'PDF split failed: {str(e)}',
            'pages': []
        }

def merge_pdf_files(uploaded_files):
    """
    Merge multiple PDF files into one.
    
    Args:
        uploaded_files: List of Streamlit UploadedFile objects
        
    Returns:
        dict: Merge results with combined PDF bytes
    """
    
    if PDF_LIBRARY is None:
        raise ImportError("PDF processing library not available. Install PyPDF2 or pypdf.")
    
    try:
        if not uploaded_files:
            return {
                'success': False,
                'error': 'No files provided for merging',
                'pdf_bytes': None
            }
        
        writer = PyPDF2.PdfWriter()
        file_info = []
        total_pages = 0
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                pdf_bytes = uploaded_file.getvalue()
                pdf_stream = io.BytesIO(pdf_bytes)
                pdf_reader = PyPDF2.PdfReader(pdf_stream)
                
                if pdf_reader.is_encrypted:
                    file_info.append({
                        'file_name': uploaded_file.name,
                        'pages': 0,
                        'error': 'Encrypted PDF skipped'
                    })
                    continue
                
                pages_added = 0
                for page in pdf_reader.pages:
                    writer.add_page(page)
                    pages_added += 1
                    total_pages += 1
                
                file_info.append({
                    'file_name': uploaded_file.name,
                    'pages': pages_added,
                    'error': None
                })
                
            except Exception as file_error:
                file_info.append({
                    'file_name': uploaded_file.name,
                    'pages': 0,
                    'error': str(file_error)
                })
        
        if total_pages == 0:
            return {
                'success': False,
                'error': 'No pages could be merged from provided files',
                'pdf_bytes': None,
                'file_info': file_info
            }
        
        # Create merged PDF bytes
        merged_stream = io.BytesIO()
        writer.write(merged_stream)
        merged_bytes = merged_stream.getvalue()
        merged_stream.close()
        
        return {
            'success': True,
            'pdf_bytes': merged_bytes,
            'total_pages': total_pages,
            'merged_files': len([f for f in file_info if f['error'] is None]),
            'file_info': file_info,
            'size': len(merged_bytes)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'PDF merge failed: {str(e)}',
            'pdf_bytes': None
        }

def get_pdf_metadata(uploaded_file):
    """
    Extract detailed metadata from PDF file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        dict: Comprehensive PDF metadata
    """
    
    if PDF_LIBRARY is None:
        return {
            'available': False,
            'error': 'PDF processing library not available'
        }
    
    try:
        pdf_bytes = uploaded_file.getvalue()
        pdf_stream = io.BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_stream)
        
        # Basic metadata
        metadata = {
            'available': True,
            'file_name': uploaded_file.name,
            'file_size': len(pdf_bytes),
            'num_pages': len(pdf_reader.pages),
            'encrypted': pdf_reader.is_encrypted,
            'pdf_version': getattr(pdf_reader, 'pdf_header', 'Unknown')
        }
        
        # Document info (if available)
        if hasattr(pdf_reader, 'metadata') and pdf_reader.metadata:
            doc_info = pdf_reader.metadata
            metadata['document_info'] = {
                'title': doc_info.get('/Title', ''),
                'author': doc_info.get('/Author', ''),
                'subject': doc_info.get('/Subject', ''),
                'creator': doc_info.get('/Creator', ''),
                'producer': doc_info.get('/Producer', ''),
                'creation_date': str(doc_info.get('/CreationDate', '')),
                'modification_date': str(doc_info.get('/ModDate', ''))
            }
        
        # Page analysis (sample first few pages for performance)
        page_analysis = []
        sample_pages = min(3, len(pdf_reader.pages))
        
        for i in range(sample_pages):
            try:
                page = pdf_reader.pages[i]
                page_info = {
                    'page_number': i + 1,
                    'has_text': bool(page.extract_text().strip()),
                    'text_length': len(page.extract_text())
                }
                
                # Try to get page dimensions
                if hasattr(page, 'mediaBox') and page.mediaBox:
                    page_info['width'] = float(page.mediaBox.width)
                    page_info['height'] = float(page.mediaBox.height)
                
                page_analysis.append(page_info)
                
            except Exception as page_error:
                page_analysis.append({
                    'page_number': i + 1,
                    'error': str(page_error)
                })
        
        metadata['sample_pages'] = page_analysis
        
        return metadata
        
    except Exception as e:
        return {
            'available': False,
            'error': f'Metadata extraction failed: {str(e)}',
            'file_name': uploaded_file.name
        }

def create_pdf_summary(uploaded_file, max_pages=None):
    """
    Create a comprehensive summary of PDF content and structure.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        max_pages: Maximum number of pages to analyze (None for all)
        
    Returns:
        dict: Complete PDF summary
    """
    
    try:
        # Get basic validation
        validation = validate_pdf_file(uploaded_file)
        if not validation['valid']:
            return {
                'success': False,
                'error': validation['error'],
                'summary': None
            }
        
        # Get metadata
        metadata = get_pdf_metadata(uploaded_file)
        
        # Extract text content
        text_extraction = extract_text_from_pdf(uploaded_file)
        
        if not text_extraction['success']:
            return {
                'success': False,
                'error': text_extraction['error'],
                'summary': None
            }
        
        # Analyze content
        pages_to_analyze = text_extraction['pages'][:max_pages] if max_pages else text_extraction['pages']
        
        content_analysis = {
            'total_pages': len(text_extraction['pages']),
            'analyzed_pages': len(pages_to_analyze),
            'total_words': sum(p['word_count'] for p in pages_to_analyze),
            'total_chars': sum(p['char_count'] for p in pages_to_analyze),
            'empty_pages': len([p for p in pages_to_analyze if p['word_count'] == 0]),
            'text_pages': len([p for p in pages_to_analyze if p['word_count'] > 0])
        }
        
        # Calculate averages
        text_pages = [p for p in pages_to_analyze if p['word_count'] > 0]
        if text_pages:
            content_analysis['avg_words_per_page'] = sum(p['word_count'] for p in text_pages) / len(text_pages)
            content_analysis['avg_chars_per_page'] = sum(p['char_count'] for p in text_pages) / len(text_pages)
        else:
            content_analysis['avg_words_per_page'] = 0
            content_analysis['avg_chars_per_page'] = 0
        
        # Create summary
        summary = {
            'file_info': {
                'name': uploaded_file.name,
                'size': validation['file_size'],
                'size_mb': round(validation['file_size'] / 1024 / 1024, 2)
            },
            'structure': {
                'pages': validation['num_pages'],
                'encrypted': validation.get('encrypted', False),
                'pdf_version': metadata.get('pdf_version', 'Unknown')
            },
            'content': content_analysis,
            'document_info': metadata.get('document_info', {}),
            'processing_status': {
                'text_extractable': text_extraction['success'],
                'pages_with_text': content_analysis['text_pages'],
                'processing_errors': len([p for p in pages_to_analyze if 'error' in p])
            }
        }
        
        return {
            'success': True,
            'summary': summary,
            'raw_text': text_extraction['text'] if len(text_extraction['text']) < 10000 else text_extraction['text'][:10000] + "...[truncated]",
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Summary creation failed: {str(e)}',
            'summary': None
        }