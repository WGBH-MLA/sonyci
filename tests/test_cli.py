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
            '--client-id',
            config['client_id'],
            '--client-secret',
            config['client_secret'],
            'login',
            '--username',
            config['username'],
            '--password',
            config['password'],
        ],
    )
    assert result.exit_code == 0
    assert not result.stdout


@mark.vcr()
def test_bad_login(runner):
    result = runner.invoke(
        app,
        [
            '--client-id',
            'test',
            '--client-secret',
            'test',
            'login',
            '--username',
            'test',
            '--password',
            'test',
        ],
    )
    assert result.exit_code == 1
    assert 'invalid_client' in str(result.exception)


def test_missing_username(runner):
    result = runner.invoke(
        app,
        [
            '--client-id',
            'test',
            '--client-secret',
            'test',
            'login',
            '--password',
            'test',
        ],
    )
    assert result.exit_code == 2
    assert '--username' in result.stdout
