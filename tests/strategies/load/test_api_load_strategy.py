import httpx
import pytest
from unittest.mock import patch, MagicMock
from fluxus.exceptions import errors
from fluxus.enums import ContentFormat
from fluxus.models.dto import TransformedData
from fluxus.strategies.load.api_load_strategy import ApiLoadStrategy


@pytest.fixture
def sample_data():
    return TransformedData(content=b'{"key": "value"}')


def _mock_response(status_code):
    mock_response = MagicMock()
    mock_response.status_code = status_code
    if status_code >= 400:
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=mock_response
        )
    return mock_response


def test_api_load_strategy_success(sample_data:TransformedData):
    with patch("fluxus.strategies.load.api_load_strategy.httpx.put", return_value=_mock_response(200)) as mock_put:
        ApiLoadStrategy.load(data=sample_data, address="https://mock-url.com", target_format=ContentFormat.JSON)

    mock_put.assert_called_once_with(
        url="https://mock-url.com",
        content=sample_data.content,
        headers={"Content-Type": "application/json"},
        timeout=10.0,
    )

@pytest.mark.parametrize("status_code,expected_error", [
    (400, errors.LoadBadRequestError),
    (401, errors.LoadNotAuthorizedError),
    (403, errors.LoadNotAuthorizedError),
    (404, errors.LoadNotFoundError),
    (413, errors.LoadPayloadTooLargeError),
    (429, errors.LoadRateLimitError),
    (502, errors.LoadServerError),
])
def test_api_load_strategy_status_errors(sample_data:TransformedData, status_code:int, expected_error):
    with patch("fluxus.strategies.load.api_load_strategy.httpx.put", return_value=_mock_response(status_code)):
        with pytest.raises(expected_error):
            ApiLoadStrategy.load(data=sample_data, address="https://mock-url.com", target_format=ContentFormat.JSON)