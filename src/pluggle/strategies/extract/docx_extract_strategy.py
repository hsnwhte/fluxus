import io
import json
import zipfile
from pyexpat import ExpatError

import xmltodict

from pluggle.enums import ContentFormat
from pluggle.exceptions import errors
from pluggle.models.dto import TransformableData


class DocxExtractStrategy:
    @staticmethod
    def extract(*, content: bytes) -> TransformableData:
        try:
            filelike = io.BytesIO(content)
            z = zipfile.ZipFile(filelike)
            parsed = {}
            for name in z.namelist():
                if name.endswith(".xml"):
                    file_bytes = z.read(name)
                    parsed[name] = xmltodict.parse(file_bytes)
        except zipfile.BadZipFile as e:
            raise errors.ExtractSyntaxError(f"Not a valid DOCX content: {e}") from e
        except ExpatError as e:
            raise errors.ExtractSyntaxError(f"Malformed XML inside DOCX: {e}") from e
        content = json.dumps(parsed, ensure_ascii=False).encode()
        return TransformableData(content=content, origin_format=ContentFormat.DOCX)
