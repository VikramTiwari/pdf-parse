from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import JSONResponse
from pypdf import PdfReader
import io
from typing import List
from extractors import extract_emails, extract_links, extract_tables
from extractors.gemini_extractor import extract_page_with_gemini

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

@app.post("/parse-pdf-gemini/")
async def parse_pdf_gemini(
    file: UploadFile = File(...),
    page_range: str = Query("all", description="Page range to parse (e.g., '1-3' or 'all')")
):
    try:
        # Read the uploaded file
        contents = await file.read()

        # Create a PDF reader object
        pdf_reader = PdfReader(io.BytesIO(contents))
        total_pages = len(pdf_reader.pages)

        # Determine which pages to process
        pages_to_process = []
        if page_range.lower() == "all":
            pages_to_process = range(total_pages)
        else:
            try:
                start, end = map(int, page_range.split("-"))
                # Convert to 0-based indexing and ensure within bounds
                start = max(0, start - 1)
                end = min(total_pages, end)
                pages_to_process = range(start, end)
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid page range format. Use 'all' or 'start-end' (e.g., '1-3')"}
                )

        # Extract information from specified pages using Gemini
        pages_data = []
        for page_num in pages_to_process:
            page = pdf_reader.pages[page_num]

            # Extract information using Gemini
            content, page_info = extract_page_with_gemini(page)

            pages_data.append({
                "page_number": page_num + 1,
                "content": content,
                **page_info
            })

        return JSONResponse(content={
            "filename": file.filename,
            "total_pages": total_pages,
            "processed_pages": len(pages_data),
            "pages": pages_data
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing PDF with Gemini: {str(e)}"}
        )

@app.get("/")
async def root():
    return {"message": "Welcome to PDF Parser API. Use POST /parse-pdf/ or /parse-pdf-gemini/ to upload and parse PDF files."}
