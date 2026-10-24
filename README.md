# Streetlights to roads

This program assigns every streetlight in a small suburb to the road it lights, and flags the ones a person should check.

## Setup

Python 3.12 or later is needed.

macOS or Linux:

```bash
git clone https://github.com/riskand/streetlight-road-assignment.git
cd streetlight-road-assignment
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell; in Command Prompt, activate with `.venv\Scripts\activate.bat`):

```powershell
git clone https://github.com/riskand/streetlight-road-assignment.git
cd streetlight-road-assignment
py -m venv .venv
.venv\Scripts\Activate.ps1
```

## Install requirements

```bash
pip install -r requirements.txt
```

Optionally copy the settings file; it runs with built-in defaults without a `.env`. On macOS or Linux, `cp .env.example .env`; on Windows, `copy .env.example .env`.

## Settings

The numbering pattern, the two distance thresholds, the metric coordinate system, the input and output file paths and the log level are read from a `.env` file with pydantic-settings (see `.env.example` for every name, with its default). Defaults are built in, so the program runs the same with no `.env`.

## Run

```bash
python main.py
```

The result is `output/light_road_assignment.csv`, created on the first run. `output/` is git-ignored, so the CSV is attached separately.

To run the tests: `python -m pytest`.

`main.py` is the entry point. It writes the result to `output/light_road_assignment.csv` (change the path with `OUTPUT_CSV`). It reads `data/lights.geojson` and `data/roads.geojson` (change them with `LIGHTS_PATH` and `ROADS_PATH`); if a setting is invalid, including an input file that does not exist, it logs one ERROR per problem naming the setting and exits with code 1. Relative paths are resolved against the repo and absolute paths are used as they are. The output has one row per light in file order, with `light_id`, `road_id`, `distance_m` and `flag` first, then `road_name`, `pole_id`, `lamp_type` and `row`. The console shows what was read, how many lights were flagged (one line each) and where the CSV went; it goes through logging, and `LOG_LEVEL` (DEBUG, INFO, WARNING, ERROR, CRITICAL; default INFO) sets how much is shown.

## Problem

Two layers for a small, fictional suburb: `roads.geojson` (road centrelines, with `road_id` and `road_name`) and `lights.geojson` (streetlight points, with `light_id`, `pole_id` and `lamp_type`). Each light needs the road it lights and its distance to that road, and a flag wherever the data has an issue or no clearly correct answer.

## What it does

- Reads the two layers and checks they share a coordinate system.
- Projects both layers to GDA2020 MGA Zone 55 (EPSG:7855) so distances are measured in metres.
- Assigns each light to its nearest road.
- Runs a set of checks on the data and writes a plain-words reason to the `flag` column.
- Writes the result to a CSV.

## Output

The result is `output/light_road_assignment.csv`, with one row per input light in file order. The columns are `light_id`, `road_id`, `distance_m` and `flag` first, then `road_name`, `pole_id`, `lamp_type` and `row`. `row` is the light's 1-based position in the input file, used to refer to lights that have no ID or share an ID. Text cells starting with `=`, `+`, `-`, `@`, a tab or a carriage return get a leading quote so a spreadsheet does not run them as formulas.

## Built with

Python, GeoPandas, Shapely, pydantic-settings and pytest.

## Assumptions

Every threshold and the numbering pattern are settings in `.env` (see Settings below).

1. Each light belongs to exactly one road, its nearest. Where a light sits at the join of two segments of the same street, it takes one of them and is not flagged: SL10287 sits at the R01/R02 join of Main St, 7.0 m from each, and is assigned R02.
2. The spacing check compares lights on the same `road_id` only, so a light near a segment join is not compared with the lights on the other segment.
3. The input files carry no CRS, so they are read as WGS84 (EPSG:4326), as the GeoJSON standard (RFC 7946) requires.
4. Distances are measured after projecting both layers to GDA2020 MGA Zone 55 (EPSG:7855), so they are in metres.
5. Far from road means over 15 m. The threshold sits inside a gap in the data (no light between 8.3 m and 45 m) and is about twice the normal 6 to 8 m set-back of a light from its road.
6. Too close means under 5 m apart along the same road, and both lights are flagged. The threshold sits inside a gap in the data (nothing between 0 m and 17.8 m); gaps from 17.8 m up are normal lights near a corner. Lights already flagged as far from the road, and exact duplicates, are left out of this check.
7. A light near a corner is not flagged on that ground alone; it still gets its nearest road.
8. The lamp type check compares each light with the most common type on its assigned road, and only when there is a clear majority (no tie for most common).
9. Light and pole numbers are linked by light number = 10000 + (pole number minus 4000) x 7 / 3. This link is inferred from the data, not a stated rule, so breaking it only raises a flag.
10. The checks only raise a flag. They never change, drop or invent data, and every input row is kept in the output.
11. Rows are numbered from 1 in input file order.
12. The checks judge the lights, not the roads layer. A road problem is reported only through the lights assigned to it.

## Findings in the data

Each layer was checked first: every geometry is valid, neither layer declares a CRS, so both are read as WGS84 (EPSG:4326), and Main St is stored as two segments, R01 and R02. The issues found:

1. **No light ID** at row 2 (pole P4066). The one gap in the light numbering, SL10154, is the number this light should have.
2. **Duplicate:** SL10105 appears twice, identical, at rows 4 and 8.
3. **Two lights on one pole:** SL10567 (row 23) and SL10049 (row 39) are both on pole P4021, 0.6 m apart, at the same point along Birch St. The number SL10567 points to pole P4243, which is missing from the data, so SL10567 is probably a real light recorded on the wrong pole.
4. **Far from road:** SL10014 (row 15) is 45 m from the nearest road; every other light is within 8.3 m.
5. **Lamp type unlike its street:** SL10014 (row 15) and SL10175 (row 16) are LED 17W on Church St, where the rest are LED 33W; SL10350 (row 41) is LED 33W on Oak St, where the rest are LED 17W.
6. **Unnamed, unconnected road:** R09 has no name and connects to no other road. Its lights, SL10070 (row 20) and SL10112 (row 78), are flagged.

In total, 10 of 82 lights are flagged.

## Use of AI

I used Claude Code as a pair throughout, but the process and the decisions were mine. This is how I worked:

### Understanding The Data

I first read the structure of both GeoJSON files myself in my IDE. I then used AI to summarise their content faster: the features in each FeatureCollection, their properties, the geometry types, and that no CRS is declared, so the coordinates are WGS84 longitude and latitude, the GeoJSON default. AI also plotted the files in 2D, so I could see the layout without writing plotting code.

### Pattern Lookup

AI presented the data frames as a simple web page, so I had a readable view without setting up a Jupyter notebook. It was then used to look up the relations between the lights and their streets. It surfaced clear patterns, which I checked against the data:

- **Street layout:** the suburb is a grid, so most roads run east to west or north to south.
- **Lamp type by street:** each street uses one lamp type, matching the road's role: HPS 150W on Main St, LED 33W on Church St and Park Rd, and LED 17W on the local streets.
- **Set-back:** lights sit 6 to 8 m from their road's centreline.
- **Spacing:** along each street, lights are about 50 m apart.
- **Numbering:** light numbers go up in steps of 7 (SL10007 to SL10567) and pole numbers in steps of 3 (P4003 to P4240), and each light's number is tied to its pole: light number = 10000 + (pole number minus 4000) x 7 / 3.

### Find Pattern Break

AI first looked up potential pattern breaks: lights with no ID, lights not assigned to a road, the numbering pattern, the distance to the road, the spacing along each street and the lamp types. I sorted what it found into two kinds of problem: data that is wrong or incomplete, and data that is fine but has no single correct answer, such as a light at a corner. I checked each layer on its own first (schema, missing values, duplicates, ID patterns and geometry), then how the two layers fit together. Each confirmed break became a candidate issue:

- **No ID:** the light on pole P4066 has no `light_id`.
- **Numbering:** SL10567 on pole P4021 breaks the light to pole link; its number points to pole P4243, which is missing from the data. The one gap in the light numbers, SL10154, is the number the light with no ID should have.
- **Duplicate:** SL10105 appears twice, and the two records are identical.
- **Spacing:** SL10049 and SL10567 share pole P4021 and are 0.6 m apart, against the usual 50 m.
- **Set-back:** SL10014 is 45 m from the nearest road, against the usual 6 to 8 m.
- **Lamp type:** SL10014 and SL10175 are LED 17W on Church St, where the rest are LED 33W; SL10350 is LED 33W on Oak St, where the rest are LED 17W.
- **Street layout:** road R09 has no name and connects to no other road.

### Handling Each Issue

I went through the issues one by one and decided how to treat each. My rule for all of them: a check only raises a flag in plain words. It never changes, drops or invents data, so every input light is in the output.

- **No ID:** flagged. The row is kept and no ID is invented, even though SL10154 is the likely one.
- **Numbering:** flagged only. The link is inferred from the data, not a stated rule.
- **Duplicate:** both rows are flagged, each pointing to the other, so a person sees both before removing one.
- **Spacing:** two lights under 5 m apart on the same road are both flagged. I set 5 m inside the gap in the data (nothing between 0 m and 17.8 m). Exact duplicates and lights already flagged as far from the road are left out, because their own checks explain them.
- **Set-back:** a light over 15 m from the nearest road is flagged but still gets that road and distance. I set 15 m inside the gap in the data (nothing between 8.3 m and 45 m).
- **Lamp type:** flagged when a light differs from the most common type on its assigned road. The common type is worked out from the data, and only when there is a clear majority. It never changes the assignment.
- **Street layout:** lights on the unnamed road R09 keep their assignment and are flagged, so a person can name the road.
- **Corner lights:** no check of their own. A light near a corner gets its nearest road like any other light, and if its lamp type does not fit that road, the lamp type check flags it. The gaps between lights near a corner start at 17.8 m, well above the 5 m spacing threshold, so they are not flagged as too close.
- **One road per light:** a stated assumption. A light at the join of two segments of the same street takes one of them and is not flagged.

I decided where the flag lives: on the loaded lights layer itself, as one `flag` column added after the roads are assigned. The CSV and the log only show that column; they never work a flag out.

### Code Design

I chose the structure of the code:

- **Checks that can grow:** the list of rules will grow, so each check is its own class in the `checks` folder, built on one base class with a `run` method that returns one reason per light. A new rule is a new file and one line in the list; nothing else changes. A rule that must stop the run, like the same CRS test, has its own small base.
- **Settings:** the thresholds, the numbering pattern, the CRS, the file paths and the log level are read with pydantic-settings from `.env` and validated in one place, with defaults built in. A threshold can be changed without touching the code.
- **Separation:** `utils` reads the files, assigns the roads, joins the flag reasons and writes the CSV; `checks` judges the data; `settings.py` holds the configuration; `main.py` only wires the steps together.
- **Tests:** every check and step has tests. In real work tests are necessary; for a task this size they may be more than needed, but they show how I work.

### Building

I built it one step at a time, and only the step I had just decided. AI wrote the code and tests for that step to my design; I reviewed it, ran it and checked the output against the data before moving on.

Changes I made along the way:

- **Row numbers:** rows were first numbered from 0. I changed them to start at 1, the way a person counts in a spreadsheet, so a flag that says row 8 points to the eighth light.
- **Raw geometry:** GeoPandas can drop a broken geometry on load, so the reader keeps each feature's original geometry and the geometry check judges that, and no row is lost.
- **Main kept short:** the printing moved out of `main.py`, which now only wires the steps together, and everything on the console goes through logging.
- **One flag column:** the checks first had a column each while I built them; I joined them into the single `flag` column the result needs.
- **Paths in one place:** relative and absolute file paths are resolved only in `settings.py`, which also checks the input files exist, and the files are read as UTF-8, so it runs the same on Windows, macOS and Linux.
