from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pypdf import PdfReader
import io
from typing import List
from extractors import extract_emails, extract_links, extract_tables

app = FastAPI(title="PDF Parser API")

@app.post("/parse-pdf/")
async def parse_pdf(file: UploadFile = File(...)):
    try:
        # Read the uploaded file
        contents = await file.read()
        
        # Create a PDF reader object
        pdf_reader = PdfReader(io.BytesIO(contents))
        
        # Extract text from each page
        pages_data = []
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            
            # Extract metadata using the page object
            emails = extract_emails(page)
            links = extract_links(page)
            tables = extract_tables(page)
            
            pages_data.append({
                "page_number": page_num + 1,
                "content": text,
                "metadata": {
                    "emails": emails,
                    "links": links,
                    "tables": tables
                }
            })
        
        return JSONResponse(content={
            "filename": file.filename,
            "total_pages": len(pdf_reader.pages),
            "pages": pages_data
        })
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing PDF: {str(e)}"}
        )

@app.get("/")
async def root():
    return {"message": "Welcome to PDF Parser API. Use POST /parse-pdf/ to upload and parse PDF files."} 