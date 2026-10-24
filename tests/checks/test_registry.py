# streetlight-road-assignment/tests/checks/test_registry.py
from checks import build_checks, build_preconditions
from checks.base import BaseCheck, BasePrecondition
from settings import Settings

CHECKS = build_checks(Settings())
PRECONDITIONS = build_preconditions()


def test_every_check_is_a_base_check():
    assert all(isinstance(check, BaseCheck) for check in CHECKS)


def test_check_classes_are_unique():
    names = [type(check).__name__ for check in CHECKS]
    assert len(names) == len(set(names))


def test_every_precondition_is_a_base_precondition_and_not_a_check():
    assert all(isinstance(p, BasePrecondition) for p in PRECONDITIONS)
    assert not any(p in CHECKS for p in PRECONDITIONS)
