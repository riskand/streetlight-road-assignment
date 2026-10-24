# streetlight-road-assignment/checks/geometry.py
import math

import pandas as pd
from shapely.geometry import shape

from checks.base import BaseCheck

MAX_LON = 180
MAX_LAT = 90
LINE_TYPES = ("LineString", "MultiLineString")


class GeometryValid(BaseCheck):
    """Reasons from judging the original geometry in raw_geometry, never fixing or dropping it.

    Each feature is checked against the type it declares itself.
    """

    @staticmethod
    def _flatten(coordinates):
        """Yield every [lon, lat] pair in a nested coordinates list."""
        if coordinates and isinstance(coordinates[0], (int, float)):
            yield coordinates
            return
        for part in coordinates:
            yield from GeometryValid._flatten(part)

    @staticmethod
    def _coordinate_reasons(coordinates):
        """Reasons for NaN coordinates or coordinates outside the valid degree range."""
        reasons = []
        pairs = list(GeometryValid._flatten(coordinates))
        if any(math.isnan(value) for pair in pairs for value in pair):
            reasons.append("coordinates are not numbers (NaN)")
        elif any(abs(lon) > MAX_LON or abs(lat) > MAX_LAT for lon, lat, *_ in pairs):
            reasons.append("coordinates outside the valid degree range")
        return reasons

    @staticmethod
    def _build_reasons(geometry):
        """Reasons from trying to build the declared geometry with shapely."""
        try:
            built = shape(geometry)
        except Exception:
            return ["geometry cannot be built from its coordinates"]
        if built.is_empty:
            return ["geometry is empty"]
        if built.geom_type in LINE_TYPES and built.length == 0:
            return ["line has zero length"]
        return []

    @staticmethod
    def _reason(geometry):
        """"" if the geometry passes, else the reasons joined with "; "."""
        if geometry is None:
            return "geometry is missing"
        reasons = GeometryValid._build_reasons(geometry)
        try:
            reasons += GeometryValid._coordinate_reasons(geometry["coordinates"])
        except (KeyError, TypeError, ValueError):
            pass
        return "; ".join(reasons)

    def run(self, lights, roads):
        return pd.Series(
            [self._reason(geometry) for geometry in lights["raw_geometry"]],
            index=lights.index,
        )
