from typing import List, Dict, Any
from pypdf import PdfReader
import io

def extract_tables_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract tables from plain text using basic table detection."""
    tables = []
    lines = text.split('\n')
    current_table = []
    in_table = False
    
    for line in lines:
        if len(line.split()) > 1 and any(len(part) > 20 for part in line.split()):
            if not in_table:
                in_table = True
                current_table = []
            current_table.append(line)
        else:
            if in_table and current_table:
                table_data = []
                for row in current_table:
                    columns = [col.strip() for col in row.split('  ') if col.strip()]
                    table_data.append(columns)
                
                if table_data:
                    tables.append({
                        "data": table_data,
                        "row_count": len(table_data),
                        "column_count": len(table_data[0]) if table_data else 0,
                        "source": "text"
                    })
                
                in_table = False
                current_table = []
    
    return tables

def extract_tables_from_annotations(page) -> List[Dict[str, Any]]:
    """Extract tables from PDF annotations and form fields."""
    tables = []
    
    # Check for table annotations
    if "/Annots" in page:
        for annot in page["/Annots"]:
            annot_obj = annot.get_object()
            if "/Contents" in annot_obj:
                content = annot_obj["/Contents"]
                if isinstance(content, str):
                    tables.extend(extract_tables_from_text(content))
    
    # Check for form fields that might contain table data
    if "/AcroForm" in page:
        form = page["/AcroForm"]
        if "/Fields" in form:
            table_fields = []
            for field in form["/Fields"]:
                field_obj = field.get_object()
                if "/FT" in field_obj and field_obj["/FT"] == "/Tx":  # Text field
                    if "/V" in field_obj:
                        value = field_obj["/V"]
                        if isinstance(value, str):
                            table_fields.append(value)
            
            if table_fields:
                # Try to detect if these fields form a table
                table_data = []
                for field in table_fields:
                    row = [col.strip() for col in field.split('\t') if col.strip()]
                    if row:
                        table_data.append(row)
                
                if table_data and len(table_data) > 1:
                    tables.append({
                        "data": table_data,
                        "row_count": len(table_data),
                        "column_count": len(table_data[0]) if table_data else 0,
                        "source": "form"
                    })
    
    return tables

def extract_tables(page) -> List[Dict[str, Any]]:
    """
    Extract tables from a PDF page, including both text content and PDF-specific elements.
    
    Args:
        page: A PDF page object from PyPDF2
        
    Returns:
        List[Dict[str, Any]]: List of tables found on the page, where each table is a dictionary
                             containing the table data and metadata
    """
    # Extract from text content
    text = page.extract_text()
    text_tables = extract_tables_from_text(text)
    
    # Extract from PDF-specific elements
    pdf_tables = extract_tables_from_annotations(page)
    
    # Combine all tables
    all_tables = text_tables + pdf_tables
    
    # Add page-specific metadata
    for table in all_tables:
        table["page_number"] = page.page_number + 1
    
    return all_tables 