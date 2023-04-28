from typer import Option, Typer

app = Typer(context_settings={'help_option_names': ['-h', '--help']})


def version_callback(value: bool):
    """Print the version of the program and exit."""
    if value:
        from typer import Exit

        from ._version import __version__

        print(f'v{__version__}')

        raise Exit()


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
):
    pass


if __name__ == '__main__':
    app()
