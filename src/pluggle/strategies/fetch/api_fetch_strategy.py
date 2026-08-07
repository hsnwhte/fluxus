import httpx

from pluggle.enums import MimeType
from pluggle.exceptions import errors
from pluggle.helpers import mime_to_content_format
from pluggle.models.dto import ExtractableData


class ApiFetchStrategy:
    @staticmethod
    def fetch(*, address: str, table_name: str | None = None) -> ExtractableData:
        try:
            response = httpx.get(address, timeout=10.0)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status == 400:
                raise errors.FetchBadRequestError(address)
            if status in (401, 403):
                raise errors.FetchNotAuthorizedError(address, status)
            if status == 404:
                raise errors.FetchNotFoundError(address)
            if status == 429:
                raise errors.FetchRateLimitError(address)
            if 500 <= status < 600:
                raise errors.FetchServerError(address, status)
            raise

        content = response.content
        mime = response.headers.get("Content-Type")
        if mime is None:
            raise errors.FetchContentTypeMissingError(address=address)
        clean_mime = mime.split(";")[0].strip()
        if clean_mime.endswith("+xml"):
            clean_mime = "application/xml"
        try:
            mime_type = MimeType(clean_mime)
        except ValueError as e:
            raise errors.FetchApiError(
                f"Unrecognized Content-Type: {clean_mime}"
            ) from e

        content_type = mime_to_content_format(mime_type)
        return ExtractableData(content=content, source_format=content_type)
