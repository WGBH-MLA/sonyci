from requests import post
from requests_oauth2client.auth import BearerToken

from sonyci.config import TOKEN_URL
from sonyci.log import log


def get_token(
    username: str,
    password: str,
    client_id: str,
    client_secret: str,
    token_url: str = TOKEN_URL,
) -> BearerToken:
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
        log.error('Token did not return 200', response.text)
        raise Exception(
            f'Token did not return 200. Returned: {response.status_code}: {response.text}'
        )
    return BearerToken(**response.json())
