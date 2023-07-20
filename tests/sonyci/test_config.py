from os import environ

from pytest import fixture

from sonyci import Config


@fixture(
    scope='module',
    params=[
        {'filename': './tests/sonyci/sonyci.toml'},
        {'filename': './tests/sonyci/sonyci_no_key.toml', 'key': None},
        {
            'filename': './tests/sonyci/sonyci_different_key.toml',
            'key': 'different_key',
        },
    ],
)
def dict_from_toml(request):
    """Parameterized fixture returning dict of values from given toml file, under the given toml key"""
    return Config.from_toml(**request.param)


def test_from_toml(dict_from_toml):
    """Returns a dict of config values from a given toml file under a given toml key"""
    assert dict_from_toml['username'] == 'test username'
    assert dict_from_toml['password'] == 'test password'
    assert dict_from_toml['client_id'] == 'test client id'
    assert dict_from_toml['client_secret'] == 'test client secret'


def test_load_precedence():
    """Returns a Config instance loaded with data merged from different sources"""
    environ['CI_USERNAME'] = 'username from environment'
    config = Config.load(
        toml_filename='./tests/sonyci/sonyci.toml', password='password from arg'
    )
    assert config.username == 'username from environment'
    assert config.password == 'password from arg'
    assert config.client_id == 'test client id'
