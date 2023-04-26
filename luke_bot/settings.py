import dataclasses
import logging
import os
from types import UnionType
from typing import Any, Literal, Self, TypeVar, cast, get_args, get_origin

from dotenv import load_dotenv

logger = logging.getLogger()

T = TypeVar("T")


def coerce_type(value: str, to_type: type[T]) -> T:
    new_value: Any
    origin = get_origin(to_type)
    if origin is Literal:
        args: tuple[str, ...] = get_args(to_type)
        if value not in args:
            raise ValueError(f"{value} not valid for Literal{[*args]}")
        new_value = value
    elif origin is UnionType:
        types: tuple[type[T], ...] = get_args(to_type)
        for t in types:
            try:
                new_value = coerce_type(value, t)
                break
            except NotImplementedError:
                continue
        else:
            raise NotImplementedError
    elif origin is None and issubclass(to_type, (str, int, float)):
        new_value = to_type(value)
    elif to_type is None:
        new_value = None
    else:
        raise NotImplementedError
    return cast(T, new_value)


@dataclasses.dataclass(kw_only=True)
class Settings:
    """Defines the environment variables required to run the bot."""

    GG_TOKEN: str
    GG_PLAYER_ID: int
    PLAYER_NAME: str
    DISCORD_TOKEN: str
    DISCORD_CHANNEL_ID: int
    DEPLOYED_ENVIRONMENT: Literal["dev", "test", "prod"]
    BOT_POLLING_PERIOD: int = 30
    DEFAULT_GAME_ID: int = 1386
    LOG_FILEPATH: str | None = None
    LOG_LEVEL: int | Literal[
        "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"
    ] = logging.DEBUG

    @classmethod
    def from_environment(cls) -> Self:
        logger.info("Checking environment variables...")
        load_dotenv()
        settings_dict = {
            f.name: coerce_type(v, f.type)
            for f in dataclasses.fields(cls)
            if (v := os.getenv(f.name)) is not None
        }
        settings_ = cls(**settings_dict)
        logger.info("Environment variables validated")
        return settings_


settings = Settings.from_environment()
