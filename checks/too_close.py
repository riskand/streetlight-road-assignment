# streetlight-road-assignment/checks/too_close.py
import geopandas as gpd
import pandas as pd

from utils.assign_road import project
from checks.base import BaseCheck
from checks.duplicate import Duplicate


class TooClose(BaseCheck):
    """Flag both lights of each consecutive pair under min_m apart along a road.

    Lights further than far_m from their road are left out before measuring, and so are
    exact duplicates (see Duplicate.partners), which the duplicate check already explains.
    Needs road_id and distance_m.
    """

    def __init__(self, min_m: float, far_m: float, crs: str) -> None:
        # far_m is the same distance as FarFromRoad.max_m, kept separate so the checks
        # do not depend on each other or on their order.
        self.min_m = min_m
        self.far_m = far_m
        self.crs = crs

    def _close_pairs(self, positions: list[float], rows: list[int]) -> list[tuple[int, int, float]]:
        """Consecutive (row, other row, gap) where the gap is under min_m."""
        ordered = sorted(zip(positions, rows))
        return [
            (a_row, b_row, b_pos - a_pos)
            for (a_pos, a_row), (b_pos, b_row) in zip(ordered, ordered[1:])
            if b_pos - a_pos < self.min_m
        ]

    def run(self, lights: gpd.GeoDataFrame, roads: gpd.GeoDataFrame) -> pd.Series:
        lines = project(roads, self.crs).set_index("road_id").geometry
        points = project(lights, self.crs).geometry
        issues = pd.Series("", index=lights.index)
        is_duplicate = Duplicate.partners(lights).map(bool)
        candidates = lights[
            (lights["road_id"] != "") & ~(lights["distance_m"] > self.far_m) & ~is_duplicate
        ]
        for road_id, group in candidates.groupby("road_id"):
            positions = [lines[road_id].project(points[i]) for i in group.index]
            for a, b, gap in self._close_pairs(positions, list(group.index)):
                for here, other in ((a, b), (b, a)):
                    issues[here] = (
                        f"within {gap:.1f} m of row {lights.at[other, 'row']}"
                        " on the same road"
                    )
        return issues
