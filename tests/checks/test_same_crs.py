# streetlight-road-assignment/tests/checks/test_same_crs.py
import logging

import geopandas as gpd
import pytest
from shapely.geometry import Point

from checks.same_crs import SameCrs


def layer(crs):
    return gpd.GeoDataFrame({"geometry": [Point(0, 0)]}, crs=crs)


def test_same_crs_returns_none_and_logs_info(caplog):
    with caplog.at_level(logging.INFO):
        assert SameCrs().run(layer("EPSG:4326"), layer("EPSG:4326")) is None
    assert caplog.records[0].levelname == "INFO"
    assert "use the same coordinate system (EPSG:4326), continuing" in caplog.text


def test_different_crs_logs_error_naming_both_and_exits(caplog):
    with pytest.raises(SystemExit):
        SameCrs().run(layer("EPSG:4326"), layer("EPSG:3857"))
    assert caplog.records[0].levelname == "ERROR"
    assert "EPSG:4326" in caplog.text
    assert "EPSG:3857" in caplog.text
