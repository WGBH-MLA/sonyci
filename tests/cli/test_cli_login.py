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
def test_bad_login(error_runner):
    result = error_runner.invoke(
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
