from unittest.mock import MagicMock, patch

import httpx
import pytest

from fluxus.enums import ContentFormat
from fluxus.exceptions import errors
from fluxus.strategies.fetch.api_fetch_strategy import ApiFetchStrategy

CONTENT = b'{"test_key":"test_value"}'


def _mock_response(
    status_code, content: bytes = CONTENT, content_type: str | None = "application/json"
):
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.content = content
    mock_response.headers = {"Content-Type": content_type}
    if status_code >= 400:
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=mock_response
        )
    return mock_response


def test_api_fetch_strategy_success():
    with patch(
        "fluxus.strategies.fetch.api_fetch_strategy.httpx.get",
        return_value=_mock_response(200),
    ):
        result = ApiFetchStrategy.fetch(address="https://mock-url.com")

    assert result.content == CONTENT
    assert result.source_format == ContentFormat.JSON


def test_api_fetch_strategy_missing_content_type():
    mock_response = _mock_response(200, content_type=None)
    mock_response.headers = {}
    with patch(
        "fluxus.strategies.fetch.api_fetch_strategy.httpx.get",
        return_value=mock_response,
    ):
        with pytest.raises(errors.FetchContentTypeMissingError):
            ApiFetchStrategy.fetch(address="https://mock-url.com")


def test_api_fetch_strategy_unrecognized_content_type():
    with patch(
        "fluxus.strategies.fetch.api_fetch_strategy.httpx.get",
        return_value=_mock_response(200, content_type="application/unknown"),
    ):
        with pytest.raises(errors.FetchApiError):
            ApiFetchStrategy.fetch(address="https://mock-url.com")
