# PM2.5 in Northern Thailand: from raw data to a recommendation

DS-270702 Data Science Programming, MSc Data Science, Chiang Mai University — Homework 4.

Compares PM2.5 in Chiang Mai (basin terrain) vs Nan (mountainous terrain, upland agricultural burning) and predicts tomorrow's daily mean PM2.5 (regression).

## Setup

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Requires Python 3.10+.

## How to run, in order

```
python src/fetch_data.py
python src/fetch_firms.py
python src/prepare_data.py
python src/analyse.py
python src/model.py
```

- `fetch_data.py` downloads hourly PM2.5/pollutant and weather data for both locations from the Open-Meteo Air Quality API and Archive API (2023-01-01 to the run date), and writes raw CSVs to `data/raw/`.
- `fetch_firms.py` downloads NASA FIRMS fire hotspot detections for both locations (burn seasons 2023-2026) into `data/raw/`. Requires a free FIRMS MAP_KEY (https://firms.modis.gov/api/map_key/) placed in a local `.env` file as `FIRMS_MAP_KEY=your_key_here` (not committed — see `.gitignore`). This step is optional; it only supports the Part D discussion in the report and is not used by `model.py`.
- `prepare_data.py` joins each location's pollutant and weather data on timestamp, drops the fetch-date (which mixes forecast and observed hours), aggregates hourly data to daily, and writes `data/processed/{location}_daily.csv`.
- `analyse.py` produces the figures in `outputs/figures/` and descriptive statistics in `outputs/results/`.
- `model.py` trains a persistence baseline and a linear regression model (per location) to predict tomorrow's daily mean PM2.5, using a time-ordered train/test split and TimeSeriesSplit cross-validation, and writes metrics to `outputs/results/`.

Re-running `fetch_data.py` and `fetch_firms.py` on a later date will produce different files, because more days of data will have accumulated since the original run (2023-01-01 to run-date is always the requested range).

## Repository layout

```
README.md
requirements.txt
src/
  fetch_data.py       downloads raw data, writes to data/raw/
  fetch_firms.py       downloads NASA FIRMS fire hotspot data, writes to data/raw/
  prepare_data.py      cleaning, joining, feature construction
  analyse.py            figures and descriptive statistics
  model.py               baseline, training, evaluation
data/
  raw/                    exactly what the API returned
  processed/              what was fed to the model
outputs/
  figures/                fig01_*.png ... fig08_*.png
  results/                metrics and descriptive-statistics CSVs
report/
  report.pdf
```

## AI usage disclosure

See the final page of `report/report.pdf`.
