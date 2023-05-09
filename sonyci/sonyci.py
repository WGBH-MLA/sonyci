from typing import Any

from pydantic import BaseModel
from requests_oauth2client import ApiClient, OAuth2Client
from requests_oauth2client.auth import OAuth2AccessTokenAuth
from requests_oauth2client.tokens import BearerToken

from sonyci.config import BASE_URL, TOKEN_URL
from sonyci.utils import get_token


class SonyCi(BaseModel, extra='allow'):
    """SonyCI API client

    Attributes:
        username (str, optional): SonyCI username.
        password (str): SonyCI password.
        client_id (str): SonyCI client ID.
        client_secret (str): SonyCI client secret.
        workspace_id (str): SonyCI workspace ID.
        token (BearerToken): SonyCI token.

    """

    base_url: str = BASE_URL
    token_url: str = TOKEN_URL
    username: str | None = None
    password: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    workspace_id: str | None = None

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
        return get_token(
            self.username, self.password, self.client_id, self.client_secret
        )

    @property
    def auth(self) -> OAuth2AccessTokenAuth:
        """Create and cache an OAuth2AccessTokenAuth instance.

        This will refresh the token automatically if it is expired.
        """
        return OAuth2AccessTokenAuth(client=self.oauth, token=self.token)

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
    def workspace(self) -> str:
        """Return the workspace prefix for API calls."""
        return f'workspaces/{self.workspace_id}'

    def __call__(self, path: str, **kwds: Any) -> Any:
        """Default action: make GET request to Sony CI."""
        return self.client.get(path, **kwds)
