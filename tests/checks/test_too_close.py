# streetlight-road-assignment/tests/checks/test_too_close.py
from frames import lights_frame, roads_frame

from utils import assign_road
from checks.far_from_road import FarFromRoad
from utils.flag import combine_reasons
from checks.too_close import TooClose
from settings import Settings

SETTINGS = Settings()


def spacing_setup(rows):
    roads = roads_frame([("R1", "A St", -200, 0, 200, 0)])
    lights = lights_frame(rows)
    lights[["road_id", "road_name", "distance_m"]] = assign_road.assign_road(lights, roads, SETTINGS.projected_crs)
    return lights, roads


def too_close():
    return TooClose(SETTINGS.too_close_m, SETTINGS.far_from_road_m, SETTINGS.projected_crs)


def test_spacing_marks_both_close_lights():
    lights, roads = spacing_setup([{"x_m": 0, "y_m": 7}, {"x_m": 0.5, "y_m": 7}, {"x_m": 50, "y_m": 7}])
    issues = too_close().run(lights, roads).tolist()
    assert issues[0].endswith("of row 2 on the same road") and issues[0].startswith("within 0.")
    assert issues[1].endswith("of row 1 on the same road")
    assert issues[2] == ""


def test_spacing_ignores_far_flagged_light():
    lights, roads = spacing_setup([{"x_m": 0, "y_m": 7}, {"x_m": 0.5, "y_m": 45}])
    assert too_close().run(lights, roads).tolist() == ["", ""]


def test_spacing_leaves_lights_20m_apart():
    lights, roads = spacing_setup([{"x_m": 0, "y_m": 7}, {"x_m": 20, "y_m": 7}])
    assert too_close().run(lights, roads).tolist() == ["", ""]


def test_spacing_skips_exact_duplicates_but_not_other_close_pairs():
    twin = {"light_id": "SL10007", "pole_id": "P4003", "x_m": 0, "y_m": 7}
    near = {"light_id": "SL10049", "pole_id": "P4021", "x_m": 100, "y_m": 7}
    lights, roads = spacing_setup([twin, dict(twin), near, {**near, "light_id": "SL10567", "x_m": 100.5}])
    issues = too_close().run(lights, roads).tolist()
    assert issues[:2] == ["", ""]
    assert issues[2].endswith("of row 4 on the same road")
    assert issues[3].endswith("of row 3 on the same road")


def test_result_is_the_same_whatever_the_check_order():
    lights, roads = spacing_setup([{"x_m": 0, "y_m": 7}, {"x_m": 0.5, "y_m": 7}, {"x_m": 0.5, "y_m": 45}])
    checks = [FarFromRoad(max_m=SETTINGS.far_from_road_m), too_close()]
    results = []
    for ordered in (checks, checks[::-1]):
        frame = lights.copy()
        reasons = [check.run(frame, roads) for check in ordered]
        results.append(combine_reasons(reasons).tolist())
    assert results[0] == results[1]
    assert results[0][2] == "45.0 m from the nearest road (over 15 m)"
