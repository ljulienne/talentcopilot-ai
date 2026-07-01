import pdfplumber


def extract_text_from_pdf(uploaded_file):
    try:
        text = ""

        with pdfplumber.open(uploaded_file) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_number} ---\n"
                    text += page_text + "\n"

        text = text.strip()

        if not text:
            return {
                "success": False,
                "text": "",
                "error": "No readable text found. The PDF may be scanned or image-based."
            }

        return {
            "success": True,
            "text": text,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "text": "",
            "error": str(e)
        }