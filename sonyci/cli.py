from json import dumps, loads
from pathlib import Path
from typing import Optional
from urllib.request import urlretrieve

from requests_oauth2client.tokens import BearerToken, BearerTokenSerializer
from typer import Argument, Context, Exit, Option, Typer
from typer.main import get_group
from typing_extensions import Annotated

from sonyci import SonyCi
from sonyci.log import log
from sonyci.types import ProxyType
from sonyci.utils import save_token_to_file

app = Typer(context_settings={'help_option_names': ['-h', '--help']})


def parse_bearer_token(token: str) -> BearerToken:
    """Parse a bearer token from a json string."""
    return BearerToken(loads(token))


def version_callback(value: bool):
    """Print the version of the program and exit."""
    if value:
        from ._version import __version__

        print(f'v{__version__}')

        raise Exit()


class ProxyNotFoundError(Exception):
    """Raised when a specific proxy is not found."""


try:
    from trogon import Trogon

    @app.command()
    def tui(ctx: Context):
        Trogon(get_group(app), click_context=ctx).run()

except ImportError:
    pass


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
        save_token_to_file(token, '.token')
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
    data=Argument(help='The data to POST'),
):
    """Make a POST request to Sony CI."""
    ci = SonyCi(t=ctx.parent.params['token'])
    data = loads(data)
    log.debug(f'POST {path} {data}')
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


@app.command()
def download(
    ctx: Context,
    id: Annotated[str, Argument(..., help='The SonyCi ID of the file to download')],
    proxy: Annotated[ProxyType, Option('--proxy', '-p', help='Download ')] = None,
    output: Annotated[
        Optional[Path],
        Option('--output', '-o', help='The path to download the file to'),
    ] = None,
):
    """Download a file from Sony CI"""
    ci = SonyCi(t=ctx.parent.params['token'])
    log.trace(f'download id: {id} proxy: {proxy} output: {output}')
    result = ci.asset_download(id)
    link = result['location']
    if proxy:
        for p in result['proxies']:
            if p['type'] == proxy.value:
                log.debug(f'found proxy {proxy.value}')
                link = p['location']
                break
        # Check if matching proxy was found. Raise an exception if not found.
        if link == result['location']:
            raise ProxyNotFoundError(f'proxy {proxy} not found')

    log.trace(f'link: {link}')
    filename = output or Path(link).name.split('?')[0]
    log.debug(f'downloading {id} to {filename}')
    urlretrieve(link, filename)
    log.success(f'downloaded {id} to {filename}')


@app.command()
def asset(
    ctx: Context,
    asset: Annotated[str, Argument(..., help='The asset ID to search for')],
):
    """Search for files in a Sony CI workspace"""
    ci = SonyCi(
        t=ctx.parent.params['token'], workspace_id=ctx.parent.params['workspace_id']
    )
    log.trace(f'asset {asset}')
    result = ci.asset(asset)
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
    token: Annotated[
        BearerToken,
        Option(
            '--token',
            '-t',
            parser=parse_bearer_token,
            help='Sony CI token.',
            envvar='CI_TOKEN',
        ),
    ] = None,
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
