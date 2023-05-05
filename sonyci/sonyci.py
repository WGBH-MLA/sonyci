from functools import cached_property
from typing import Any

from pydantic import BaseModel
from requests_oauth2client import ApiClient, OAuth2Client
from requests_oauth2client.auth import OAuth2AccessTokenAuth
from requests_oauth2client.tokens import BearerToken

from sonyci.config import BASE_URL, TOKEN_URL
from sonyci.utils import get_token


class SonyCi(BaseModel, extra='allow'):
    base_url: str = BASE_URL
    token_url: str = TOKEN_URL
    username: str | None = None
    password: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    workspace_id: str | None = None

    @cached_property
    def oauth(self) -> OAuth2Client:
        return OAuth2Client(
            token_endpoint=self.token_url,
            auth=(self.username, self.password),
            data={
                'grant_type': 'password',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            },
        )

    @cached_property
    def token(self) -> BearerToken:
        return get_token(
            self.username, self.password, self.client_id, self.client_secret
        )

    @cached_property
    def auth(self) -> OAuth2AccessTokenAuth:
        return OAuth2AccessTokenAuth(client=self.oauth, token=self.token)

    @cached_property
    def client(self) -> ApiClient:
        return ApiClient(self.base_url, auth=self.auth)

    @property
    def workspace(self) -> str:
        return f'workspaces/{self.workspace_id}'

    def __call__(self, path: str, **kwds: Any) -> Any:
        """Default action: make GET request to Sony CI."""
        return self.client.get(path, **kwds)
