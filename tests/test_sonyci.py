from pytest import fixture, mark

from sonyci import SonyCi
from sonyci.config import Config


@fixture(scope='module')
def ci_config():
    # return Config.load('./tests/sonyci/sonyci.toml')
    return Config.load('./ci.toml')


@fixture(scope='module')
def ci(ci_config: Config):
    # Ensure all specs can without an existing .token file.
    SonyCi.delete_token_file()
    return SonyCi(config=ci_config)


@mark.vcr()
def test_token(ci: SonyCi):
    token = ci.token
    assert type(token.access_token) is str, 'Access token is not a string'
    assert len(token.access_token) > 0, 'Access token was empty'


@mark.vcr()
def test_workspaces(ci: SonyCi):
    workspaces = ci.workspaces
    assert type(workspaces) == list, 'workspaces is not a list'
    assert len(workspaces) > 0, 'no workspaces found'


@mark.vcr()
def test_workspace(ci: SonyCi):
    workspace = ci.workspace
    assert type(workspace) == dict, 'workspace is not a dict'
    assert 'id' in workspace, 'workspace has no id'
