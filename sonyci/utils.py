from requests import post
from requests_oauth2client.tokens import BearerToken, BearerTokenSerializer

from sonyci.config import TOKEN_URL
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
