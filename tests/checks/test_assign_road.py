# streetlight-road-assignment/tests/checks/test_assign_road.py
from frames import lights_frame, roads_frame

from utils import assign_road
from settings import Settings

CRS = Settings().projected_crs


def test_nearest_road_and_distance_in_metres():
    roads = roads_frame([("R1", "A St", -100, 0, 100, 0), ("R2", "B St", -100, 20, 100, 20)])
    lights = lights_frame([{"x_m": 0, "y_m": 6}, {"x_m": 0, "y_m": 14}])
    assigned = assign_road.assign_road(lights, roads, CRS)
    assert assigned["road_id"].tolist() == ["R1", "R2"]
    assert assigned["road_name"].tolist() == ["A St", "B St"]
    assert all(abs(d - e) < 0.2 for d, e in zip(assigned["distance_m"], [6, 6]))


def test_tie_goes_to_first_road_and_empty_geometry_gets_no_assignment():
    roads = roads_frame([("R1", "A", -100, 0, 100, 0), ("R2", "B", -100, 0, 100, 0)])
    lights = lights_frame([{"y_m": 10}, {}])
    lights.loc[1, "geometry"] = None
    assigned = assign_road.assign_road(lights, roads, CRS)
    assert assigned["road_id"].tolist() == ["R1", ""]
    assert assigned["distance_m"].isna().tolist() == [False, True]
