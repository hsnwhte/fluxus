import httpx
import pytest
from unittest.mock import patch, MagicMock

from fluxus.exceptions import errors
from fluxus.enums import ContentFormat
from fluxus.strategies.fetch.api_fetch_strategy import ApiFetchStrategy


@pytest.fixture
def mock_response_200():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"test_key":"test_value"}'
    mock_response.raise_for_status = MagicMock()
    return mock_response

@pytest.fixture
def mock_response_400():
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.content = b'{"test_key":"test_value"}'
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=MagicMock(), response=mock_response
    )
    return mock_response

@pytest.fixture
def mock_response_401():
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.content = b'{"test_key":"test_value"}'
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=MagicMock(), response=mock_response
    )
    return mock_response

@pytest.fixture
def mock_response_403():
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.content = b'{"test_key":"test_value"}'
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=MagicMock(), response=mock_response
    )
    return mock_response

@pytest.fixture
def mock_response_404():
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.content = b'{"test_key":"test_value"}'
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=MagicMock(), response=mock_response
    )
    return mock_response

@pytest.fixture
def mock_response_429():
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.content = b'{"test_key":"test_value"}'
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=MagicMock(), response=mock_response
    )
    return mock_response

@pytest.fixture
def mock_response_502():
    mock_response = MagicMock()
    mock_response.status_code = 502
    mock_response.content = b'{"test_key":"test_value"}'
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=MagicMock(), response=mock_response
    )
    return mock_response

def test_api_fetch_strategy_success(mock_response_200:MagicMock):
    with patch("fluxus.strategies.fetch.api_fetch_strategy.httpx.get", return_value=mock_response_200):
        result = ApiFetchStrategy.fetch(address="https://mock-url.com")

    assert result.content == b'{"test_key":"test_value"}'
    assert result.source_format == ContentFormat.JSON

def test_api_fetch_strategy_status_400(mock_response_400:MagicMock):
    with patch("fluxus.strategies.fetch.api_fetch_strategy.httpx.get", return_value=mock_response_400):
        with pytest.raises(errors.FetchBadRequestError):
            ApiFetchStrategy.fetch(address="https://mock-url.com")

def test_api_fetch_strategy_status_401(mock_response_401:MagicMock):
    with patch("fluxus.strategies.fetch.api_fetch_strategy.httpx.get", return_value=mock_response_401):
        with pytest.raises(errors.FetchNotAuthorizedError):
            ApiFetchStrategy.fetch(address="https://mock-url.com")

def test_api_fetch_strategy_status_403(mock_response_403:MagicMock):
    with patch("fluxus.strategies.fetch.api_fetch_strategy.httpx.get", return_value=mock_response_403):
        with pytest.raises(errors.FetchNotAuthorizedError):
            ApiFetchStrategy.fetch(address="https://mock-url.com")

def test_api_fetch_strategy_status_404(mock_response_404:MagicMock):
    with patch("fluxus.strategies.fetch.api_fetch_strategy.httpx.get", return_value=mock_response_404):
        with pytest.raises(errors.FetchNotFoundError):
            ApiFetchStrategy.fetch(address="https://mock-url.com")

def test_api_fetch_strategy_status_429(mock_response_429:MagicMock):
    with patch("fluxus.strategies.fetch.api_fetch_strategy.httpx.get", return_value=mock_response_429):
        with pytest.raises(errors.FetchRateLimitError):
            ApiFetchStrategy.fetch(address="https://mock-url.com")

def test_api_fetch_strategy_status_5xx(mock_response_502:MagicMock):
    with patch("fluxus.strategies.fetch.api_fetch_strategy.httpx.get", return_value=mock_response_502):
        with pytest.raises(errors.FetchServerError):
            ApiFetchStrategy.fetch(address="https://mock-url.com")
