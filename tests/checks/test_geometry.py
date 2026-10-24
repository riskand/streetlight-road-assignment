# streetlight-road-assignment/tests/checks/test_geometry.py
import pandas as pd

from checks.geometry import GeometryValid

POINT = {"type": "Point", "coordinates": [145.0, -37.8]}
LINE = {"type": "LineString", "coordinates": [[145.0, -37.8], [145.1, -37.9]]}


def reasons(*geometries):
    lights = pd.DataFrame({"raw_geometry": pd.Series(geometries, dtype=object)})
    return GeometryValid().run(lights, None).tolist()


def reason(geometry):
    return reasons(geometry)[0]


def test_good_point_passes():
    assert reason(POINT) == ""


def test_good_line_passes():
    assert reason(LINE) == ""


def test_null_geometry_flagged():
    assert "missing" in reason(None)


def test_any_declared_type_is_valid_if_it_builds():
    polygon = {"type": "Polygon", "coordinates": [[[145.0, -37.8], [145.1, -37.8], [145.1, -37.9], [145.0, -37.8]]]}
    assert reason(polygon) == ""


def test_missing_type_flagged():
    assert "cannot be built" in reason({"coordinates": [145.0, -37.8]})


def test_one_point_line_cannot_be_built():
    assert "cannot be built" in reason({"type": "LineString", "coordinates": [[145.0, -37.8]]})


def test_empty_coordinates_flagged():
    assert reason({"type": "Point", "coordinates": []}) != ""


def test_zero_length_line_flagged():
    assert "zero length" in reason({"type": "LineString", "coordinates": [[145.0, -37.8], [145.0, -37.8]]})


def test_out_of_range_longitude_flagged():
    assert "valid degree range" in reason({"type": "Point", "coordinates": [200.0, -37.8]})


def test_nan_flagged():
    assert "NaN" in reason({"type": "Point", "coordinates": [float("nan"), -37.8]})


def test_one_reason_per_feature_in_order():
    result = reasons(POINT, None, POINT)
    assert [bool(r) for r in result] == [False, True, False]
