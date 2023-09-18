from pytest import fixture, mark

from sonyci import Config, SonyCi


@fixture(scope='module')
def ci_config(pytestconfig):
    if pytestconfig.getoption('record'):
        return Config.load('./ci.toml')
    return Config.load('./tests/sonyci/sonyci.toml')


@fixture(scope='module')
def ci(ci_config: Config):
    return SonyCi(**ci_config.model_dump())


@mark.vcr()
def test_token(ci: SonyCi):
    token = ci.token
    assert isinstance(token.access_token, str), 'Access token is not a string'
    assert len(token.access_token) > 0, 'Access token was empty'


@mark.vcr()
def test_workspaces(ci: SonyCi):
    workspaces = ci.workspaces()
    assert isinstance(workspaces, list), 'workspaces is not a list'
    assert len(workspaces) > 0, 'no workspaces found'


@mark.vcr()
def test_workspace(ci: SonyCi):
    workspace = ci.workspace()
    assert isinstance(workspace, dict), 'workspace is not a dict'
    assert 'id' in workspace, 'workspace has no id'


@mark.vcr()
def test_workspace_contents(ci: SonyCi):
    result = ci.workspace_contents()
    assert isinstance(result, list)
    assert result


@mark.vcr()
def test_workspace_empty_search(ci: SonyCi):
    result = ci.workspace_search(query='i am not a guid')
    assert isinstance(result, list)
    assert not result


@mark.vcr()
def test_workspace_search(ci: SonyCi, guid: str):
    assets = ci.workspace_search(guid)
    assert isinstance(assets, list)
    assert len(assets) == 1

    assert guid in assets[0]['name']


@mark.vcr()
def test_asset(ci: SonyCi, asset_id, **kwargs):
    asset = ci.asset(asset_id)
    assert isinstance(asset, dict)
    assert asset['id'] == asset_id


@mark.vcr()
def test_asset_download(ci: SonyCi, asset_id, **kwargs):
    asset = ci.asset_download(asset_id)
    assert isinstance(asset, dict)
    assert asset['id'] == asset_id
