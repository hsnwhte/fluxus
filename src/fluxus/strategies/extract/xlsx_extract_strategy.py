import json
import zipfile
import xmltodict
import io
from pyexpat import ExpatError
from fluxus.models.dto import TransformableData
from fluxus.enums import ContentFormat
from fluxus.exceptions import errors


class XlsxExtractStrategy:
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
            raise errors.ExtractMalformedError(f"Not a valid DOCX content: {e}") from e
        except ExpatError as e:
            raise errors.ExtractMalformedError(f"Malformed XML inside DOCX: {e}") from e
        content = json.dumps(parsed, ensure_ascii=False).encode()
        return TransformableData(content=content, origin_format=ContentFormat.XLSX)
