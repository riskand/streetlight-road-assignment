# streetlight-road-assignment/checks/numbering.py
import re

import geopandas as gpd
import pandas as pd

from checks.base import BaseCheck


class Numbering(BaseCheck):
    """Flag a light whose light_id and pole_id break the inferred numbering link."""

    def __init__(
        self, light_pattern: str, pole_pattern: str, light_base: int, pole_base: int, light_step: int, pole_step: int
    ) -> None:
        # The numbering link is a pattern inferred from the data, not a stated rule:
        # light number = light_base + (pole number - pole_base) * light_step / pole_step.
        self.light_pattern = re.compile(light_pattern)
        self.pole_pattern = re.compile(pole_pattern)
        self.light_base = light_base
        self.pole_base = pole_base
        self.light_step = light_step
        self.pole_step = pole_step

    @staticmethod
    def parse_number(pattern: re.Pattern[str], value: object) -> int | None:
        """The digits of an id as an int, or None when the id does not fit the pattern."""
        match = pattern.fullmatch(value) if isinstance(value, str) else None
        return int(match.group(1)) if match else None

    def _expected_pole_number(self, light_number: int) -> int | None:
        """The pole number the light number points to, or None when it is not a whole pole."""
        scaled = (light_number - self.light_base) * self.pole_step
        if scaled % self.light_step:
            return None
        return self.pole_base + scaled // self.light_step

    def _numbering_reason(self, light_id: object, pole_id: object, known_poles: set[str]) -> str:
        light = self.parse_number(self.light_pattern, light_id)
        pole = self.parse_number(self.pole_pattern, pole_id)
        if light is None or pole is None:
            return ""
        expected = self._expected_pole_number(light)
        if expected == pole:
            return ""
        reason = "light ID does not match pole ID"
        if expected is None:
            return reason
        expected_id = f"P{expected:04d}"
        reason += f"; its number points to pole {expected_id}"
        if expected_id not in known_poles:
            reason += ", which is missing from the data"
        return reason

    def run(self, lights: gpd.GeoDataFrame, roads: gpd.GeoDataFrame) -> pd.Series:
        known_poles = set(lights["pole_id"].dropna())
        return pd.Series(
            [self._numbering_reason(light, pole, known_poles)
             for light, pole in zip(lights["light_id"], lights["pole_id"])],
            index=lights.index,
        )
