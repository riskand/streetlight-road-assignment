# streetlight-road-assignment/tests/checks/test_numbering.py
from frames import lights_frame

from checks import build_checks
from checks.numbering import Numbering
from settings import Settings


def numbering():
    return next(c for c in build_checks(Settings()) if isinstance(c, Numbering))


def test_numbering_match():
    lights = lights_frame([{"light_id": "SL10007", "pole_id": "P4003"}])
    assert numbering().run(lights, None).tolist() == [""]


def test_numbering_mismatch_with_existing_pole():
    rows = [{"light_id": "SL10007", "pole_id": "P4006"}, {"light_id": "SL10014", "pole_id": "P4003"}]
    assert numbering().run(lights_frame(rows), None).tolist() == [
        "light ID does not match pole ID; its number points to pole P4003",
        "light ID does not match pole ID; its number points to pole P4006",
    ]


def test_numbering_mismatch_with_missing_pole():
    lights = lights_frame([{"light_id": "SL10567", "pole_id": "P4021"}])
    assert numbering().run(lights, None).tolist() == [
        "light ID does not match pole ID; its number points to pole P4243, "
        "which is missing from the data"]


def test_numbering_skips_null_and_unparseable_ids():
    rows = [{"light_id": None, "pole_id": "P4066"}, {"light_id": "X1", "pole_id": "P4003"}]
    assert numbering().run(lights_frame(rows), None).tolist() == ["", ""]
