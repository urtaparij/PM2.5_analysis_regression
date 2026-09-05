import requests
import csv
import datetime
import os

env_path = ".env"
if os.path.exists(env_path):
    env_file = open(env_path)
    for line in env_file:
        line = line.strip()
        if line != "" and "=" in line:
            key_part = line.split("=", 1)[0]
            val_part = line.split("=", 1)[1]
            os.environ[key_part] = val_part
    env_file.close()

map_key = os.environ.get("FIRMS_MAP_KEY", "")

locations = [
    {"name": "chiangmai", "lat": 18.7883, "lon": 98.9853},
    {"name": "nan", "lat": 18.7756, "lon": 100.7730},
]

box_deg = 0.5
source = "VIIRS_SNPP_SP"
seasons = [2023, 2024, 2025, 2026]
max_days_per_request = 5

request_count = 0

for loc in locations:
    name = loc["name"]
    lat = loc["lat"]
    lon = loc["lon"]
    west = lon - box_deg
    east = lon + box_deg
    south = lat - box_deg
    north = lat + box_deg
    bbox = str(west) + "," + str(south) + "," + str(east) + "," + str(north)

    out_path = "data/raw/firms_" + name + "_raw.csv"
    out_file = open(out_path, "w", newline="")
    out_writer = csv.writer(out_file)
    header_written = False

    total_rows = 0
    for year in seasons:
        season_start = datetime.date(year, 2, 1)
        season_end = datetime.date(year, 4, 30)
        chunk_start = season_start
        while chunk_start <= season_end:
            days_left = (season_end - chunk_start).days + 1
            chunk_days = min(max_days_per_request, days_left)
            url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/" + map_key + "/" + source + "/" + bbox + "/" + str(chunk_days) + "/" + chunk_start.isoformat()
            print("fetching", name, year, chunk_start.isoformat(), "days", chunk_days)
            response = requests.get(url)
            request_count = request_count + 1
            response_text = response.text.strip()
            if response_text.startswith("Invalid") or response_text.startswith("Error") or response_text == "":
                print("WARNING: request failed:", response_text)
                lines = []
            else:
                lines = response_text.split("\n")
            if len(lines) > 0 and lines[0] != "":
                reader = csv.reader(lines)
                rows = []
                for row in reader:
                    rows.append(row)
                if len(rows) > 0:
                    if header_written == False:
                        out_writer.writerow(rows[0])
                        header_written = True
                    i = 1
                    while i < len(rows):
                        out_writer.writerow(rows[i])
                        total_rows = total_rows + 1
                        i = i + 1
            chunk_start = chunk_start + datetime.timedelta(days=chunk_days)

    out_file.close()
    print("saved", out_path, "rows:", total_rows)

print("total API requests made:", request_count)
print("done")
