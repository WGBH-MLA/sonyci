from functools import cached_property

from pydantic import BaseModel
from requests import post
from requests_oauth2client import ApiClient, OAuth2Client
from requests_oauth2client.auth import OAuth2AccessTokenAuth
from requests_oauth2client.tokens import BearerToken


class SonyCi(BaseModel):
    base_url: str = 'https://api.cimediacloud.com/'
    token_url: str = 'https://api.cimediacloud.com/oauth2/token'
    username: str
    password: str
    client_id: str
    client_secret: str
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
    def auth(self) -> OAuth2AccessTokenAuth:
        return OAuth2AccessTokenAuth(client=self.oauth, token=self.token)

    @cached_property
    def client(self) -> ApiClient:
        return ApiClient(self.base_url, auth=self.auth)

    @cached_property
    def token(self) -> BearerToken:
        response = post(
            self.token_url,
            auth=(self.username, self.password),
            data={
                'grant_type': 'password',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            },
        )
        assert response.status_code == 200, 'Token did not return 200'
        return BearerToken(**response.json())

    @property
    def workspace(self):
        return f'workspaces/{self.workspace_id}'
