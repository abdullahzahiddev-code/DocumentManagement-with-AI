import logging
import os

logger = logging.getLogger('documents')


def process_document(document_id):
    """Process a document: extract text using appropriate method."""
    import django
    # Ensure Django is set up (needed for threads)
    if not django.conf.settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()

    from documents.models import Document

    try:
        doc = Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        logger.error(f'Document {document_id} not found for processing.')
        return

    doc.processing_status = Document.Status.PROCESSING
    doc.save(update_fields=['processing_status'])

    try:
        file_path = doc.file.path
        file_type = doc.file_type.lower()
        extracted_text = ''

        if file_type == 'pdf':
            extracted_text = extract_pdf_text(file_path)
        elif file_type == 'docx':
            extracted_text = extract_docx_text(file_path)
        elif file_type == 'txt':
            extracted_text = extract_txt_text(file_path)
        elif file_type in ['png', 'jpg', 'jpeg']:
            extracted_text = extract_image_text(file_path)

        doc.extracted_text = extracted_text or ''
        doc.processing_status = Document.Status.COMPLETED
        doc.processing_error = ''
        doc.save(update_fields=['extracted_text', 'processing_status', 'processing_error'])
        logger.info(f'Document {document_id} processed successfully. Extracted {len(extracted_text)} chars.')

    except Exception as e:
        logger.error(f'Error processing document {document_id}: {e}')
        doc.processing_status = Document.Status.FAILED
        doc.processing_error = str(e)[:1000]
        doc.save(update_fields=['processing_status', 'processing_error'])


def extract_pdf_text(file_path):
    """Extract text from PDF using PyMuPDF. Falls back to OCR for scanned PDFs."""
    try:
        import fitz  # PyMuPDF
        text = ''
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text()
        # If minimal text extracted, try OCR
        if len(text.strip()) < 50:
            logger.info(f'PDF has little text ({len(text.strip())} chars), attempting OCR.')
            text = ocr_pdf(file_path) or text
        return text
    except ImportError:
        logger.warning('PyMuPDF not installed. Cannot extract PDF text.')
        return ''
    except Exception as e:
        logger.error(f'PDF extraction error: {e}')
        raise


def extract_docx_text(file_path):
    """Extract text from DOCX using python-docx."""
    try:
        from docx import Document as DocxDocument
        doc = DocxDocument(file_path)
        return '\n'.join(para.text for para in doc.paragraphs if para.text)
    except ImportError:
        logger.warning('python-docx not installed.')
        return ''
    except Exception as e:
        logger.error(f'DOCX extraction error: {e}')
        raise


def extract_txt_text(file_path):
    """Read plain text files."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        logger.error(f'TXT extraction error: {e}')
        raise


def extract_image_text(file_path):
    """Extract text from images using Tesseract OCR."""
    try:
        import pytesseract
        from PIL import Image
        from django.conf import settings
        if hasattr(settings, 'TESSERACT_CMD') and os.path.exists(settings.TESSERACT_CMD):
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
        img = Image.open(file_path)
        return pytesseract.image_to_string(img)
    except ImportError:
        logger.warning('pytesseract or Pillow not installed.')
        return ''
    except Exception as e:
        logger.error(f'Image OCR error: {e}')
        raise


def ocr_pdf(file_path):
    """OCR a scanned PDF by converting pages to images then running Tesseract."""
    try:
        import fitz
        import pytesseract
        from PIL import Image
        import io
        from django.conf import settings

        if hasattr(settings, 'TESSERACT_CMD') and os.path.exists(settings.TESSERACT_CMD):
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

        text = ''
        with fitz.open(file_path) as pdf:
            for page_num, page in enumerate(pdf):
                if page_num > 10:  # Limit to first 10 pages for performance
                    break
                mat = fitz.Matrix(2, 2)  # 2x zoom for better OCR quality
                pix = page.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes('png')
                img = Image.open(io.BytesIO(img_bytes))
                page_text = pytesseract.image_to_string(img)
                text += page_text + '\n'
        return text
    except ImportError:
        logger.warning('pytesseract/Pillow not available for PDF OCR.')
        return ''
    except Exception as e:
        logger.error(f'PDF OCR error: {e}')
        return ''
