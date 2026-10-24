# streetlight-road-assignment/tests/checks/frames.py
"""Small lights and roads frames for the check tests."""

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point

LON, LAT = 145.0, -37.8
METRE_LON = 1 / 88000  # about one metre of longitude here
METRE_LAT = 1 / 111000


def lights_frame(rows):
    """rows: dicts with optional light_id, pole_id, lamp_type, x_m, y_m (metres from origin)."""
    table = pd.DataFrame({
        "row": range(1, len(rows) + 1),
        "light_id": [r.get("light_id") for r in rows],
        "pole_id": [r.get("pole_id") for r in rows],
        "lamp_type": [r.get("lamp_type", "LED") for r in rows],
    })
    points = [Point(LON + r.get("x_m", 0) * METRE_LON, LAT + r.get("y_m", 0) * METRE_LAT) for r in rows]
    return gpd.GeoDataFrame(table, geometry=points, crs="EPSG:4326")


def roads_frame(roads):
    """roads: (road_id, road_name, x1_m, y1_m, x2_m, y2_m)."""
    table = pd.DataFrame({"road_id": [r[0] for r in roads], "road_name": [r[1] for r in roads]})
    lines = [
        LineString([(LON + r[2] * METRE_LON, LAT + r[3] * METRE_LAT),
                    (LON + r[4] * METRE_LON, LAT + r[5] * METRE_LAT)])
        for r in roads
    ]
    return gpd.GeoDataFrame(table, geometry=lines, crs="EPSG:4326")
