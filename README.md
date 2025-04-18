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

### Response Format

The API returns a JSON response with the following structure:
```json
{
    "filename": "your_file.pdf",
    "total_pages": 3,
    "pages": [
        {
            "page_number": 1,
            "content": "Text content from page 1"
        },
        {
            "page_number": 2,
            "content": "Text content from page 2"
        },
        // ... more pages
    ]
}
```

## API Documentation

Once the server is running, you can access the automatic API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc` 