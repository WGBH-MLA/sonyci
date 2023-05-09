from os import environ

from pytest import fixture, mark

from sonyci import SonyCi
from sonyci.config import Config


@fixture(scope='module')
def guid():
    return 'cpb-aacip-e4308199588'
    # return Config.load('./tests/sonyci/sonyci.toml')


@fixture(scope='module')
def ci_config():
    if environ.get('RECORD'):
        return Config.load('./ci.toml')
    return Config.load('./tests/sonyci/sonyci.toml')


@fixture(scope='module')
def ci(ci_config: Config):
    return SonyCi(**ci_config.dict())


@mark.vcr()
def test_token(ci: SonyCi):
    token = ci.token
    assert type(token.access_token) is str, 'Access token is not a string'
    assert len(token.access_token) > 0, 'Access token was empty'


@mark.vcr()
def test_workspaces(ci: SonyCi):
    workspaces = ci.workspaces()
    assert type(workspaces) == list, 'workspaces is not a list'
    assert len(workspaces) > 0, 'no workspaces found'


@mark.vcr()
def test_workspace(ci: SonyCi):
    workspace = ci.workspace()
    assert type(workspace) == dict, 'workspace is not a dict'
    assert 'id' in workspace, 'workspace has no id'


def test_workspace_contents(ci: SonyCi):
    result = ci.workspace_contents()
    assert type(result) is list
    assert result


def test_workspace_empty_search(ci: SonyCi):
    result = ci.workspace_search(query='i am not a guid')
    assert type(result) is list
    assert not result


def test_workspace_search(ci: SonyCi):
    assets = ci.workspace_search(guid)
    assert len(assets) == 1

    assert guid in assets[0]['name']

    item_names = [i['name'] for i in assets['items']]
    assert guid in assets['items']
    assert guid in item_names
