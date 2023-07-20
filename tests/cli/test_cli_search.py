from json import loads

from pytest import mark

from sonyci.cli import app


@mark.vcr()
def test_empty_search(runner, config):
    result = runner.invoke(
        app,
        [
            '-w',
            config['workspace_id'],
            'search',
            'i am not a guid',
        ],
    )
    assert result.exit_code == 0
    output = loads(result.output)
    assert type(output) is list
    assert not output


@mark.vcr()
def test_guid_search(runner, config, guid):
    result = runner.invoke(
        app,
        [
            '-w',
            config['workspace_id'],
            'search',
            guid,
        ],
    )
    assert result.exit_code == 0
    output = loads(result.output)
    assert type(output) is list
    assert len(output) == 1
    assert guid in output[0]['name']
    assert len(output) == 1
    assert guid in output[0]['name']
