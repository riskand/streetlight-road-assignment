# streetlight-road-assignment/tests/test_write.py
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.write import COLUMNS, write_csv


def lights_table(count):
    return pd.DataFrame({
        "row": range(1, count + 1),
        "light_id": [f"SL{10000 + n}" for n in range(count)],
        "pole_id": ["P4000"] * count,
        "lamp_type": ["LED"] * count,
        "road_id": ["R1"] * count,
        "road_name": ["A St"] * count,
        "distance_m": [7.25] * count,
        "flag": [""] * count,
        "raw_geometry": [None] * count,
    })


def read_back(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")


def test_columns_are_the_four_required_first_then_the_rest(tmp_path):
    path = write_csv(lights_table(3), tmp_path / "out" / "result.csv")
    assert list(read_back(path).columns) == COLUMNS
    assert COLUMNS[:4] == ["light_id", "road_id", "distance_m", "flag"]


def test_one_row_per_light_in_file_order_and_folder_created(tmp_path):
    path = write_csv(lights_table(82), tmp_path / "deep" / "result.csv")
    rows = read_back(path)
    assert len(rows) == 82
    assert rows["row"].tolist() == [str(n) for n in range(1, 83)]


def test_missing_values_are_blank_not_nan(tmp_path):
    table = lights_table(2)
    table["distance_m"] = [float("nan"), 3.0]
    table.loc[0, "pole_id"] = None
    path = write_csv(table, tmp_path / "result.csv")
    text = path.read_text(encoding="utf-8")
    assert "nan" not in text.lower()
    assert read_back(path).loc[0, "distance_m"] == ""
    assert read_back(path).loc[0, "pole_id"] == ""


def test_distance_has_one_decimal_and_no_index_column(tmp_path):
    table = lights_table(1)
    table["distance_m"] = [8.0]
    path = write_csv(table, tmp_path / "result.csv")
    assert path.read_text(encoding="utf-8").splitlines()[1].split(",")[2] == "8.0"
    assert read_back(path).columns[0] == "light_id"


def test_text_starting_like_a_formula_gets_a_leading_quote(tmp_path):
    table = lights_table(5)
    table["light_id"] = ["=1+1", "+x", "-x", "@x", "\tx"]
    table["flag"] = ["=bad", "", "", "", "\rx"]
    rows = read_back(write_csv(table, tmp_path / "result.csv"))
    assert rows["light_id"].tolist() == ["'=1+1", "'+x", "'-x", "'@x", "'\tx"]
    assert rows["flag"].tolist() == ["'=bad", "", "", "", "'\rx"]


def test_ordinary_text_and_numbers_are_unchanged(tmp_path):
    table = lights_table(2)
    table["distance_m"] = [-1.5, 7.25]
    rows = read_back(write_csv(table, tmp_path / "result.csv"))
    assert rows["light_id"].tolist() == ["SL10000", "SL10001"]
    assert rows["road_name"].tolist() == ["A St", "A St"]
    assert rows["distance_m"].tolist() == ["-1.5", "7.2"]
    assert rows["row"].tolist() == ["1", "2"]


def test_input_frame_is_not_modified(tmp_path):
    table = lights_table(2)
    table["light_id"] = ["=1+1", "SL2"]
    before = table.copy()
    write_csv(table, tmp_path / "result.csv")
    pd.testing.assert_frame_equal(table, before)
