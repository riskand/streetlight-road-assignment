# streetlight-road-assignment/checks/__init__.py
"""The preconditions, then the validation checks, each run in this order. A new rule is a new file and one line here."""

from checks.base import BaseCheck, BasePrecondition
from checks.duplicate import Duplicate
from checks.far_from_road import FarFromRoad
from checks.geometry import GeometryValid
from checks.lamp_type import LampType
from checks.missing_id import MissingId
from checks.numbering import Numbering
from checks.same_crs import SameCrs
from checks.too_close import TooClose
from checks.unnamed_road import UnnamedRoad
from settings import Settings


def build_preconditions() -> list[BasePrecondition]:
    return [SameCrs()]


def build_checks(settings: Settings) -> list[BaseCheck]:
    """The checks in run order, each given only the values it needs."""
    return [
        GeometryValid(),
        MissingId(),
        Duplicate(),
        Numbering(
            light_pattern=settings.light_pattern,
            pole_pattern=settings.pole_pattern,
            light_base=settings.light_base,
            pole_base=settings.pole_base,
            light_step=settings.light_step,
            pole_step=settings.pole_step,
        ),
        FarFromRoad(max_m=settings.far_from_road_m),
        TooClose(min_m=settings.too_close_m, far_m=settings.far_from_road_m, crs=settings.projected_crs),
        LampType(),
        UnnamedRoad(),
    ]
