# streetlight-road-assignment/tests/test_read.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.read import build_layer

GOOD = {"type": "Point", "coordinates": [145.0, -37.8]}
BAD = {"type": "Point", "coordinates": [200.0, -37.8]}
COLLECTION = {
    "features": [
        {"properties": {"light_id": "A"}, "geometry": GOOD},
        {"properties": {"light_id": "B"}, "geometry": BAD},
        {"properties": {"light_id": "C"}, "geometry": None},
    ]
}


def test_one_row_per_feature_in_file_order():
    layer = build_layer(COLLECTION)
    assert len(layer) == 3
    assert layer["row"].tolist() == [1, 2, 3]
    assert layer["light_id"].tolist() == ["A", "B", "C"]


def test_every_row_keeps_its_original_geometry():
    layer = build_layer(COLLECTION)
    assert layer["raw_geometry"].tolist() == [GOOD, BAD, None]


def test_valid_feature_has_a_built_geometry():
    assert build_layer(COLLECTION).iloc[0]["geometry"].geom_type == "Point"


def test_unbuildable_feature_is_kept_with_no_geometry():
    unbuildable = {"type": "LineString", "coordinates": [[145.0, -37.8]]}
    collection = {"features": COLLECTION["features"] + [{"properties": {"light_id": "D"}, "geometry": unbuildable}]}
    layer = build_layer(collection)
    assert len(layer) == 4
    assert layer.iloc[2]["geometry"] is None
    assert layer.iloc[3]["geometry"] is None
    assert layer.iloc[3]["raw_geometry"] == unbuildable


def test_crs_is_wgs84():
    assert build_layer(COLLECTION).crs.to_epsg() == 4326
