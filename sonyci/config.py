import tomllib
from os import environ

from pydantic import BaseModel

BASE_URL = 'https://api.cimediacloud.com/'
TOKEN_URL = 'https://api.cimediacloud.com/oauth2/token'


class Config(BaseModel):
    ENV_PREFIX: str = 'CI_'
    TOML_KEY: str = 'sonyci'

    base_url: str = BASE_URL
    token_url: str = TOKEN_URL
    username: str | None = None
    password: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    workspace_id: str | None = None

    @classmethod
    def load(
        cls,
        toml_filename: str | None = None,
        toml_key: str = TOML_KEY,
        env_prefix: str = ENV_PREFIX,
        **kwargs,
    ):
        """
        Returns a new Config instance loaded with data in the following precedence: arguments,
        environment variables, toml file, defaults defined in the Config class.
        """
        if toml_filename:
            from_toml = cls.from_toml(filename=toml_filename, key=toml_key)
        else:
            from_toml = {}
        from_env = cls.from_env(env_prefix)
        params = {**from_toml, **from_env, **kwargs}
        return cls(**params)

    @classmethod
    def from_toml(cls, filename: str, key: str = TOML_KEY) -> dict:
        with open(str(filename), 'rb') as f:
            vals = tomllib.load(f)
        if key:
            return vals.get(key)
        return vals

    @classmethod
    def load_from_toml(cls, filename: str, key: str = TOML_KEY):
        return cls(**cls.from_toml(filename=filename, key=key))

    @classmethod
    def from_env(cls, prefix: str = ENV_PREFIX) -> dict:
        if not prefix:
            return {}

        # Returns a dict of config vars from the environment that begin with `prefix`
        return {
            k[len(prefix) :].lower(): v
            for k, v in environ.items()
            if k.startswith(prefix)
        }
