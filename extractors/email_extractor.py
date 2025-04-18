import re
from typing import List, Dict, Any
from pypdf import PdfReader

def extract_emails_from_text(text: str) -> List[str]:
    """Extract emails from plain text using regex."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return list(dict.fromkeys(emails))

def extract_emails_from_annotations(page) -> List[str]:
    """Extract emails from PDF annotations and form fields."""
    emails = []
    
    # Check annotations
    if "/Annots" in page:
        for annot in page["/Annots"]:
            annot_obj = annot.get_object()
            if "/Contents" in annot_obj:
                emails.extend(extract_emails_from_text(annot_obj["/Contents"]))
    
    # Check form fields
    if "/AcroForm" in page:
        form = page["/AcroForm"]
        if "/Fields" in form:
            for field in form["/Fields"]:
                field_obj = field.get_object()
                if "/V" in field_obj:
                    value = field_obj["/V"]
                    if isinstance(value, str):
                        emails.extend(extract_emails_from_text(value))
    
    return list(dict.fromkeys(emails))

def extract_emails(page) -> List[str]:
    """
    Extract email addresses from a PDF page, including both text content and PDF-specific elements.
    
    Args:
        page: A PDF page object from PyPDF2
        
    Returns:
        List[str]: List of unique email addresses found
    """
    # Extract from text content
    text = page.extract_text()
    text_emails = extract_emails_from_text(text)
    
    # Extract from PDF-specific elements
    pdf_emails = extract_emails_from_annotations(page)
    
    # Combine and deduplicate
    all_emails = text_emails + pdf_emails
    return list(dict.fromkeys(all_emails)) 