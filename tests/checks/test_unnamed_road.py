# streetlight-road-assignment/tests/checks/test_unnamed_road.py
import pandas as pd

from checks.unnamed_road import UnnamedRoad


def test_road_name_issue():
    lights = pd.DataFrame({"road_id": ["R1", "R9", ""], "road_name": ["Main St", "", ""]})
    assert UnnamedRoad().run(lights, None).tolist() == ["", "assigned road R9 has no name", ""]
