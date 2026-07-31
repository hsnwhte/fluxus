import json
import zipfile
import xmltodict
import io
from fluxus.models.dto import TransformableData
from fluxus.enums import ContentFormat


class DocxExtractStrategy:
    @staticmethod
    def extract(*, content: bytes) -> TransformableData:
        filelike = io.BytesIO(content)
        z = zipfile.ZipFile(filelike)
        parsed = {}
        for name in z.namelist():
            if name.endswith(".xml"):
                file_bytes = z.read(name)
                parsed[name] = xmltodict.parse(file_bytes)
        content = json.dumps(parsed, ensure_ascii=False).encode()
        return TransformableData(content=content, origin_format=ContentFormat.DOCX)
