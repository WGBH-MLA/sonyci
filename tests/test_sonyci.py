from pytest import fixture, mark

from sonyci import SonyCi


@fixture(scope='module')
def ci():
    return SonyCi(
        username='username',
        password='password',
        client_id='client_id',
        client_secret='client_secret',
        workspace_id='f44132c2393d470c88b9884f45877ebb',
    )


@mark.vcr()
def test_token(ci):
    token = ci.token
    assert type(token.access_token) is str, 'Access token is not a string'
    assert len(token.access_token) > 0, 'Access token was empty'


@mark.vcr()
def test_workspace(ci):
    response = ci.client.get(f'workspaces/{ci.workspace_id}')
    assert response.status_code == 200, 'Workspace did not return 200'
    assert response.json()['id'] == ci.workspace_id, 'Workspace id did not match'
