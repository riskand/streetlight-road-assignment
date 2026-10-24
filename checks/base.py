# streetlight-road-assignment/checks/base.py
"""The shape every check shares."""

from abc import ABC, abstractmethod

import pandas as pd


class BaseCheck(ABC):
    """One validation rule. It gives each light one plain-words reason, or "" when fine."""

    @abstractmethod
    def run(self, lights, roads) -> pd.Series:
        """One reason per light, "" when fine, aligned to lights.index."""


class BasePrecondition(ABC):
    """One rule about the whole dataset, not about a single light.

    Unlike BaseCheck, which marks each light with a reason and never stops the
    program, a precondition answers once for both layers and stops the run when
    the data cannot be processed.
    """

    @abstractmethod
    def run(self, lights, roads) -> None:
        """Raise SystemExit with a plain-words message when the data cannot be
        processed. Return None when it can."""
