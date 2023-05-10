from os import environ

from pytest import fixture, mark
from typer.testing import CliRunner

from sonyci import Config
from sonyci.cli import app


@fixture
def runner():
    return CliRunner()


@fixture
def config():
    if environ.get('RECORD'):
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
        ],
    )
    assert result.exit_code == 1
    assert 'invalid_client' in str(result.exception)
