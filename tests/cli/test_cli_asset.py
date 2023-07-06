from json import loads

from pytest import mark

from sonyci.cli import app


@mark.vcr()
def test_asset_search(runner, asset_id):
    result = runner.invoke(app, ['asset', asset_id])
    assert result.exit_code == 0
    asset = loads(result.output)
    assert type(asset) is dict
    assert asset['id'] == asset_id
