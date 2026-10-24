# streetlight-road-assignment/utils/write.py
"""Write the result CSV."""

COLUMNS = ["light_id", "road_id", "distance_m", "flag", "road_name", "pole_id", "lamp_type", "row"]
DISTANCE_FORMAT = "%.1f"
FORMULA_STARTS = ("=", "+", "-", "@", "\t", "\r")


def quote_formulas(value):
    """Prefix a single quote to text a spreadsheet would run as a formula."""
    if isinstance(value, str) and value.startswith(FORMULA_STARTS):
        return "'" + value
    return value


def write_csv(lights, path):
    """Write one row per light, in COLUMNS order, to the full path given; return it.

    Missing values are blank cells and distance_m has one decimal. Text cells that start with =, +, -, @,
    a tab or a carriage return get a leading quote. The folder is created if missing.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    table = lights[COLUMNS].copy()
    for column in table.select_dtypes(include=["object", "string"]).columns:
        table[column] = table[column].map(quote_formulas)
    table.to_csv(path, index=False, na_rep="", float_format=DISTANCE_FORMAT, encoding="utf-8")
    return path
