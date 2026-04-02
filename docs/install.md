# Install

This guide will walk you through the installation process for the `sonyci` package. It can be installed with `pip` or `uv`

## (Option 1) Install with pip

```sh
pip install sonyci
```

## (Option 2) Install with uv

[uv](https://docs.astral.sh/uv/) is used as the packaging manager. It can be installed with `pip install uv`.

### Clone the repository::

```sh
git clone https://github.com/WGBH-MLA/sonyci.git
cd sonyci
```

### Create a virtual environment

```sh
uv venv
```

### Activate your virtual environment

```sh
source .venv/bin/activate
```

!!! info "Deactivate"

    To deactivate the virtual environmet, run the `deactivate` command.

    ```sh
    deactivate
    ```

### Install

Install the project with development dependencies:

```sh
uv sync
```

## Login

The first time you run the application, you will need to get an access token. You can do this with the `login` command:

```sh
ci login
```

### Credentials

You will need to provide your `username` and `password`, as well as your `client_id` and `client_secret`. These can be provided as command line options, or (recommended) as `ENVIRONMENT_VARIABLES`:

Create a file called `.cred` with the following contents, and add your credentials:

```sh
export CI_USERNAME=
export CI_PASSWORD=
export CI_CLIENT_ID=
export CI_CLIENT_SECRET=
export CI_WORKSPACE_ID=
```

!!! abstract inline end "Dot notation"

    Alternate notation for `source` (may not be available in your terminal):

    ```sh
    . .cred
    ```

Activate the variables:

```sh
source .cred
```

!!! abstract "Check ennvironment variables"

    To check your environment variables are stored, run:

    ```sh
    echo $CI_USERNAME
    ```

    If your username does not appear, you may need to run the `source` command again.

Otherwise, you can now login and get an access token:

```sh
ci login
```

This will save a file called `.token` in the current directory. This file will be used to authenticate future requests, and you do not need to login again until the token expires.

## Run the application

Now you are ready to run the application:

```sh
ci -h
```

See the [CLI reference](../reference/cli) for more details.

## Development

Additional development scripts are available in the `pyproject.toml` file. You can run them with `uv run <script_name>`. For example, to run the tests:

```sh
uv run test
```

### Available scripts

- `test`: Run the tests
- `lint`: Run the linter, autofix fixable issues
- `format`: Format the code
- `docs`: Build the documentation
