from pytest import fixture, mark
from requests_oauth2client.tokens import BearerToken

from sonyci import SonyCi


class FakeSonyCi(SonyCi):
    def token(self) -> BearerToken:
        return BearerToken(
            access_token='fake_token',
            token_type='bearer',
            expires_in=3600,
            refresh_token='fake_refresh_token',
        )


@fixture(scope='module')
def ci():
    return FakeSonyCi(
        username='username',
        password='password',
        client_id='client_id',
        client_secret='client_secret',
        workspace_id='051303c1c1d24da7988128e6d2f56aa9',
    )


# @mark.vcr()
# def test_get_token(ci):
#     response = ci.get_token()
#     assert response.json()['id'] == ci.workspace_id, 'Workspace id did not match'


@mark.vcr()
def test_workspace(ci):
    response = ci.client.get(f'workspaces/{ci.workspace_id}')
    assert response.status_code == 200, 'Workspace did not return 200'
    assert response.json()['id'] == ci.workspace_id, 'Workspace id did not match'
