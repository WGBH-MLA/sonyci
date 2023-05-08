from typing import Any

from requests_oauth2client import ApiClient, OAuth2Client
from requests_oauth2client.auth import BearerAuth, OAuth2AccessTokenAuth
from requests_oauth2client.tokens import BearerToken

from sonyci.config import Config
from sonyci.log import log
from sonyci.utils import get_token


class SonyCi(Config):
    class Config:
        arbitrary_types_allowed = True

    t: BearerToken = None

    def get_token_from_login(self):
        return get_token(
            username=self.username,
            password=self.password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

    @property
    def oauth(self) -> OAuth2Client:
        """Create and cache an OAuth2Client instance."""
        return OAuth2Client(
            token_endpoint=self.token_url,
            auth=(self.username, self.password),
            data={
                'grant_type': 'password',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            },
        )

    @property
    def token(self) -> BearerToken:
        """Get a token from SonyCI and cache the results."""
        if self.t:
            return self.t
        return self.get_token_from_login()

    @property
    def auth(self) -> OAuth2AccessTokenAuth:
        """Create and cache an OAuth2AccessTokenAuth instance.

        This will refresh the token automatically if it is expired.
        """
        if self.client_id and self.client_secret:
            return OAuth2AccessTokenAuth(client=self.oauth, token=self.token)
        return BearerAuth(token=self.token)

    @property
    def client(self) -> ApiClient:
        """Create and cache an ApiClient instance.

        Example:
            ```py
            ci.client.get('workspaces')
            ```
        """
        return ApiClient(self.base_url, auth=self.auth)

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
        return self.get(f'workspaces/{self.workspace_id}')

    @return_response_json
    def get(self, *args, **kwargs):
        return self.client.get(*args, **kwargs)

    @return_response_json
    def post(self, *args, **kwargs):
        return self.client.post(*args, **kwargs)

    def __call__(self, path: str, **kwds: Any) -> Any:
        """Default action: make GET request to Sony CI."""
        return self.get(path, **kwds)
