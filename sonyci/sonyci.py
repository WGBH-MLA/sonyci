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

    def workspaces(self) -> list:
        return self.get('workspaces')['items']

    def workspace(self) -> dict:
        """Return response of /workspaces/{workspace_id}"""
        return self.get(f'workspaces/{self.workspace_id}')

    def workspace_contents(self, **kwargs) -> list:
        """Returns items form the workspace"""
        return self.get(f'workspaces/{self.workspace_id}/contents', params=kwargs)[
            'items'
        ]

    def workspace_search(self, query: str | None = None, **kwargs) -> list:
        """Performs a search of a workspace and returns the items found"""
        if len(query) > 20:
            query = query[-20:]
        if query:
            kwargs['query'] = query
        if not kwargs.get('kind'):
            kwargs['kind'] = 'asset'
        return self.get(f'workspaces/{self.workspace_id}/search', params=kwargs)[
            'items'
        ]

    def asset(self, asset_id: str, **kwargs) -> dict:
        return self.get(f'/assets/{asset_id}', params=kwargs)

    def asset_download(self, asset_id: str, **kwargs) -> dict:
        return self.get(f'/assets/{asset_id}/download', params=kwargs)

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
