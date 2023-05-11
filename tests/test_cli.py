from json import loads

from pytest import fixture, mark
from typer.testing import CliRunner

from sonyci import Config
from sonyci.cli import app


@fixture
def runner():
    return CliRunner()


@fixture
def error_runner():
    return CliRunner(mix_stderr=False)


@fixture
def config(pytestconfig):
    if pytestconfig.getoption('record'):
        return Config.from_toml('./ci.toml')
    return Config.from_toml('./tests/sonyci/sonyci.toml')


@mark.vcr()
def test_login(runner, config):
    result = runner.invoke(
        app,
        [
            'login',
            '--username',
            config['username'],
            '--password',
            config['password'],
            '--client-id',
            config['client_id'],
            '--client-secret',
            config['client_secret'],
            '--test',
        ],
    )
    assert result.exit_code == 0
    assert not result.stdout


@mark.vcr()
def test_bad_login(runner):
    result = runner.invoke(
        app,
        [
            'login',
            '--username',
            'test',
            '--password',
            'test',
            '--client-id',
            'test',
            '--client-secret',
            'test',
            '--test',
        ],
    )
    assert result.exit_code == 1
    assert 'invalid_client' in str(result.exception)


def test_missing_username(runner):
    result = runner.invoke(
        app,
        [
            'login',
            '--password',
            'test',
            '--client-id',
            'test',
            '--client-secret',
            'test',
        ],
    )
    assert result.exit_code == 2
    assert '--username' in result.stdout


@mark.vcr(allow_playback_repeats=True)
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
