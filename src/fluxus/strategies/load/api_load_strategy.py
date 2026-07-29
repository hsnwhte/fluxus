import httpx

from fluxus.enums import MimeType, ContentFormat
from fluxus.models.dto import TransformedData
from fluxus.exceptions import errors

CONTENT_FORMAT_TO_MIME = {
    ContentFormat.JSON: MimeType.JSON,
    ContentFormat.XML: MimeType.XML,
    ContentFormat.CSV: MimeType.CSV,
    ContentFormat.HTML: MimeType.HTML,
}

class ApiLoadStrategy:
    @staticmethod
    def load(*, data:TransformedData, address:str, target_format:ContentFormat, table_name:str | None = None) ->None:
        try:
            response = httpx.put(
                url=address,
                content=data.content,
                headers={"Content-Type": CONTENT_FORMAT_TO_MIME[target_format].value},
                timeout=10.0
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code

            if status == 400:
                raise errors.LoadBadRequestError(address)
            if status in (401, 403):
                raise errors.LoadNotAuthorizedError(address, status)
            if status == 404:
                raise errors.LoadNotFoundError(address)
            if status == 413:
                raise errors.LoadPayloadTooLargeError(address)
            if status == 429:
                raise errors.LoadRateLimitError(address)
            if 500 <= status < 600:
                raise errors.LoadServerError(address, status)
            raise

