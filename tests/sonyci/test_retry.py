"""Test the retry utility in sonyci.utils."""

from unittest.mock import MagicMock, patch

from pytest import fixture, mark, raises
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

from sonyci.exceptions import RetryError
from sonyci.utils import DEFAULT_RETRY_HTTP_CODES, retry


@fixture
def mock_sleep():
    """Patch sleep in the utils module so tests don't actually wait."""
    with patch('sonyci.utils.sleep') as sleep_mock:
        yield sleep_mock


@fixture
def http_error():
    """Factory building an HTTPError whose response carries a status and headers."""

    def _build(status_code: int, headers: dict | None = None) -> HTTPError:
        response = MagicMock()
        response.status_code = status_code
        response.headers = headers or {}
        return HTTPError(response=response)

    return _build


@fixture
def mock_func():
    """Stand-in for the function being wrapped by retry."""
    return MagicMock()


@fixture
def wrapped(mock_func):
    """The mock function wrapped by the retry decorator with default options."""
    return retry(mock_func)


def test_returns_result_on_success(mock_sleep, mock_func, wrapped):
    """A function that succeeds returns its result and never sleeps."""
    mock_func.return_value = 'ok'
    assert wrapped('a', key='b') == 'ok'
    mock_func.assert_called_once_with('a', key='b')
    mock_sleep.assert_not_called()


def test_retries_then_succeeds(mock_sleep, mock_func, wrapped, http_error):
    """A retriable error is retried, then the eventual success is returned."""
    mock_func.side_effect = [http_error(503), 'ok']
    assert wrapped() == 'ok'
    assert mock_func.call_count == 2
    mock_sleep.assert_called_once_with(1)


@mark.parametrize('code', DEFAULT_RETRY_HTTP_CODES)
def test_retries_every_default_http_code(
    code, mock_sleep, mock_func, wrapped, http_error
):
    """Each default retriable status code triggers a retry."""
    mock_func.side_effect = [http_error(code), 'ok']
    assert wrapped() == 'ok'
    assert mock_func.call_count == 2


def test_non_retriable_http_error_reraises(mock_sleep, mock_func, wrapped, http_error):
    """An HTTP error with a non-retriable code is raised immediately."""
    error = http_error(404)
    mock_func.side_effect = error
    with raises(HTTPError) as exc_info:
        wrapped()
    assert exc_info.value is error
    mock_func.assert_called_once()
    mock_sleep.assert_not_called()


def test_uses_retry_after_header(mock_sleep, mock_func, wrapped, http_error):
    """On a 429, the Retry-After header determines the wait time."""
    mock_func.side_effect = [http_error(429, {'Retry-After': '7'}), 'ok']
    assert wrapped() == 'ok'
    mock_sleep.assert_called_once_with(7)


def test_retries_connection_error(mock_sleep, mock_func, wrapped):
    """A network ConnectionError is retried."""
    mock_func.side_effect = [ConnectionError(), 'ok']
    assert wrapped() == 'ok'
    assert mock_func.call_count == 2
    mock_sleep.assert_called_once_with(1)


def test_retries_timeout(mock_sleep, mock_func, wrapped):
    """A Timeout is retried."""
    mock_func.side_effect = [Timeout(), 'ok']
    assert wrapped() == 'ok'
    assert mock_func.call_count == 2


def test_retries_request_exception(mock_sleep, mock_func, wrapped):
    """An ambiguous RequestException is retried."""
    mock_func.side_effect = [RequestException(), 'ok']
    assert wrapped() == 'ok'
    assert mock_func.call_count == 2


def test_raises_retry_error_after_exhausting_tries(mock_sleep, mock_func, wrapped):
    """After the default number of failures, RetryError is raised."""
    mock_func.side_effect = Timeout()
    with raises(RetryError):
        wrapped()
    assert mock_func.call_count == 5
    assert mock_sleep.call_count == 4


def test_max_tries_read_from_first_arg(mock_sleep, mock_func, wrapped):
    """max_tries is taken from the first positional arg when present."""

    class Client:
        max_tries = 3

    mock_func.side_effect = Timeout()
    with raises(RetryError):
        wrapped(Client())
    assert mock_func.call_count == 3
    assert mock_sleep.call_count == 2


def test_backoff_increases_each_attempt(mock_sleep, mock_func, wrapped):
    """Wait time grows linearly with the attempt number."""
    mock_func.side_effect = [Timeout(), Timeout(), Timeout(), 'ok']
    assert wrapped() == 'ok'
    assert [call.args[0] for call in mock_sleep.call_args_list] == [1, 2, 3]


def test_custom_initial_delay(mock_sleep, mock_func):
    """initial_delay scales the linear backoff."""
    mock_func.side_effect = [Timeout(), 'ok']
    wrapped = retry(mock_func, initial_delay=5)
    assert wrapped() == 'ok'
    mock_sleep.assert_called_once_with(5)


def test_custom_http_codes_skips_unlisted_code(mock_sleep, mock_func, http_error):
    """A status code outside a custom http_codes list is not retried."""
    mock_func.side_effect = http_error(500)
    wrapped = retry(mock_func, http_codes=[418])
    with raises(HTTPError):
        wrapped()
    mock_func.assert_called_once()
    mock_sleep.assert_not_called()


def test_custom_http_codes_retries_listed_code(mock_sleep, mock_func, http_error):
    """A status code included in a custom http_codes list is retried."""
    mock_func.side_effect = [http_error(418), 'ok']
    wrapped = retry(mock_func, http_codes=[418])
    assert wrapped() == 'ok'
    assert mock_func.call_count == 2
