import fitz # PyMuPDF
import io
from PIL import Image

def extract_text_from_pdf(file):
    """
    Extracts text from a PDF file.

    Args:
        file (UploadedFile): The PDF file uploaded via Streamlit.

    Returns:
        str: A string containing the text extracted from the PDF.
    """
    # Reset file pointer to the beginning for reading
    file.seek(0)
    
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_and_images_from_pdf(file):
    """
    Extracts text and all images from a PDF file.

    Args:
        file (UploadedFile): The PDF file uploaded via Streamlit.

    Returns:
        tuple: A tuple containing a string of text and a list of image bytes.
    """
    # Reset file pointer to the beginning for reading
    file.seek(0)
    
    text = ""
    images = []
    
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            # Extract text from the page
            text += page.get_text()
            
            # Extract image data as bytes
            for img in page.get_images(full=True):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Append the raw image bytes to the list
                images.append(image_bytes)
                
    return text, images

