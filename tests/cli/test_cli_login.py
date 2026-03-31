from os import environ as env

from pytest import mark

from sonyci.cli import app


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
            '--client-id',
            'test',
            '--client-secret',
            'test',
            'login',
            '--username',
            'test',
            '--password',
            'test',
            '--test',
        ],
    )
    assert result.exit_code == 1
    assert 'invalid_client' in str(result.exception)


@mark.skipif(
    env.get('CI_USERNAME') is not None,
    reason='CI_USERNAME env var set. Not checking for missing username error when config is provided through env vars',
)
def test_missing_username(runner, pytestconfig):
    if pytestconfig.getoption('record'):
        mark.skip(
            'This is testing the error handling of typer when missing required options and should not run in record mode when using env vars for config'
        )
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
    assert result.exit_code != 0
    assert '-username' in result.stderr
    assert 'Missing option' in result.stderr
