from json import dumps

from requests_oauth2client.tokens import BearerToken, BearerTokenSerializer
from typer import Argument, Context, Exit, Option, Typer
from typing_extensions import Annotated

from sonyci import SonyCi
from sonyci.log import log

app = Typer(context_settings={'help_option_names': ['-h', '--help']})


def version_callback(value: bool):
    """Print the version of the program and exit."""
    if value:
        from ._version import __version__

        print(f'v{__version__}')

        raise Exit()


@app.command()
def login(
    ctx: Context,
    username: str = Option(
        ..., '--username', '-u', help='Sony CI username.', envvar='CI_USERNAME'
    ),
    password: str = Option(
        ..., '--password', '-p', help='Sony CI password.', envvar='CI_PASSWORD'
    ),
    test: bool = Option(False, '--test', '-t', help='Skips saving the token.'),
):
    """Login to Sony CI."""
    from sonyci.utils import get_token

    token: BearerToken = get_token(
        username,
        password,
        ctx.parent.params.get('client_id'),
        ctx.parent.params.get('client_secret'),
    )
    if not test:
        with open('.token', 'w') as f:
            f.write(BearerTokenSerializer().dumps(token))
    log.success('logged in to Sony CI!')


@app.command()
def get(ctx: Context, path: Annotated[str, Argument(..., help='The path to GET')]):
    """Make a GET request to Sony CI."""
    ci = SonyCi(t=ctx.parent.params['token'])
    log.trace(f'GET {path}')
    result = ci(path)
    log.success(result)
    print(dumps(result))


@app.command()
def post(
    ctx: Context,
    path: Annotated[str, Argument(..., help='The path to POST')],
    data: Annotated[str, Argument(..., help='The data to POST')],
):
    """Make a POST request to Sony CI."""
    ci = SonyCi(t=ctx.parent.params['token'])
    log.trace(f'POST {path} {data}')
    result = ci.post(path, data)
    log.success(result)
    print(dumps(result))


@app.command()
def search(
    ctx: Context, query: Annotated[str, Argument(..., help='The query to search for')]
):
    """Search for files in a Sony CI workspace"""
    ci = SonyCi(
        t=ctx.parent.params['token'], workspace_id=ctx.parent.params['workspace_id']
    )
    log.trace(f'search {query}')
    result = ci.workspace_search(query)
    log.success(result)
    print(dumps(result))


@app.callback()
def main(
    ctx: Context,
    version: bool = Option(
        None,
        '--version',
        '-V',
        callback=version_callback,
        is_eager=True,
        help='Show the version and exit.',
    ),
    verbose: bool = Option(None, '--verbose', '-v', help='Show verbose output.'),
    token: str = Option(None, '--token', '-t', help='Sony CI token.', envvar='TOKEN'),
    workspace_id: str = Option(
        None,
        '--workspace-id',
        '-w',
        help='Sony CI workspace ID.',
        envvar='CI_WORKSPACE_ID',
    ),
    client_id: str = Option(
        None, '--client-id', '-c', help='Sony CI client ID.', envvar='CI_CLIENT_ID'
    ),
    client_secret: str = Option(
        None,
        '--client-secret',
        '-s',
        help='Sony CI client secret.',
        envvar='CI_CLIENT_SECRET',
    ),
):
    if not verbose:
        log.remove()
    if not token:  # and if command is not login
        log.debug('no token provided, trying to load from .token')
        try:
            with open('.token') as f:
                token = BearerTokenSerializer().loads(f.read())
                log.debug('loaded token from .token')
                ctx.params['token'] = token
        except FileNotFoundError:
            log.debug('no .token file found')


if __name__ == '__main__':
    app()
