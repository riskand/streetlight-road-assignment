# streetlight-road-assignment/tests/checks/test_missing_id.py
from frames import lights_frame

from checks.missing_id import MissingId


def test_id_issue():
    lights = lights_frame([{"light_id": "SL10007"}, {"light_id": None}, {"light_id": "  "}])
    assert MissingId().run(lights, None).tolist() == ["", "no light ID", "no light ID"]
