# streetlight-road-assignment/tests/test_main.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent / "checks"))

from frames import lights_frame, roads_frame

from checks import build_checks
import logging

import pytest

from main import add_checks, main
from settings import Settings


def test_geometry_reason_and_check_reasons_land_in_one_flag_column():
    settings = Settings()
    roads = roads_frame([("R1", "A St", -200, 0, 200, 0)])
    lights = lights_frame([
        {"light_id": "SL10007", "pole_id": "P4003", "y_m": 7},
        {"light_id": None, "y_m": 7, "x_m": 60},
    ])
    lights["raw_geometry"] = [{"type": "Point", "coordinates": [145.0, -37.8]}, None]
    add_checks(lights, roads, build_checks(settings), settings.projected_crs)
    assert lights["flag"].tolist() == ["", "geometry is missing; no light ID"]


def test_missing_input_file_logs_an_error_naming_the_setting_and_exits_1(monkeypatch, caplog):
    monkeypatch.setenv("LIGHTS_PATH", "data/nope.geojson")
    with caplog.at_level(logging.ERROR):
        with pytest.raises(SystemExit) as exit_info:
            main()
    assert exit_info.value.code == 1
    assert "setting lights_path" in caplog.text
    assert str(Path("data") / "nope.geojson") in caplog.text
