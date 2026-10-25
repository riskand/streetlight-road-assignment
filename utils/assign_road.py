# streetlight-road-assignment/utils/assign_road.py
"""Assign each light to its nearest road, with the distance in metres."""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

DISTANCE_DECIMALS = 1


def project(layer: gpd.GeoDataFrame, crs: str) -> gpd.GeoDataFrame:
    """The layer in the metric CRS."""
    return layer.to_crs(crs)


def nearest_road(point: Point, road_lines: gpd.GeoSeries) -> tuple[int, float]:
    """(position in road_lines, distance) of the nearest road; the first road wins a tie."""
    distances = road_lines.distance(point)
    position = int(distances.values.argmin())
    return position, distances.iloc[position]


def assign_road(lights: gpd.GeoDataFrame, roads: gpd.GeoDataFrame, crs: str) -> pd.DataFrame:
    """DataFrame (lights' index) with road_id, road_name, distance_m of the nearest road.

    Lights with no valid geometry get "" and NaN. Roads with no geometry are ignored.
    Distances are measured in crs, which must be metric.
    """
    points = project(lights, crs).geometry
    road_lines = project(roads[roads.geometry.notna()], crs).reset_index(drop=True)
    assigned = pd.DataFrame(
        {"road_id": "", "road_name": "", "distance_m": float("nan")},
        index=lights.index,
    )
    for index, point in points.items():
        if point is None or road_lines.empty:
            continue
        position, distance = nearest_road(point, road_lines.geometry)
        road = road_lines.iloc[position]
        assigned.loc[index, "road_id"] = road["road_id"]
        assigned.loc[index, "road_name"] = "" if pd.isna(road["road_name"]) else road["road_name"]
        assigned.loc[index, "distance_m"] = round(distance, DISTANCE_DECIMALS)
    return assigned
