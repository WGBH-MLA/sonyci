from json import dumps, loads
from json.decoder import JSONDecodeError
from os import path

from pytest import fixture


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
