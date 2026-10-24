# streetlight-road-assignment/utils/flag.py
"""Combine the reasons of every check into the single flag column."""

import pandas as pd

SEPARATOR = "; "


def combine_reasons(reasons):
    """One Series: each light's non-blank reasons joined with "; ", in the order given.

    reasons is a list of Series with the same index; "" (or NaN) means that check passed.
    The flag is "" when every check passed.
    """
    if not reasons:
        raise ValueError("combine_reasons needs at least one series of reasons")
    table = pd.concat(reasons, axis=1).fillna("")
    return table.apply(lambda row: SEPARATOR.join(reason for reason in row if reason), axis=1)
