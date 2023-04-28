from typer import Option, Typer

from sonyci.log import log

app = Typer(context_settings={'help_option_names': ['-h', '--help']})


def version_callback(value: bool):
    """Print the version of the program and exit."""
    if value:
        from typer import Exit

        from ._version import __version__

        print(f'v{__version__}')

        raise Exit()


@app.command()
def login(
    username: str = Option(
        ..., '--username', '-u', help='Sony CI username.', envvar='CI_USERNAME'
    ),
    password: str = Option(
        ..., '--password', '-p', help='Sony CI password.', envvar='CI_PASSWORD'
    ),
    client_id: str = Option(
        ..., '--client-id', '-c', help='Sony CI client ID.', envvar='CI_CLIENT_ID'
    ),
    client_secret: str = Option(
        ...,
        '--client-secret',
        '-s',
        help='Sony CI client secret.',
        envvar='CI_CLIENT_SECRET',
    ),
):
    """Login to Sony CI."""
    # Save the credentials to config file.
    from requests_oauth2client.tokens import BearerToken, BearerTokenSerializer

    from sonyci.sonyci import get_token

    token: BearerToken = get_token(username, password, client_id, client_secret)
    with open('.token', 'w') as f:
        f.write(BearerTokenSerializer().dumps(token))
        log.success('logged in to Sony CI!')


@app.callback()
def main(
    version: bool = Option(
        None,
        '--version',
        '-v',
        callback=version_callback,
        is_eager=True,
        help='Show the version and exit.',
    ),
    token: str = Option(None, '--token', '-t', help='Sony CI token.', envvar='TOKEN'),
):
    pass


if __name__ == '__main__':
    app()
