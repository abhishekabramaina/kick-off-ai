import io
import PyPDF2
import docx

def extract_text_from_bytes(content: bytes, mime_type: str) -> str:
    """
    Technical utility to extract plain text from various binary file formats.
    - Concept: Infrastructure Utility.
    - Why: Decouples binary parsing logic from business workflows (Services) and API routes (Routers).
    - Support: PDF, DOCX, and plain text.
    """
    if mime_type == "application/pdf":
        # PyPDF2 reads from a stream, so we wrap the bytes in io.BytesIO
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        return "\n".join([page.extract_text() for page in reader.pages])
    
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        # python-docx also reads from a stream
        doc = docx.Document(io.BytesIO(content))
        return "\n".join([para.text for para in doc.paragraphs])
    
    elif "text/" in mime_type or mime_type == "application/vnd.google-apps.document":
        # For plain text or Google Docs exported as text, we decode directly
        return content.decode("utf-8")
    
    return ""
