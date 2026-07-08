from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

from talentcopilot.document_intelligence.document_loader import DocumentLoader


@dataclass
class UploadedTextDocument:
    filename: str
    file_type: str
    text: str
    status: str = "OK"


class UploadTextReaderService:
    SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}

    def read_uploaded_file(self, uploaded_file) -> UploadedTextDocument:
        filename = getattr(uploaded_file, "name", "uploaded.txt")
        suffix = Path(filename).suffix.lower()

        if suffix not in self.SUPPORTED_EXTENSIONS:
            return UploadedTextDocument(
                filename=filename,
                file_type=suffix.replace(".", "") or "unknown",
                text="",
                status=f"Unsupported file type: {suffix}",
            )

        if suffix == ".txt":
            raw = uploaded_file.getvalue()
            text = raw.decode("utf-8", errors="ignore") if isinstance(raw, bytes) else str(raw)
            return UploadedTextDocument(filename=filename, file_type="txt", text=text)

        with NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
            raw = uploaded_file.getvalue()
            tmp.write(raw)
            tmp.flush()
            loaded = DocumentLoader().load_path(tmp.name)
            return UploadedTextDocument(filename=filename, file_type=loaded.file_type, text=loaded.text)

    def read_text_direct(self, filename: str, text: str) -> UploadedTextDocument:
        suffix = Path(filename).suffix.lower().replace(".", "") or "txt"
        return UploadedTextDocument(filename=filename, file_type=suffix, text=text)
