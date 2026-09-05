import requests
import csv
import datetime

locations = [
    {"name": "chiangmai", "lat": 18.7883, "lon": 98.9853},
    {"name": "nan", "lat": 18.7756, "lon": 100.7730},
]

start_date = "2023-01-01"
end_date = datetime.date.today().isoformat()

for loc in locations:
    name = loc["name"]
    lat = loc["lat"]
    lon = loc["lon"]

    aq_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    aq_params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pm2_5,pm10,carbon_monoxide,dust",
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "Asia/Bangkok",
    }

    print("fetching air quality for", name)
    aq_response = requests.get(aq_url, params=aq_params)
    aq_data = aq_response.json()

    aq_out_path = "data/raw/" + name + "_air_quality_raw.csv"
    aq_file = open(aq_out_path, "w", newline="")
    aq_writer = csv.writer(aq_file)
    aq_writer.writerow(["time", "pm2_5", "pm10", "carbon_monoxide", "dust"])

    times = aq_data["hourly"]["time"]
    pm2_5_vals = aq_data["hourly"]["pm2_5"]
    pm10_vals = aq_data["hourly"]["pm10"]
    co_vals = aq_data["hourly"]["carbon_monoxide"]
    dust_vals = aq_data["hourly"]["dust"]

    i = 0
    while i < len(times):
        aq_writer.writerow([times[i], pm2_5_vals[i], pm10_vals[i], co_vals[i], dust_vals[i]])
        i = i + 1

    aq_file.close()
    print("saved", aq_out_path, "rows:", len(times))

    weather_url = "https://archive-api.open-meteo.com/v1/archive"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,precipitation,surface_pressure",
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "Asia/Bangkok",
    }

    print("fetching weather for", name)
    weather_response = requests.get(weather_url, params=weather_params)
    weather_data = weather_response.json()

    weather_out_path = "data/raw/" + name + "_weather_raw.csv"
    weather_file = open(weather_out_path, "w", newline="")
    weather_writer = csv.writer(weather_file)
    weather_writer.writerow(["time", "temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "precipitation", "surface_pressure"])

    w_times = weather_data["hourly"]["time"]
    temp_vals = weather_data["hourly"]["temperature_2m"]
    humidity_vals = weather_data["hourly"]["relative_humidity_2m"]
    wind_speed_vals = weather_data["hourly"]["wind_speed_10m"]
    wind_dir_vals = weather_data["hourly"]["wind_direction_10m"]
    precip_vals = weather_data["hourly"]["precipitation"]
    pressure_vals = weather_data["hourly"]["surface_pressure"]

    j = 0
    while j < len(w_times):
        weather_writer.writerow([w_times[j], temp_vals[j], humidity_vals[j], wind_speed_vals[j], wind_dir_vals[j], precip_vals[j], pressure_vals[j]])
        j = j + 1

    weather_file.close()
    print("saved", weather_out_path, "rows:", len(w_times))

print("done")
