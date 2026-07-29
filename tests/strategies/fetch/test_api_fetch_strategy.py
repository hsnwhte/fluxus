import httpx
import pytest
from unittest.mock import patch, MagicMock

from fluxus.exceptions import errors
from fluxus.enums import ContentFormat
from fluxus.strategies.fetch.api_fetch_strategy import ApiFetchStrategy

CONTENT =b'{"test_key":"test_value"}'

def _mock_response(status_code, content:bytes = CONTENT):
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.content = content
    if status_code >= 400:
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=mock_response
        )
    return mock_response


def test_api_fetch_strategy_success():
    with patch("fluxus.strategies.fetch.api_fetch_strategy.httpx.get", return_value=_mock_response(200)):
        result = ApiFetchStrategy.fetch(address="https://mock-url.com")

    assert result.content == b'{"test_key":"test_value"}'
    assert result.source_format == ContentFormat.JSON

@pytest.mark.parametrize("status_code,expected_error", [
    (400, errors.FetchBadRequestError),
    (401, errors.FetchNotAuthorizedError),
    (403, errors.FetchNotAuthorizedError),
    (404, errors.FetchNotFoundError),
    (429, errors.FetchRateLimitError),
    (502, errors.FetchServerError),
])

def test_api_fetch_strategy_status_errors(status_code, expected_error):
    mock_response = _mock_response(status_code)
    with patch("fluxus.strategies.fetch.api_fetch_strategy.httpx.get", return_value=mock_response):
        with pytest.raises(expected_error):
            ApiFetchStrategy.fetch(address="https://mock-url.com")