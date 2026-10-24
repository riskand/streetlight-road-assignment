# streetlight-road-assignment/checks/missing_id.py
import pandas as pd

from checks.base import BaseCheck


class MissingId(BaseCheck):
    """Reason "no light ID" where light_id is null or blank."""

    @staticmethod
    def _is_blank(value):
        return pd.isna(value) or str(value).strip() == ""

    def run(self, lights, roads):
        blank = lights["light_id"].map(self._is_blank)
        return pd.Series(blank.map({True: "no light ID", False: ""}), index=lights.index)
