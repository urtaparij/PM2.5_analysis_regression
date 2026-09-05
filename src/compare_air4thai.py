import requests
import json
import csv
import math

locations = [
    {"name": "chiangmai", "lat": 18.7883, "lon": 98.9853},
    {"name": "nan", "lat": 18.7756, "lon": 100.7730},
]

air4thai_url = "https://air4thai.pcd.go.th/services/getNewAQI_JSON.php"
print("fetching Air4Thai current station readings")
air4thai_response = requests.get(air4thai_url, verify=False)
air4thai_data = air4thai_response.json()
stations = air4thai_data["stations"]
print("Air4Thai stations returned:", len(stations))

results_file = open("outputs/results/air4thai_comparison.csv", "w", newline="")
results_writer = csv.writer(results_file)
results_writer.writerow(["location", "air4thai_station", "air4thai_distance_deg", "air4thai_pm25", "air4thai_datetime", "openmeteo_pm25", "openmeteo_datetime", "difference_openmeteo_minus_air4thai"])

for loc in locations:
    name = loc["name"]
    lat = loc["lat"]
    lon = loc["lon"]

    best_station = None
    best_dist = 999.0
    for s in stations:
        if s["lat"] == "" or s["long"] == "":
            continue
        slat = float(s["lat"])
        slon = float(s["long"])
        d = ((lat - slat) ** 2 + (lon - slon) ** 2) ** 0.5
        if d < best_dist:
            best_dist = d
            best_station = s

    a4t_pm25_str = best_station["AQILast"]["PM25"]["value"]
    a4t_pm25 = float(a4t_pm25_str)
    a4t_datetime = best_station["AQILast"]["date"] + " " + best_station["AQILast"]["time"]

    aq_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    aq_params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pm2_5",
        "timezone": "Asia/Bangkok",
        "past_days": 1,
        "forecast_days": 1,
    }
    print("fetching Open-Meteo current air quality for", name)
    aq_response = requests.get(aq_url, params=aq_params)
    aq_data = aq_response.json()
    om_times = aq_data["hourly"]["time"]
    om_values = aq_data["hourly"]["pm2_5"]

    target_time = best_station["AQILast"]["date"] + "T" + best_station["AQILast"]["time"]
    om_pm25 = None
    om_matched_time = None
    i = 0
    while i < len(om_times):
        if om_times[i] == target_time:
            om_pm25 = om_values[i]
            om_matched_time = om_times[i]
        i = i + 1

    if om_pm25 is None:
        om_pm25 = om_values[-1]
        om_matched_time = om_times[-1]

    diff = om_pm25 - a4t_pm25

    print(name, "nearest Air4Thai station:", best_station["nameEN"], "distance (deg):", format(best_dist, ".4f"))
    print(name, "Air4Thai PM2.5:", a4t_pm25, "at", a4t_datetime, "(instrument-measured, ground station)")
    print(name, "Open-Meteo PM2.5:", om_pm25, "at", om_matched_time, "(model output, Copernicus CAMS)")
    print(name, "difference (Open-Meteo minus Air4Thai):", format(diff, ".2f"), "ug/m3")
    print("")

    results_writer.writerow([name, best_station["nameEN"], format(best_dist, ".4f"), a4t_pm25, a4t_datetime, om_pm25, om_matched_time, format(diff, ".2f")])

results_file.close()
print("saved outputs/results/air4thai_comparison.csv")
print("done")
