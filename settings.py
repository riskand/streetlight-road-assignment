# streetlight-road-assignment/settings.py
"""The tunable values, read from a .env file with the current values as defaults."""

import logging
import re
from pathlib import Path

from pydantic import FilePath, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
REPO_DIR = Path(__file__).parent
ENV_FILE = REPO_DIR / ".env"


def _one_group_pattern(value):
    """The pattern text if it compiles with exactly one group, else a ValueError."""
    try:
        compiled = re.compile(value)
    except re.error as error:
        raise ValueError(f"not a valid regular expression: {error}")
    if compiled.groups != 1:
        raise ValueError("the pattern must have exactly one group, around the digits")
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", validate_default=True)

    # The numbering link below is a pattern inferred from the data, not a stated rule:
    # light number = light_base + (pole number - pole_base) * light_step / pole_step.
    light_pattern: str = r"SL(\d{5})"
    pole_pattern: str = r"P(\d{4})"
    light_base: int = 10000
    pole_base: int = 4000
    light_step: int = 7
    pole_step: int = 3

    # Chosen inside the gap in the data (nothing between 8.3 m and 45 m), about twice
    # the normal 6 to 8 m set-back of a light from its road.
    far_from_road_m: float = 15

    # Chosen inside the gap in the data (nothing between 0 m and 17.8 m; gaps
    # from 17.8 m up are normal lights near a corner).
    too_close_m: float = 5

    # GDA2020 MGA Zone 55, units are metres.
    projected_crs: str = "EPSG:7855"

    # The input GeoJSON files, which must exist. A relative path is resolved against the
    # repo; an absolute path is used as it is.
    lights_path: FilePath = Path("data/lights.geojson")
    roads_path: FilePath = Path("data/roads.geojson")

    # The result CSV, resolved the same way; the folder is created if missing.
    output_csv: Path = Path("output/light_road_assignment.csv")

    # A standard logging level name.
    log_level: str = "INFO"

    @field_validator("lights_path", "roads_path", "output_csv", mode="before")
    @classmethod
    def _resolve_path(cls, value):
        return REPO_DIR / value

    @field_validator("log_level")
    @classmethod
    def _check_log_level(cls, value):
        name = value.upper()
        if name not in LOG_LEVELS:
            raise ValueError(f"must be one of {', '.join(LOG_LEVELS)}")
        return name

    @field_validator("light_pattern", "pole_pattern")
    @classmethod
    def _check_pattern(cls, value):
        return _one_group_pattern(value)

    @field_validator("light_step", "pole_step", "far_from_road_m", "too_close_m")
    @classmethod
    def _check_positive(cls, value):
        if value <= 0:
            raise ValueError("must be greater than 0")
        return value
