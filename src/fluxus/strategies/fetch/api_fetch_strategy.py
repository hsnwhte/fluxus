import httpx

from fluxus.enums import ContentFormat
from fluxus.models.dto import ExtractableData
from fluxus.exceptions import errors


class ApiFetchStrategy:
    @staticmethod
    def fetch(*, address:str, table_name:str | None = None) ->ExtractableData:
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

        return ExtractableData(
            content=response.content,
            source_format=ContentFormat.JSON,
            # assumed for now; see note on Content-Type detection
        )