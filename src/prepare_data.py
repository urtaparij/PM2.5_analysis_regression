import csv
import datetime

locations = ["chiangmai", "nan"]
col_names = ["time", "pm2_5", "pm10", "carbon_monoxide", "dust", "temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "precipitation", "surface_pressure"]
today_str = datetime.date.today().isoformat()

for loc in locations:
    aq_path = "data/raw/" + loc + "_air_quality_raw.csv"
    weather_path = "data/raw/" + loc + "_weather_raw.csv"

    aq_file = open(aq_path, newline="")
    aq_reader = csv.reader(aq_file)
    aq_header = next(aq_reader)
    aq_rows = []
    for row in aq_reader:
        aq_rows.append(row)
    aq_file.close()

    weather_file = open(weather_path, newline="")
    weather_reader = csv.reader(weather_file)
    weather_header = next(weather_reader)
    weather_rows = []
    for row in weather_reader:
        weather_rows.append(row)
    weather_file.close()

    print("===", loc, "===")
    print(loc, "air_quality rows before join:", len(aq_rows))
    print(loc, "weather rows before join:", len(weather_rows))

    weather_dict = {}
    for row in weather_rows:
        weather_dict[row[0]] = row

    joined_rows = []
    for row in aq_rows:
        t = row[0]
        if t in weather_dict:
            w = weather_dict[t]
            combined = [t, row[1], row[2], row[3], row[4], w[1], w[2], w[3], w[4], w[5], w[6]]
            joined_rows.append(combined)

    print(loc, "rows after join:", len(joined_rows))
    print(loc, "rows dropped in join (time mismatch between the two endpoints):", len(aq_rows) - len(joined_rows))
    print(loc, "first joined timestamp:", joined_rows[0][0], "last joined timestamp:", joined_rows[-1][0])

    missing_counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for row in joined_rows:
        i = 0
        while i < len(row):
            if row[i] == "" or row[i] is None:
                missing_counts[i] = missing_counts[i] + 1
            i = i + 1

    total_joined = len(joined_rows)
    i = 0
    while i < len(col_names):
        pct = 0.0
        if total_joined > 0:
            pct = missing_counts[i] / total_joined * 100
        print(loc, col_names[i], "missing:", missing_counts[i], "(" + format(pct, ".4f") + "%)")
        i = i + 1

    daily_dict = {}
    for row in joined_rows:
        date_str = row[0][0:10]
        has_missing = False
        i = 1
        while i < len(row):
            if row[i] == "":
                has_missing = True
            i = i + 1
        if date_str not in daily_dict:
            daily_dict[date_str] = {"pm2_5": [], "pm10": [], "co": [], "dust": [], "temp": [], "humidity": [], "wind_speed": [], "wind_dir": [], "precip": [], "pressure": []}
        if has_missing == False:
            entry = daily_dict[date_str]
            entry["pm2_5"].append(float(row[1]))
            entry["pm10"].append(float(row[2]))
            entry["co"].append(float(row[3]))
            entry["dust"].append(float(row[4]))
            entry["temp"].append(float(row[5]))
            entry["humidity"].append(float(row[6]))
            entry["wind_speed"].append(float(row[7]))
            entry["wind_dir"].append(float(row[8]))
            entry["precip"].append(float(row[9]))
            entry["pressure"].append(float(row[10]))

    dates_sorted = sorted(daily_dict.keys())

    complete_dates = []
    for d in dates_sorted:
        entry = daily_dict[d]
        n = len(entry["pm2_5"])
        if n == 24 and d != today_str:
            complete_dates.append(d)

    print(loc, "calendar days seen:", len(dates_sorted))
    print(loc, "calendar days kept (24 valid hours, excludes fetch date " + today_str + " which mixes forecast hours):", len(complete_dates))
    print(loc, "calendar days dropped (incomplete or fetch-date forecast contamination):", len(dates_sorted) - len(complete_dates))

    out_path = "data/processed/" + loc + "_daily.csv"
    out_file = open(out_path, "w", newline="")
    writer = csv.writer(out_file)
    writer.writerow(["date", "pm2_5_mean", "pm10_mean", "co_mean", "dust_mean", "temperature_mean", "humidity_mean", "wind_speed_mean", "wind_direction_mean", "precipitation_sum", "pressure_mean", "hours_count"])

    for d in complete_dates:
        entry = daily_dict[d]
        n = len(entry["pm2_5"])
        pm2_5_mean = sum(entry["pm2_5"]) / n
        pm10_mean = sum(entry["pm10"]) / n
        co_mean = sum(entry["co"]) / n
        dust_mean = sum(entry["dust"]) / n
        temp_mean = sum(entry["temp"]) / n
        humidity_mean = sum(entry["humidity"]) / n
        wind_speed_mean = sum(entry["wind_speed"]) / n
        wind_dir_mean = sum(entry["wind_dir"]) / n
        precip_sum = sum(entry["precip"])
        pressure_mean = sum(entry["pressure"]) / n
        writer.writerow([d, pm2_5_mean, pm10_mean, co_mean, dust_mean, temp_mean, humidity_mean, wind_speed_mean, wind_dir_mean, precip_sum, pressure_mean, n])

    out_file.close()
    print(loc, "saved", out_path, "rows:", len(complete_dates))
    print("")

print("done")
