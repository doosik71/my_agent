import requests  # pyright: ignore[reportMissingModuleSource]
import fitz  # pyright: ignore[reportMissingImports]
import os
import uuid


def read_pdf_from_url(pdf_url: str) -> str:
    """
    Downloads a PDF from a given URL, extracts its text content, and returns it.
    Use this tool when the user provides a PDF URL or asks to read content from a PDF document.
    The downloaded PDF is saved to a temporary location and then deleted.

    Args:
        pdf_url: The URL to the PDF document.

    Returns:
        The extracted text content from the PDF, or an error message if extraction fails.
    """
    temp_dir = "temp"  # Using a relative path for temporary files
    os.makedirs(temp_dir, exist_ok=True)
    temp_filepath = os.path.join(temp_dir, f"{uuid.uuid4()}.pdf")

    try:
        # Download the PDF
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        with open(temp_filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Extract text using PyMuPDF
        document = fitz.open(temp_filepath)
        text_content = ""
        for page_num in range(document.page_count):
            page = document.load_page(page_num)
            text_content += page.get_text()
        document.close()

        return text_content
    except requests.exceptions.RequestException as e:
        return f"Error downloading PDF from {pdf_url}: {e}"
    except fitz.FileNotFoundError:
        return f"Error: Downloaded PDF file not found at {temp_filepath}."
    except Exception as e:
        return f"Error extracting text from PDF: {e}"
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        # Optionally remove the temp directory if it's empty, but not strictly necessary
        # try:
        #     os.rmdir(temp_dir)
        # except OSError:
        #     pass # Directory not empty
