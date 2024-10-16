from requests import post
from requests_oauth2client.tokens import BearerToken, BearerTokenSerializer

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


def get_token_from_file(filename: str = '.token'):
    with open(filename) as f:
        return BearerTokenSerializer().loads(f.read())


def save_token_to_file(token: BearerToken, filename: str = '.token'):
    with open(filename, 'w') as f:
        f.write(BearerTokenSerializer().dumps(token))


def json(func):
    """Decorator for calling .json() on Response objects."""

    def inner(*args, **kwargs):
        return func(*args, **kwargs).json()

    return inner


def retry(func):
    """Decorator for retrying a function call after a rate limit error."""
    from requests import HTTPError

    def inner(*args, **kwargs):
        tries: int = 0
        max_tries: int = 5
        while tries < max_tries:
            try:
                return func(*args, **kwargs)
            except HTTPError as e:
                if e.response.status_code != 429:
                    log.error(f'HTTPError {e.response.status_code}: {e}')
                    raise e
                from time import sleep

                # Get the retry-after header, if it exists
                retry_after = e.response.headers.get('Retry-After')
                if not retry_after:
                    log.error('No Retry-After header found')
                    raise e
                log.warning(f'Rate limited. Retrying after {retry_after} seconds...')
                sleep(int(retry_after + 1))
                tries += 1
        log.error(f'Failed after {max_tries} tries')
        raise RetryError(f'Failed after {max_tries} tries')

    return inner
