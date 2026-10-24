# streetlight-road-assignment/tests/checks/test_duplicate.py
from frames import lights_frame

from checks.duplicate import Duplicate


def test_duplicate_rows_point_to_each_other():
    rows = [
        {"light_id": "SL10007", "pole_id": "P4003"},
        {"light_id": "SL10014", "pole_id": "P4006"},
        {"light_id": "SL10007", "pole_id": "P4003"},
    ]
    assert Duplicate().run(lights_frame(rows), None).tolist() == [
        "duplicate of row 3", "", "duplicate of row 1"]


def test_same_id_but_different_position_is_not_a_duplicate():
    rows = [{"light_id": "SL10007", "pole_id": "P4003"},
            {"light_id": "SL10007", "pole_id": "P4003", "x_m": 50}]
    assert Duplicate().run(lights_frame(rows), None).tolist() == ["", ""]
