# streetlight-road-assignment/tests/checks/test_far_from_road.py
import pandas as pd

from checks.far_from_road import FarFromRoad
from settings import Settings


def test_distance_issue_threshold():
    lights = pd.DataFrame({"distance_m": [8.3, 15.0, 45.0, float("nan")]})
    assert FarFromRoad(max_m=Settings().far_from_road_m).run(lights, None).tolist() == [
        "", "", "45.0 m from the nearest road (over 15 m)", ""]
