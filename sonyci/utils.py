from time import sleep

from requests import post
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout
from requests_oauth2client import BearerToken, TokenSerializer

from sonyci.config import TOKEN_URL
from sonyci.exceptions import RetryError
from sonyci.log import log


def get_token(
    username: str,
    password: str,
    client_id: str,
    client_secret: str,
    token_url: str = TOKEN_URL,
) -> BearerToken:
    """Login to SonyCI and return a BearerToken."""
    response = post(
        token_url,
        auth=(username, password),
        data={
            'grant_type': 'password',
            'client_id': client_id,
            'client_secret': client_secret,
        },
    )
    log.debug(f'token response status: {response.status_code}')
    if response.status_code != 200:
        log.error(f'Token returned {response.status_code}: {response.text}')
        raise Exception(
            f'Token did not return 200. Returned: {response.status_code}: {response.text}'
        )
    return BearerToken(**response.json())


def get_token_from_file(filename: str = '.token') -> BearerToken:
    with open(filename) as f:
        return TokenSerializer().loads(f.read())


def save_token_to_file(token: BearerToken, filename: str = '.token') -> None:
    with open(filename, 'wb') as f:
        f.write(TokenSerializer().dumps(token))


def login(
    username: str,
    password: str,
    client_id: str,
    client_secret: str,
    token_url: str = TOKEN_URL,
    save_token: bool = True,
) -> BearerToken:
    """Login to SonyCI, save the token to a file, and return a BearerToken."""
    try:
        log.trace('Trying to load token from file')
        token = get_token_from_file()
        log.debug('Loaded token from file')
        if not token.is_expired():
            log.debug(f'Token is not expired (expires at {token.expires_at})')
            return token
    except FileNotFoundError:
        log.debug('Token file not found, getting new token')
    token = get_token(username, password, client_id, client_secret, token_url)
    if save_token:
        save_token_to_file(token)
    return token


def json(func) -> callable:
    """Decorator for calling .json() on Response objects."""

    def inner(*args, **kwargs):
        return func(*args, **kwargs).json()

    return inner


DEFAULT_RETRY_HTTP_CODES = [429, 500, 502, 503, 504]


def retry(
    func: callable, http_codes: list = DEFAULT_RETRY_HTTP_CODES, initial_delay: int = 1
) -> callable:
    """Decorator for retrying a function call after a rate limit error."""

    def inner(*args, **kwargs):
        max_tries: int = (
            args[0].max_tries if args and hasattr(args[0], 'max_tries') else 5
        )
        for attempt_number in range(max_tries):
            # Reset the retry_after value before each attempt
            retry_after = None
            try:
                return func(*args, **kwargs)
            except HTTPError as e:
                if e.response.status_code not in http_codes:
                    log.error(
                        f'HTTPError {e.response.status_code} {e} on attempt {attempt_number + 1}'
                    )
                    raise e
                if e.response.status_code == 429:
                    log.warning(f'Rate limited: {e} on attempt {attempt_number + 1}')
                    # Get the retry-after header, if it exists
                    retry_after = int(
                        e.response.headers.get('Retry-After', initial_delay)
                    )
                    log.debug(f'Retry-After header: {retry_after}s')
            # Catch network errors and retry
            except ConnectionError as ce:
                log.warning(
                    f'Network error occurred (DNS, refused connection, etc.): {ce}'
                )
            except Timeout as te:
                log.warning(f'The request timed out: {te}')
            except RequestException as re:
                log.warning(
                    f'An ambiguous error occurred while handling your request: {re}'
                )
            # Wait before retrying, except last time
            if attempt_number < max_tries - 1:
                wait_time = retry_after or (attempt_number + 1) * initial_delay
                log.debug(
                    f'Attempt {attempt_number + 1} failed. Waiting {wait_time}s before retrying...'
                )
                sleep(wait_time)
        log.error(f'Failed after {max_tries} tries')
        raise RetryError(f'Failed after {max_tries} tries')

    return inner
