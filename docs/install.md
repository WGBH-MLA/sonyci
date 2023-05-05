# Install

### Clone the repository::

```shell
git clone https://github.com/WGBH-MLA/sonyci.git
cd sonyci
```

### Install with PDM

[PDM](https://pdm.fming.dev/) is used as the packaging manager. It can be installed with `pip install pdm`.

Install the project with development dependencies:

```shell
pdm install
```

Activate your virtual environment

```shell
$(pdm venv activate)
```

!!! note "What is `$(pdm venv activate)`?"

    `pdm venv activate` outputs the command needed to activate your virtual environment.

    The `$()` wrapper evaluates it in your current shell context.

??? abstract "Install with venv"

    If PDM is not available, it can also be installed with pip. It is recommeneded to install to a virtual environment using `venv`:

    ```shell
    python3 -m venv .venv
    source .venv/bin/activate
    ```

    Install the package

    ```shell
    pip install .
    ```

!!! info "Deactivate"

    To deactivate the virtual environmet, run the `deactivate` command.

    ```shell
    deactivate
    ```

### Login

The first time you run the application, you will need to get an access token. You can do this with the `login` command:

```shell
ci login
```

#### Credentials

You will need to provide your `username` and `password`, as well as your `client_id` and `client_secret`. These can be provided as command line options, or (recommended) as `ENVIRONMENT_VARIABLES`:

Create a file called `.cred` with the following contents, and add your credentials:

```shell
export CI_USERNAME=
export CI_PASSWORD=
export CI_CLIENT_ID=
export CI_CLIENT_SECRET=
export CI_WORKSPACE_ID=
```

Activate the variables:

```shell
source .cred
```

!!! abstract "Dot notation"

    Alternate notation (may not be available in your terminal):

    ```shell
    . .cred
    ```

Now you can login and get an access token:

```shell
ci login
```

This will save a file called `.token` in the current directory. This file will be used to authenticate future requests, and you do not need to login again until the token expires.

## Run the application

Now you are ready to run the application:

```shell
ci -h
```

See the [CLI reference](../reference/cli) for more details.
