# streetlight-road-assignment/checks/lamp_type.py
import geopandas as gpd
import pandas as pd

from checks.base import BaseCheck


class LampType(BaseCheck):
    """Flag a light whose lamp type differs from its road's single most common type."""

    def run(self, lights: gpd.GeoDataFrame, roads: gpd.GeoDataFrame) -> pd.Series:
        issues = pd.Series("", index=lights.index)
        assigned = lights[(lights["road_id"] != "") & lights["lamp_type"].notna()]
        for road_id, group in assigned.groupby("road_id"):
            counts = group["lamp_type"].value_counts()
            if len(counts) > 1 and counts.iloc[0] == counts.iloc[1]:
                continue
            common = counts.index[0]
            name = group["road_name"].iloc[0] or road_id
            for index in group.index[group["lamp_type"] != common]:
                issues[index] = f"lamp {group.at[index, 'lamp_type']}, the rest of {name} uses {common}"
        return issues
