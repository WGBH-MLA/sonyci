![deploy](https://github.com/WGBH-MLA/sonyci/actions/workflows/CI.yml/badge.svg)
[![codecov](https://codecov.io/gh/WGBH-MLA/sonyci/branch/main/graph/badge.svg?token=6J7UUYW9I9)](https://codecov.io/gh/WGBH-MLA/sonyci)
<a href="https://codecov.io/gh/WGBH-MLA/sonyci"><img height=20 src="https://codecov.io/gh/WGBH-MLA/sonyci/branch/main/graphs/tree.svg?token=6J7UUYW9I9"></img></a>

# sonyci

A Sony Ci api client

## Install

```shell
pdm install
```

## Configure

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

Alternate notation: (May not be available in your terminal)

```shell
. .cred
```

## Use

Run the cli with `ci`

```shell
$ ci -h

 Usage: ci [OPTIONS] COMMAND [ARGS]...


╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --version             -V                          Show the version and exit.                             │
│ --verbose             -v                          Show verbose output.                                   │
│ --token               -t      PARSE_BEARER_TOKEN  Sony CI token. [env var: CI_TOKEN] [default: None]     │
│ --workspace-id        -w      TEXT                Sony CI workspace ID. [env var: CI_WORKSPACE_ID]       │
│                                                   [default: None]                                        │
│ --client-id           -c      TEXT                Sony CI client ID. [env var: CI_CLIENT_ID]             │
│                                                   [default: None]                                        │
│ --client-secret       -s      TEXT                Sony CI client secret. [env var: CI_CLIENT_SECRET]     │
│                                                   [default: None]                                        │
│ --install-completion                              Install completion for the current shell.              │
│ --show-completion                                 Show completion for the current shell, to copy it or   │
│                                                   customize the installation.                            │
│ --help                -h                          Show this message and exit.                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────╮
│ asset      Search for files in a Sony CI workspace                                                       │
│ download   Download a file from Sony CI                                                                  │
│ get        Make a GET request to Sony CI.                                                                │
│ login      Login to Sony CI.                                                                             │
│ post       Make a POST request to Sony CI.                                                               │
│ search     Search for files in a Sony CI workspace                                                       │
│ tui                                                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

### Login

```shell
ci login
```

## develop

### pre-commit secret scanning

0. Install [ggshield](https://docs.gitguardian.com/ggshield-docs/getting-started)

```shell
pip install ggshield
# or
brew install gitguardian/tap/ggshield
```

1. Login to gitguardian

```shell
ggshield auth login
```

2. Install the pre-commit hooks

```shell
pre-commit install
```
