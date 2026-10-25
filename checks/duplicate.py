# streetlight-road-assignment/checks/duplicate.py
import geopandas as gpd
import pandas as pd

from checks.base import BaseCheck


class Duplicate(BaseCheck):
    """Mark every row that repeats another in light_id, pole_id, lamp_type and geometry."""

    @staticmethod
    def partners(lights: gpd.GeoDataFrame) -> pd.Series:
        """For each light, the row (1-based) of every other light that is an exact duplicate of it.

        An exact duplicate has the same light_id, pole_id, lamp_type and geometry. The list is
        empty when the light has no duplicate. This is the one definition of "exact duplicate",
        shared by Duplicate and TooClose so neither reads the other's result.
        """
        keys = list(zip(
            lights["light_id"], lights["pole_id"], lights["lamp_type"],
            lights.geometry.map(lambda geometry: None if geometry is None else geometry.wkt),
        ))
        rows_by_key = {}
        for index, key in zip(lights["row"], keys):
            rows_by_key.setdefault(key, []).append(index)
        partners = [[other for other in rows_by_key[key] if other != index]
                    for index, key in zip(lights["row"], keys)]
        return pd.Series(partners, index=lights.index)

    def run(self, lights: gpd.GeoDataFrame, roads: gpd.GeoDataFrame) -> pd.Series:
        return self.partners(lights).map(
            lambda others: "duplicate of row " + ", ".join(map(str, others)) if others else "")
