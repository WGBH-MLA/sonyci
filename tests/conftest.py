from json import dumps, loads
from json.decoder import JSONDecodeError
from os import environ, path

from pytest import fixture, mark
from requests_oauth2client.tokens import BearerToken
from typer.testing import CliRunner

from sonyci import Config


def clean_response(response: dict):
    """Replace secrets in response body with dummy values."""
    try:
        body = loads(response['body']['string'].decode())
    except JSONDecodeError:
        return response
    if 'access_token' in body:
        body['access_token'] = 'DUMMY_ACCESS_TOKEN'
    if 'refresh_token' in body:
        body['refresh_token'] = 'DUMMY_REFRESH_TOKEN'
    response['body']['string'] = dumps(body).encode()
    return response


@fixture(scope='module')
def vcr_config(request):
    return {
        # Save cassettes in tests/vhs/<module_name>/<test_name>.yaml
        'cassette_library_dir': path.join(
            path.dirname(path.abspath(__file__)), 'vhs', request.module.__name__
        ),
        # Replace the Authorization request header with "DUMMY" in cassettes
        'filter_headers': [('authorization', 'Bearer DUMMY')],
        # Replace secrets in request body
        'filter_post_data_parameters': [
            ('client_id', 'FAKE_CLIENT_ID'),
            ('client_secret', 'FAKE_CLIENT_SECRET'),
        ],
        # Replace secrets in response body
        'before_record_response': clean_response,
    }


def pytest_addoption(parser):
    parser.addoption('--record', action='store_true', default=False)
    parser.addoption(
        '--no_ci',
        action='store_true',
        help='skips CI tests',
    )


def pytest_configure(config):
    config.addinivalue_line('markers', 'slow: mark test as slow to run')


def pytest_collection_modifyitems(config, items):
    if config.getoption('--no_ci'):
        skip_ci = mark.skip(reason='skipping CI tests')
        for item in items:
            if 'no_ci' in item.keywords:
                item.add_marker(skip_ci)


@fixture
def guid() -> str:
    return Config.from_toml('./tests/sonyci/guid.toml')['guid']


@fixture
def token() -> BearerToken:
    return dumps(
        BearerToken(
            access_token='FakeAccessToken', refresh_token='FakeRefreshToken'
        ).as_dict()
    )


# CLI fixtures
@fixture
def runner(token, pytestconfig):
    # If we're not recording, use a dummy token
    if not pytestconfig.getoption('record'):
        environ['CI_TOKEN'] = token
    return CliRunner()


@fixture
def error_runner():
    return CliRunner(mix_stderr=False)


@fixture
def config(pytestconfig):
    if pytestconfig.getoption('record'):
        return Config.from_toml('./ci.toml')
    return Config.from_toml('./tests/sonyci/sonyci.toml')


@fixture
def asset_id():
    return '554544ceaf6b4c94a4a06cee5bc1f39f'
