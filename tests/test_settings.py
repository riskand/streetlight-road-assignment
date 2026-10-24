# streetlight-road-assignment/tests/test_settings.py
import sys
from pathlib import Path

import pandas as pd
import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parent.parent))

from checks import build_checks
from checks.far_from_road import FarFromRoad
from settings import REPO_DIR, Settings


def far_check(settings):
    return next(c for c in build_checks(settings) if isinstance(c, FarFromRoad))


def test_defaults_load_without_an_env_file(monkeypatch):
    monkeypatch.chdir("/")
    settings = Settings(_env_file=None)
    assert settings.light_pattern == r"SL(\d{5})"
    assert settings.pole_pattern == r"P(\d{4})"
    assert (settings.light_base, settings.pole_base) == (10000, 4000)
    assert (settings.light_step, settings.pole_step) == (7, 3)
    assert settings.far_from_road_m == 15
    assert settings.too_close_m == 5
    assert settings.projected_crs == "EPSG:7855"


def test_environment_variable_overrides_a_default_and_the_check_honours_it(monkeypatch):
    monkeypatch.setenv("FAR_FROM_ROAD_M", "20")
    settings = Settings()
    assert settings.far_from_road_m == 20
    lights = pd.DataFrame({"distance_m": [10.0, 17.0, 25.0]})
    issues = far_check(settings).run(lights, None)
    assert issues.tolist() == ["", "", "25.0 m from the nearest road (over 20 m)"]


@pytest.mark.parametrize("name", ["LIGHT_STEP", "POLE_STEP"])
def test_step_of_zero_is_rejected(monkeypatch, name):
    monkeypatch.setenv(name, "0")
    with pytest.raises(ValidationError):
        Settings()


@pytest.mark.parametrize("name", ["FAR_FROM_ROAD_M", "TOO_CLOSE_M"])
def test_threshold_of_zero_is_rejected(monkeypatch, name):
    monkeypatch.setenv(name, "0")
    with pytest.raises(ValidationError):
        Settings()


@pytest.mark.parametrize("name", ["LIGHT_PATTERN", "POLE_PATTERN"])
@pytest.mark.parametrize("value", [r"SL\d{5}", r"(S)(L)", "SL(", ])
def test_pattern_without_exactly_one_group_is_rejected(monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(ValidationError):
        Settings()


def test_log_level_defaults_to_info_and_accepts_lowercase(monkeypatch):
    assert Settings(_env_file=None).log_level == "INFO"
    monkeypatch.setenv("LOG_LEVEL", "debug")
    assert Settings().log_level == "DEBUG"


def test_unknown_log_level_is_rejected(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "LOUD")
    with pytest.raises(ValidationError):
        Settings()


def test_output_csv_default_resolves_to_the_repo():
    assert Settings(_env_file=None).output_csv == REPO_DIR / "output" / "light_road_assignment.csv"


def test_input_path_defaults_resolve_to_the_repo():
    settings = Settings(_env_file=None)
    assert settings.lights_path == REPO_DIR / "data" / "lights.geojson"
    assert settings.roads_path == REPO_DIR / "data" / "roads.geojson"


def test_relative_path_resolves_to_the_repo_and_absolute_is_kept(monkeypatch, tmp_path):
    absolute = tmp_path / "roads.geojson"
    absolute.write_text("{}")
    monkeypatch.setenv("LIGHTS_PATH", str(Path("data") / "roads.geojson"))
    monkeypatch.setenv("ROADS_PATH", str(absolute))
    settings = Settings()
    assert settings.lights_path == REPO_DIR / "data" / "roads.geojson"
    assert settings.roads_path == absolute


def test_missing_input_file_is_rejected(monkeypatch):
    monkeypatch.setenv("ROADS_PATH", str(Path("data") / "nope.geojson"))
    with pytest.raises(ValidationError):
        Settings()
