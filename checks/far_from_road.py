# streetlight-road-assignment/checks/far_from_road.py
import pandas as pd

from checks.base import BaseCheck


class FarFromRoad(BaseCheck):
    """Flag a light further than max_m from its nearest road (needs distance_m)."""

    def __init__(self, max_m):
        self.max_m = max_m

    def run(self, lights, roads):
        far = lights["distance_m"] > self.max_m
        return pd.Series(
            [f"{d} m from the nearest road (over {self.max_m:g} m)" if f else ""
             for d, f in zip(lights["distance_m"], far)],
            index=lights.index,
        )
