# streetlight-road-assignment/checks/unnamed_road.py
import geopandas as gpd
import pandas as pd

from checks.base import BaseCheck


class UnnamedRoad(BaseCheck):
    """Flag a light whose assigned road has no name."""

    def run(self, lights: gpd.GeoDataFrame, roads: gpd.GeoDataFrame) -> pd.Series:
        unnamed = (lights["road_id"] != "") & (lights["road_name"].fillna("").str.strip() == "")
        return pd.Series(
            [f"assigned road {road_id} has no name" if flag else ""
             for road_id, flag in zip(lights["road_id"], unnamed)],
            index=lights.index,
        )
