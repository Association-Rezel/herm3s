"""Environment definitions for the back-end."""

from os import getenv
from dotenv import load_dotenv

__all__ = ["EnvError", "ENV"]


class EnvError(OSError):
    """Any error related to environment variables."""


class MissingEnvError(EnvError):
    """An environment variable is missing."""

    def __init__(self, key: str) -> None:
        """An environment variable is missing."""
        super().__init__(f"{key} is not set")


def get_or_raise(key: str) -> str:
    """Get value from environment or raise an error."""
    value = getenv(key)
    if not value:
        raise MissingEnvError(key)
    return value


def get_or_none(key: str) -> str | None:
    """Get value from environment or return None."""
    value = getenv(key)
    if not value:
        return None
    return value


def get_or_default(key: str, default: str) -> str:
    """Get value from environment or return default."""
    value = getenv(key)
    if not value:
        return default
    return value


class Env:  # pylint: disable=too-many-instance-attributes
    """Check environment variables types and constraints."""

    deploy_env: str

    db_uri: str
    db_name: str

    ptah_releases_base_url: str
    gitlab_ptah_access_token: str

    temp_generated_box_configs_dir: str

    def __init__(self) -> None:
        """Load all variables."""

        # If we are in a kubernetes pod, we need to load vault secrets and relevant .env file
        # Check if KUBERNETES_SERVICE_HOST is set
        if getenv("KUBERNETES_SERVICE_HOST"):
            load_dotenv("/vault/secrets/env")
            load_dotenv(f".env.{getenv('DEPLOY_ENV')}")

        # Else, env variables are already loaded via docker compose

        self.db_uri = get_or_raise("DB_URI")
        self.db_name = get_or_raise("DB_NAME")
        self.ptah_releases_base_url = get_or_raise("PTAH_RELEASES_BASE_URL")
        self.gitlab_ptah_access_token = get_or_raise("GITLAB_PTAH_ACCESS_TOKEN")
        self.temp_generated_box_configs_dir = get_or_raise(
            "TEMP_GENERATED_BOX_CONFIGS_DIR"
        )

        if self.temp_generated_box_configs_dir[-1] != "/":
            self.temp_generated_box_configs_dir += "/"

        if self.ptah_releases_base_url[-1] != "/":
            self.ptah_releases_base_url += "/"


ENV = Env()
