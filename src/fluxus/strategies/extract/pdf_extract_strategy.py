import json
import pypdf, pypdf.errors
import io
from fluxus.models.dto import TransformableData
from fluxus.enums import ContentFormat
from fluxus.exceptions import errors


class PdfExtractStrategy:
    @staticmethod
    def extract(*, content: bytes) -> TransformableData:
        try:
            filelike = io.BytesIO(content)
            reader = pypdf.PdfReader(filelike)

            parsed = []
            for i in range(len(reader.pages)):
                page = reader.pages[i]
                text = page.extract_text()
                page_number = i + 1
                page_dict = {"page": page_number, "text": text}
                parsed.append(page_dict)
        except pypdf.errors.PdfReadError as e:
            raise errors.ExtractSyntaxError(f"Malformed PDF content: {e}") from e
        content = json.dumps(parsed, ensure_ascii=False).encode()
        return TransformableData(content=content, origin_format=ContentFormat.PDF)
