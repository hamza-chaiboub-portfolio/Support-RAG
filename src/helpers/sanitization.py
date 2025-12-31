import re
import html
import os

def sanitize_input(text: str) -> str:
    """
    Sanitize input string by removing HTML tags and special characters.
    
    Args:
        text: Input string
        
    Returns:
        Sanitized string
    """
    if not text:
        return text
        
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]*>', '', text)
    
    # Unescape HTML entities
    clean_text = html.unescape(clean_text)
    
    # Remove potential script injection patterns
    clean_text = re.sub(r'javascript:', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'vbscript:', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'onload', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'onerror', '', clean_text, flags=re.IGNORECASE)
    
    return clean_text.strip()

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and other issues.
    
    Args:
        filename: Input filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed_file"
        
    # Remove directory traversal characters
    filename = os.path.basename(filename)
    
    # Remove non-alphanumeric characters except dots, dashes, and underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    return filename
