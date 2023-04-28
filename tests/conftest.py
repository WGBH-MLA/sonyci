from os import path

from pytest import fixture


@fixture(scope='module')
def vcr_cassette_dir(request):
    # Put all cassettes in tests/vhs/{module}/{test}.yaml
    return path.join(
        path.dirname(path.abspath(__file__)), 'vhs', request.module.__name__
    )


@fixture(scope='module')
def vcr_config(request):
    return {
        # Replace the Authorization request header with "DUMMY" in cassettes
        'filter_headers': [('authorization', 'Bearer DUMMY')],
    }
