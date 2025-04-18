# PDF Parser API

A simple FastAPI server that processes PDF files and returns their content page by page.

## Setup

1. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

## API Usage

### Upload and Parse PDF

Send a POST request to `/parse-pdf/` with a PDF file in the request body.

Example using curl:
```bash
curl -X POST "http://localhost:8000/parse-pdf/" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@your_file.pdf"
```

### Upload and Parse PDF with Gemini

Send a POST request to `/parse-pdf-gemini/` with a PDF file and optional page range in the request body.

Example using curl to parse all pages:
```bash
curl -X POST "http://localhost:8000/parse-pdf-gemini/" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@your_file.pdf" -F "page_range=all"
```

Example using curl to parse specific pages (e.g., pages 1-3):
```bash
curl -X POST "http://localhost:8000/parse-pdf-gemini/" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@your_file.pdf" -F "page_range=1-3"
```

The `page_range` parameter accepts:
- "all" to process all pages (default)
- "start-end" format (e.g., "1-3") to process a specific range of pages

### Response Format

The API returns a JSON response with the following structure:
```json
{
    "filename": "your_file.pdf",
    "total_pages": 3,
    "processed_pages": 2,  // Only present in /parse-pdf-gemini/ response
    "pages": [
        {
            "page_number": 1,
            "content": "Text content from page 1",
            "emails": ["email1@example.com"],
            "links": ["https://example.com"],
            "tables": [
                {
                    "header": ["Column 1", "Column 2"],
                    "content": [["Data 1", "Data 2"], ["Data 3", "Data 4"]]
                }
            ]
        },
        // ... more pages
    ]
}
```

## API Documentation

Once the server is running, you can access the automatic API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc` 