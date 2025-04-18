import json
import os
from typing import Dict, Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Initialize Gemini with API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")


client = genai.Client(api_key=GEMINI_API_KEY)
model = "gemini-2.0-flash"

generate_content_config = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=genai.types.Schema(
        type = genai.types.Type.OBJECT,
        properties = {
            "emails": genai.types.Schema(
                type = genai.types.Type.ARRAY,
                items = genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
            ),
            "links": genai.types.Schema(
                type = genai.types.Type.ARRAY,
                items = genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
            ),
            "tables": genai.types.Schema(
                type = genai.types.Type.ARRAY,
                items = genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "header": genai.types.Schema(
                            type = genai.types.Type.ARRAY,
                            items = genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                        ),
                        "rows": genai.types.Schema(
                            type = genai.types.Type.ARRAY,
                            items = genai.types.Schema(
                                type = genai.types.Type.ARRAY,
                                items = genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                ),
                            ),
                        ),
                    },
                ),
            ),
        },
    ),
    system_instruction=[
        types.Part.from_text(text="""You are an AI assistant which helps in extracting structured information from PDF files"""),
    ],
)


def extract_with_gemini(text: str) -> Dict[str, Any]:
    """
    Extract information from text using Gemini.

    Args:
        text (str): The text to analyze

    Returns:
        Dict[str, Any]: Extracted information including content, emails, links, and tables
    """
    # Create the prompt
    prompt = f"""
    Analyze the following text and extract the following information in JSON format:
    1. Main content (the actual text content)
    2. Email addresses
    3. URLs/links
    4. Tables (if any, in a structured format)

    Text to analyze:
    {text}

    Return the response in this exact JSON format:
    {{
        "emails": ["email1@example.com", "email2@example.com"],
        "links": ["https://example1.com", "https://example2.com"],
        "tables": [
            {{
                "header": ["header1", "header2"],
                "content": [["content1", "content2"], ["content3", "content4"]],
            }}
        ]
    }}
    """

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]

    # Generate content
    response = client.models.generate_content(model=model, contents=contents, config=generate_content_config)
    return json.loads(response.text)

def extract_page_with_gemini(page) -> (str, Dict[str, Any]):
    """
    Extract information from a PDF page using Gemini.

    Args:
        page: A PDF page object from PyPDF2

    Returns:
        Dict[str, Any]: Extracted information including content, emails, links, and tables
    """
    # Extract text from the page
    text = page.extract_text()
    # Use Gemini to analyze the text
    return text, extract_with_gemini(text)
