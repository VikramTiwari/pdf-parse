import re
from typing import List, Dict, Any
from pypdf import PdfReader

def extract_links_from_text(text: str) -> List[str]:
    """Extract URLs from plain text using regex."""
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w .-]*/?'
    links = re.findall(url_pattern, text)
    return list(dict.fromkeys(links))

def extract_links_from_annotations(page) -> List[str]:
    """Extract links from PDF annotations and form fields."""
    links = []
    
    # Check annotations
    if "/Annots" in page:
        for annot in page["/Annots"]:
            annot_obj = annot.get_object()
            # Check for link annotations
            if annot_obj.get("/Subtype") == "/Link":
                if "/A" in annot_obj:
                    action = annot_obj["/A"]
                    if "/URI" in action:
                        uri = action["/URI"]
                        if isinstance(uri, str):
                            links.append(uri)
            
            # Check annotation contents
            if "/Contents" in annot_obj:
                links.extend(extract_links_from_text(annot_obj["/Contents"]))
    
    # Check form fields
    if "/AcroForm" in page:
        form = page["/AcroForm"]
        if "/Fields" in form:
            for field in form["/Fields"]:
                field_obj = field.get_object()
                if "/V" in field_obj:
                    value = field_obj["/V"]
                    if isinstance(value, str):
                        links.extend(extract_links_from_text(value))
    
    return list(dict.fromkeys(links))

def extract_links(page) -> List[str]:
    """
    Extract URLs from a PDF page, including both text content and PDF-specific elements.
    
    Args:
        page: A PDF page object from PyPDF2
        
    Returns:
        List[str]: List of unique URLs found
    """
    # Extract from text content
    text = page.extract_text()
    text_links = extract_links_from_text(text)
    
    # Extract from PDF-specific elements
    pdf_links = extract_links_from_annotations(page)
    
    # Combine and deduplicate
    all_links = text_links + pdf_links
    return list(dict.fromkeys(all_links)) 