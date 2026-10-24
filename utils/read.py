# streetlight-road-assignment/utils/read.py
"""Read the source files: the raw GeoJSON and the layers built from it."""

import json

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape

def load_geojson(path):
    """Return the raw GeoJSON as a dict using only the standard library."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_geometry(raw):
    """The shapely geometry for a raw GeoJSON geometry dict, or None if it cannot be built."""
    try:
        return shape(raw)
    except Exception:
        return None


def build_layer(geojson):
    """Return a GeoDataFrame with one row per feature, in file order.

    Columns: row (1-based, as a person counts data rows in a spreadsheet), the properties, raw_geometry (the original geometry
    dict, untouched) and geometry (None where shapely cannot build it). The
    loader does not judge the geometry; the GeometryValid check does.
    """
    features = geojson["features"]
    raws = [feature.get("geometry") for feature in features]
    table = pd.DataFrame([feature["properties"] for feature in features])
    table.insert(0, "row", range(1, len(features) + 1))
    table["raw_geometry"] = pd.Series(raws, index=table.index, dtype=object)
    geometries = [build_geometry(raw) for raw in raws]
    return gpd.GeoDataFrame(table, geometry=geometries, crs="EPSG:4326")


def load_layer(path):
    """Return the layer at path as a GeoDataFrame with a raw_geometry column."""
    return build_layer(load_geojson(path))
