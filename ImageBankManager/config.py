import configparser
from pathlib import Path
from re import Pattern
from typing import List

from environs import Env
from pydantic import BaseModel, ConfigDict


class Config(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True
    )

    MAX_LABELS: int
    ALLOWED_MIME_TYPES: List[str]
    MIME_TYPE_REGEX: Pattern[str] = r"(?i)^image/[a-z0-9\-+.]+$"

    SECRET_KEY: str
    ALLOWED_HOSTS: List[str]
    DB_URL: str


def load_config(cfg_path: Path, env_path: Path = Path(".env")) -> Config:
    env = Env()
    env.read_env(env_path)

    parser = configparser.ConfigParser()
    parser.read(cfg_path)

    return Config(
        MAX_LABELS=parser.getint("models.image", "MAX_LABELS"),
        ALLOWED_MIME_TYPES=parser.get("upload", "ALLOWED_MIME_TYPES").split(","),
        SECRET_KEY=env.str("SECRET_KEY"),
        ALLOWED_HOSTS=env.list("ALLOWED_HOSTS"),
        DB_URL=env.str("DB_URL")
    )


config = load_config(Path("./settings.cfg"))
