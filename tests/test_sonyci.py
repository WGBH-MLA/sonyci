from pytest import fixture, mark

from sonyci import SonyCi


@fixture(scope='module')
def ci():
    return SonyCi(
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
