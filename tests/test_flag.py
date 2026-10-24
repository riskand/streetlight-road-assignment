# streetlight-road-assignment/tests/test_flag.py
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.flag import combine_reasons


def test_blank_when_no_check_fired():
    assert combine_reasons([pd.Series(["", ""]), pd.Series(["", ""])]).tolist() == ["", ""]


def test_single_reason_is_kept_as_is():
    assert combine_reasons([pd.Series(["", "no light ID"]), pd.Series(["", ""])]).tolist() == ["", "no light ID"]


def test_several_reasons_joined_in_check_order():
    first = pd.Series(["a", "", "x"])
    second = pd.Series(["b", "c", ""])
    assert combine_reasons([first, second]).tolist() == ["a; b", "c", "x"]


def test_index_is_kept():
    reasons = pd.Series(["", "r"], index=[5, 9])
    assert combine_reasons([reasons]).index.tolist() == [5, 9]


def test_no_series_is_an_error():
    with pytest.raises(ValueError):
        combine_reasons([])
