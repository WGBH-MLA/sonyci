from typing import Any

from requests_oauth2client import ApiClient, OAuth2Client
from requests_oauth2client.auth import BearerAuth, OAuth2AccessTokenAuth
from requests_oauth2client.tokens import BearerToken

from sonyci.config import Config
from sonyci.log import log
from sonyci.utils import get_token, json


class SonyCi(Config):
    class Config:
        arbitrary_types_allowed = True

    """A SonyCI client."""

    # This will not be needed when we upgrade to pydantic2,
    # we will be able to directly overwrite the @cached_property instance
    t: BearerToken = None

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
        return get_token(
            username=self.username,
            password=self.password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

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

    @property
    def workspaces(self):
        return self.get('workspaces')['items']

    @property
    def workspace(self):
        """Return response of /workspaces/{workspace_id}"""
        return self.get(f'workspaces/{self.workspace_id}')

    @json
    def get(self, *args, **kwargs):
        log.debug(f'GET {args} {kwargs}')
        return self.client.get(*args, **kwargs)

    @json
    def post(self, *args, **kwargs):
        return self.client.post(*args, **kwargs)

    def __call__(self, path: str, **kwds: Any) -> Any:
        """Default action: make GET request to Sony CI."""
        return self.get(path, **kwds)
