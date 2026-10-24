# streetlight-road-assignment/checks/same_crs.py
"""Precondition: both layers must use the same coordinate system."""

import logging

from checks.base import BasePrecondition

logger = logging.getLogger(__name__)


class SameCrs(BasePrecondition):
    """Stop the program if the two layers use different coordinate systems."""

    def run(self, lights, roads) -> None:
        if lights.crs != roads.crs:
            logger.error("lights and roads use different coordinate systems: %s and %s", lights.crs, roads.crs)
            raise SystemExit(1)
        logger.info("lights and roads use the same coordinate system (%s), continuing", lights.crs)
