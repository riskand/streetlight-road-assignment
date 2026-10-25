# streetlight-road-assignment/main.py
"""Entry point: read both layers and add the road and one flag column to the lights."""

import logging
import sys

import geopandas as gpd
import pandas as pd
from pydantic import ValidationError

from utils import assign_road, read
from checks.base import BaseCheck
from checks import build_checks, build_preconditions
from utils.flag import combine_reasons
from settings import Settings
from utils.write import write_csv

LOG_FORMAT = "%(levelname)s %(message)s"
logger = logging.getLogger(__name__)


def load_settings() -> Settings:
    """The settings; if any is invalid, log one ERROR per problem and exit 1."""
    try:
        return Settings()
    except ValidationError as error:
        logging.basicConfig(format=LOG_FORMAT)
        for problem in error.errors():
            logger.error("setting %s: %s (%s)", problem["loc"][0], problem["msg"], problem["input"])
        sys.exit(1)


def add_checks(lights: gpd.GeoDataFrame, roads: gpd.GeoDataFrame, checks: list[BaseCheck], crs: str) -> None:
    """Assign each light its road, then fold every check's reason into flag."""
    lights[["road_id", "road_name", "distance_m"]] = assign_road.assign_road(lights, roads, crs)
    reasons = [check.run(lights, roads) for check in checks]
    lights["flag"] = combine_reasons(reasons)


def log_flagged(lights: gpd.GeoDataFrame) -> None:
    """One INFO line per flagged light: its row in the file, its id and the reason."""
    flagged = lights[lights["flag"] != ""]
    logger.info("%d of %d lights flagged", len(flagged), len(lights))
    for _, light in flagged.iterrows():
        logger.info("row %d %s: %s", light["row"], "(no id)" if pd.isna(light["light_id"]) else light["light_id"], light["flag"])


def main() -> None:
    settings = load_settings()
    logging.basicConfig(level=settings.log_level, format=LOG_FORMAT)
    lights = read.load_layer(settings.lights_path)
    roads = read.load_layer(settings.roads_path)
    logger.info("read %d lights and %d roads", len(lights), len(roads))

    for precondition in build_preconditions():
        precondition.run(lights, roads)

    add_checks(lights, roads, build_checks(settings), settings.projected_crs)
    log_flagged(lights)
    logger.info("wrote %s", write_csv(lights, settings.output_csv))


if __name__ == "__main__":
    main()
