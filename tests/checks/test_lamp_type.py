# streetlight-road-assignment/tests/checks/test_lamp_type.py
import pandas as pd

from checks.lamp_type import LampType


def lamp_frame(road_id, lamps, name="Church St"):
    return pd.DataFrame({"road_id": road_id, "road_name": name, "lamp_type": lamps})


def test_lamp_issue_flags_the_odd_one_out():
    lights = lamp_frame("R1", ["LED 33W", "LED 33W", "LED 17W"])
    assert LampType().run(lights, None).tolist() == [
        "", "", "lamp LED 17W, the rest of Church St uses LED 33W"]


def test_lamp_issue_not_flagged_on_a_tie_for_first():
    assert LampType().run(lamp_frame("R9", ["A", "B"], name=""), None).tolist() == ["", ""]


def test_lamp_issue_uses_road_id_when_unnamed():
    lights = lamp_frame("R9", ["A", "A", "B"], name="")
    assert LampType().run(lights, None).tolist()[2] == "lamp B, the rest of R9 uses A"
