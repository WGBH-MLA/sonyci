import contextlib
import os
from typing import Any
from pydantic import BaseModel
from requests_oauth2client import ApiClient
from requests_oauth2client.auth import BearerAuth
from requests_oauth2client.tokens import BearerToken, BearerTokenSerializer
from requests import post
from sonyci.config import Config
from sonyci.log import log


class SonyCi(BaseModel):
    config: Config
    base_url: str = 'https://api.cimediacloud.com/'
    token_url: str = 'https://api.cimediacloud.com/oauth2/token'

    @property
    def token_from_file(self):
        try:
            with open('.token') as f:
                return BearerTokenSerializer().loads(f.read())
        except FileNotFoundError:
            return None

    def get_new_token(self) -> BearerToken:
        response = post(
            self.token_url,
            auth=(self.config.username, self.config.password),
            data={
                'grant_type': 'password',
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret,
            },
        )
        log.debug(f'token response status: {response.status_code}')
        if response.status_code != 200:
            log.error('Token did not return 200', response.text)
            raise Exception(
                f'Token did not return 200. Returned: {response.status_code}: {response.text}'
            )
        return BearerToken(**response.json())

    @staticmethod
    def delete_token_file():
        with contextlib.suppress(FileNotFoundError):
            os.remove('.token')

    def obtain_new_token_file(self):
        new_token = self.get_new_token()
        with open('.token', 'w') as f:
            f.write(BearerTokenSerializer().dumps(new_token))

    @property
    def token(self) -> BearerToken:
        """Get a token from SonyCI and cache the results."""
        if not self.token_from_file:
            self.obtain_new_token_file()
        return self.token_from_file

    @property
    def bearer_auth(self) -> BearerAuth:
        """Returns a BearerAuth instance with"""
        return BearerAuth(token=self.token)

    @property
    def client(self) -> ApiClient:
        """Create and cache an ApiClient instance.

        Example:
            ```py
            ci.client.get('workspaces')
            ```
        """
        return ApiClient(self.base_url, auth=self.bearer_auth)

    @staticmethod
    def return_response_json(func):
        """
        Decorator for calling .json() on Response objects.
        """

        def inner(*args, **kwargs):
            return func(*args, **kwargs).json()

        return inner

    @property
    def workspaces(self):
        return self.get('workspaces')['items']

    @property
    def workspace(self):
        """Return response of /workspaces/{workspace_id}"""
        return self.get(f'workspaces/{self.config.workspace_id}')

    @return_response_json
    def get(self, *args, **kwargs):
        return self.client.get(*args, **kwargs)

    @return_response_json
    def post(self, *args, **kwargs):
        return self.client.post(*args, **kwargs)

    def __call__(self, path: str, **kwds: Any) -> Any:
        """Default action: make GET request to Sony CI."""
        return self.get(path, **kwds)
