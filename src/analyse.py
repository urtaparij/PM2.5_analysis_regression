import csv
import datetime
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import math

locations = ["chiangmai", "nan"]
standard = 37.5
colors_by_loc = {"chiangmai": "tab:blue", "nan": "tab:orange"}
colors_by_year = {2023: "tab:blue", 2024: "tab:orange", 2025: "tab:green", 2026: "tab:red"}
station_coords = {"chiangmai": (18.7883, 98.9853), "nan": (18.7756, 100.7730)}
octant_names = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

data = {}
for loc in locations:
    path = "data/processed/" + loc + "_daily.csv"
    f = open(path, newline="")
    reader = csv.reader(f)
    header = next(reader)
    dates = []
    pm25 = []
    pm10 = []
    temp = []
    humidity = []
    wind_speed = []
    wind_dir = []
    precip = []
    pressure = []
    for row in reader:
        d = datetime.date.fromisoformat(row[0])
        dates.append(d)
        pm25.append(float(row[1]))
        pm10.append(float(row[2]))
        temp.append(float(row[5]))
        humidity.append(float(row[6]))
        wind_speed.append(float(row[7]))
        wind_dir.append(float(row[8]))
        precip.append(float(row[9]))
        pressure.append(float(row[10]))
    f.close()
    data[loc] = {"date": dates, "pm25": pm25, "pm10": pm10, "temp": temp, "humidity": humidity, "wind_speed": wind_speed, "wind_dir": wind_dir, "precip": precip, "pressure": pressure}
    print(loc, "loaded rows:", len(dates), "range:", dates[0], "to", dates[-1])

print("")
print("=== Figure 1: monthly PM2.5 climatology by year ===")

monthly = {}
for loc in locations:
    monthly[loc] = {}
    i = 0
    while i < len(data[loc]["date"]):
        d = data[loc]["date"][i]
        y = d.year
        m = d.month
        if y not in monthly[loc]:
            monthly[loc][y] = {}
            mm = 1
            while mm <= 12:
                monthly[loc][y][mm] = []
                mm = mm + 1
        monthly[loc][y][m].append(data[loc]["pm25"][i])
        i = i + 1

fig1, axes1 = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
loc_idx = 0
while loc_idx < len(locations):
    loc = locations[loc_idx]
    ax = axes1[loc_idx]
    years_sorted = sorted(monthly[loc].keys())
    yi = 0
    while yi < len(years_sorted):
        y = years_sorted[yi]
        months_x = []
        means_y = []
        m = 1
        while m <= 12:
            vals = monthly[loc][y][m]
            if len(vals) > 0:
                months_x.append(m)
                means_y.append(sum(vals) / len(vals))
            m = m + 1
        color = colors_by_year.get(y, "gray")
        ax.plot(months_x, means_y, marker="o", label=str(y), color=color)
        yi = yi + 1
    ax.axhline(y=standard, color="black", linestyle="--", linewidth=1, label="Thai 24h standard (37.5)")
    ax.set_title(loc)
    ax.set_xlabel("Month")
    ax.set_xticks(list(range(1, 13)))
    if loc_idx == 0:
        ax.set_ylabel("Mean daily PM2.5 (ug/m3)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    loc_idx = loc_idx + 1

fig1.suptitle("Monthly PM2.5 climatology by year, Chiang Mai vs Nan")
fig1.tight_layout()
fig1.savefig("outputs/figures/fig01_seasonal_pattern.png", dpi=150)
plt.close(fig1)
print("saved outputs/figures/fig01_seasonal_pattern.png")

print("")
print("=== Figure 2: exceedance days per year ===")

annual_counts = {}
annual_totals = {}
for loc in locations:
    annual_counts[loc] = {}
    annual_totals[loc] = {}
    i = 0
    while i < len(data[loc]["date"]):
        y = data[loc]["date"][i].year
        if y not in annual_counts[loc]:
            annual_counts[loc][y] = 0
            annual_totals[loc][y] = 0
        annual_totals[loc][y] = annual_totals[loc][y] + 1
        if data[loc]["pm25"][i] > standard:
            annual_counts[loc][y] = annual_counts[loc][y] + 1
        i = i + 1

years_all = []
for loc in locations:
    for y in annual_counts[loc].keys():
        if y not in years_all:
            years_all.append(y)
years_all = sorted(years_all)

results_file = open("outputs/results/annual_exceedance.csv", "w", newline="")
results_writer = csv.writer(results_file)
results_writer.writerow(["location", "year", "days_over_standard", "days_in_year", "note"])
for loc in locations:
    for y in years_all:
        count = annual_counts[loc].get(y, 0)
        total = annual_totals[loc].get(y, 0)
        note = ""
        if total < 360:
            note = "partial year"
        results_writer.writerow([loc, y, count, total, note])
        print(loc, y, "days over 37.5:", count, "out of", total, note)
results_file.close()
print("saved outputs/results/annual_exceedance.csv")

fig2, ax2 = plt.subplots(figsize=(9, 5))
bar_width = 0.35
x_positions = list(range(len(years_all)))
loc_idx = 0
while loc_idx < len(locations):
    loc = locations[loc_idx]
    heights = []
    yi = 0
    while yi < len(years_all):
        heights.append(annual_counts[loc].get(years_all[yi], 0))
        yi = yi + 1
    offsets = []
    xi = 0
    while xi < len(x_positions):
        offsets.append(x_positions[xi] + loc_idx * bar_width)
        xi = xi + 1
    ax2.bar(offsets, heights, width=bar_width, label=loc, color=colors_by_loc[loc])
    loc_idx = loc_idx + 1

xtick_labels = []
yi = 0
while yi < len(years_all):
    label = str(years_all[yi])
    if annual_totals["chiangmai"].get(years_all[yi], 0) < 360:
        label = label + "*"
    xtick_labels.append(label)
    yi = yi + 1

xtick_positions = []
xi = 0
while xi < len(x_positions):
    xtick_positions.append(x_positions[xi] + bar_width / 2)
    xi = xi + 1

ax2.set_xticks(xtick_positions)
ax2.set_xticklabels(xtick_labels)
ax2.set_xlabel("Year (* = partial year, data through fetch date)")
ax2.set_ylabel("Days with daily mean PM2.5 > 37.5 ug/m3")
ax2.set_title("Days exceeding the Thai 24h PM2.5 standard per year")
ax2.legend()
ax2.grid(True, alpha=0.3, axis="y")
fig2.tight_layout()
fig2.savefig("outputs/figures/fig02_annual_exceedance.png", dpi=150)
plt.close(fig2)
print("saved outputs/figures/fig02_annual_exceedance.png")

print("")
print("=== Figure 3: location comparison (C4 evidence) ===")

nan_by_date = {}
i = 0
while i < len(data["nan"]["date"]):
    nan_by_date[data["nan"]["date"][i]] = data["nan"]["pm25"][i]
    i = i + 1

cm_vals = []
nan_vals = []
i = 0
while i < len(data["chiangmai"]["date"]):
    d = data["chiangmai"]["date"][i]
    if d in nan_by_date:
        cm_vals.append(data["chiangmai"]["pm25"][i])
        nan_vals.append(nan_by_date[d])
    i = i + 1

n_matched = len(cm_vals)
mean_cm = sum(cm_vals) / n_matched
mean_nan = sum(nan_vals) / n_matched
mean_diff = mean_cm - mean_nan

cov_sum = 0.0
var_cm_sum = 0.0
var_nan_sum = 0.0
i = 0
while i < n_matched:
    dx = cm_vals[i] - mean_cm
    dy = nan_vals[i] - mean_nan
    cov_sum = cov_sum + dx * dy
    var_cm_sum = var_cm_sum + dx * dx
    var_nan_sum = var_nan_sum + dy * dy
    i = i + 1
correlation = cov_sum / ((var_cm_sum ** 0.5) * (var_nan_sum ** 0.5))

days_differ_5 = 0
i = 0
while i < n_matched:
    if abs(cm_vals[i] - nan_vals[i]) > 5:
        days_differ_5 = days_differ_5 + 1
    i = i + 1
pct_differ_5 = days_differ_5 / n_matched * 100

print("matched days:", n_matched)
print("mean chiangmai:", mean_cm, "mean nan:", mean_nan, "mean difference:", mean_diff)
print("correlation (chiangmai vs nan):", correlation)
print("days differing by more than 5 ug/m3:", days_differ_5, "(" + format(pct_differ_5, ".1f") + "%)")

comp_file = open("outputs/results/location_comparison_stats.csv", "w", newline="")
comp_writer = csv.writer(comp_file)
comp_writer.writerow(["metric", "value"])
comp_writer.writerow(["matched_days", n_matched])
comp_writer.writerow(["mean_pm25_chiangmai", mean_cm])
comp_writer.writerow(["mean_pm25_nan", mean_nan])
comp_writer.writerow(["mean_difference_chiangmai_minus_nan", mean_diff])
comp_writer.writerow(["pearson_correlation", correlation])
comp_writer.writerow(["pct_days_differing_more_than_5ugm3", pct_differ_5])
comp_file.close()
print("saved outputs/results/location_comparison_stats.csv")

fig3, ax3 = plt.subplots(figsize=(6, 6))
ax3.scatter(cm_vals, nan_vals, s=8, alpha=0.35, color="tab:purple")
max_val = max(max(cm_vals), max(nan_vals))
ax3.plot([0, max_val], [0, max_val], color="black", linestyle="--", linewidth=1, label="y = x")
ax3.set_xlabel("Chiang Mai daily mean PM2.5 (ug/m3)")
ax3.set_ylabel("Nan daily mean PM2.5 (ug/m3)")
ax3.set_title("Chiang Mai vs Nan, same-day PM2.5 (n=" + str(n_matched) + ")")
text_str = "r = " + format(correlation, ".3f") + "\nmean diff = " + format(mean_diff, ".1f") + " ug/m3\n" + format(pct_differ_5, ".0f") + "% of days differ by >5 ug/m3"
ax3.text(0.05, 0.95, text_str, transform=ax3.transAxes, fontsize=9, verticalalignment="top")
ax3.legend(loc="lower right")
ax3.grid(True, alpha=0.3)
fig3.tight_layout()
fig3.savefig("outputs/figures/fig03_location_comparison.png", dpi=150)
plt.close(fig3)
print("saved outputs/figures/fig03_location_comparison.png")

print("")
print("=== Figure 4: weather on bad days vs good days ===")

fig4, axes4 = plt.subplots(1, 2, figsize=(11, 5))
loc_idx = 0
bar_width = 0.35
metric_names = ["wind_speed", "humidity"]
metric_labels = ["Mean wind speed (m/s)", "Mean relative humidity (%)"]
mi = 0
while mi < len(metric_names):
    metric = metric_names[mi]
    ax = axes4[mi]
    good_means = []
    bad_means = []
    loc_idx = 0
    while loc_idx < len(locations):
        loc = locations[loc_idx]
        good_vals = []
        bad_vals = []
        i = 0
        while i < len(data[loc]["pm25"]):
            if data[loc]["pm25"][i] > standard:
                bad_vals.append(data[loc][metric][i])
            else:
                good_vals.append(data[loc][metric][i])
            i = i + 1
        good_means.append(statistics.mean(good_vals))
        bad_means.append(statistics.mean(bad_vals))
        loc_idx = loc_idx + 1
    x_positions = list(range(len(locations)))
    offsets_good = []
    offsets_bad = []
    xi = 0
    while xi < len(x_positions):
        offsets_good.append(x_positions[xi] - bar_width / 2)
        offsets_bad.append(x_positions[xi] + bar_width / 2)
        xi = xi + 1
    ax.bar(offsets_good, good_means, width=bar_width, label="good day (<=37.5)", color="tab:green")
    ax.bar(offsets_bad, bad_means, width=bar_width, label="bad day (>37.5)", color="tab:red")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(locations)
    ax.set_ylabel(metric_labels[mi])
    ax.set_title(metric_labels[mi])
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")
    mi = mi + 1

fig4.suptitle("Weather conditions on good vs bad PM2.5 days")
fig4.tight_layout()
fig4.savefig("outputs/figures/fig04_weather_vs_bad_days.png", dpi=150)
plt.close(fig4)
print("saved outputs/figures/fig04_weather_vs_bad_days.png")

print("")
print("=== Figure 5: day-of-week pattern ===")

weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
fig5, ax5 = plt.subplots(figsize=(8, 5))
loc_idx = 0
while loc_idx < len(locations):
    loc = locations[loc_idx]
    weekday_vals = {}
    wd = 0
    while wd < 7:
        weekday_vals[wd] = []
        wd = wd + 1
    i = 0
    while i < len(data[loc]["date"]):
        wd = data[loc]["date"][i].weekday()
        weekday_vals[wd].append(data[loc]["pm25"][i])
        i = i + 1
    means_by_wd = []
    wd = 0
    while wd < 7:
        means_by_wd.append(sum(weekday_vals[wd]) / len(weekday_vals[wd]))
        wd = wd + 1
    ax5.plot(list(range(7)), means_by_wd, marker="o", label=loc, color=colors_by_loc[loc])
    loc_idx = loc_idx + 1

ax5.set_xticks(list(range(7)))
ax5.set_xticklabels(weekday_names)
ax5.set_xlabel("Day of week")
ax5.set_ylabel("Mean daily PM2.5 (ug/m3)")
ax5.set_title("Weekly pattern in PM2.5")
ax5.legend()
ax5.grid(True, alpha=0.3)
fig5.tight_layout()
fig5.savefig("outputs/figures/fig05_weekly_pattern.png", dpi=150)
plt.close(fig5)
print("saved outputs/figures/fig05_weekly_pattern.png")

print("")
print("=== Figure 6: NASA FIRMS fire hotspots near each location (Part D support) ===")

firms_years = [2023, 2024, 2025, 2026]
firms_counts = {}
firms_frp = {}
for loc in locations:
    path = "data/raw/firms_" + loc + "_raw.csv"
    f = open(path, newline="")
    reader = csv.reader(f)
    header = next(reader)
    date_col = header.index("acq_date")
    frp_col = header.index("frp")
    year_counts = {}
    year_frp = {}
    yy = 0
    while yy < len(firms_years):
        year_counts[firms_years[yy]] = 0
        year_frp[firms_years[yy]] = 0.0
        yy = yy + 1
    for row in reader:
        y = int(row[date_col][0:4])
        if y in year_counts:
            year_counts[y] = year_counts[y] + 1
            year_frp[y] = year_frp[y] + float(row[frp_col])
    f.close()
    firms_counts[loc] = year_counts
    firms_frp[loc] = year_frp
    total_loc = sum(year_counts.values())
    print(loc, "total hotspots (Feb-Apr, 2023-2026, within 0.5 deg box):", total_loc)

firms_file = open("outputs/results/firms_summary.csv", "w", newline="")
firms_writer = csv.writer(firms_file)
firms_writer.writerow(["location", "year", "hotspot_count", "total_frp_mw"])
for loc in locations:
    for y in firms_years:
        firms_writer.writerow([loc, y, firms_counts[loc][y], firms_frp[loc][y]])
firms_file.close()
print("saved outputs/results/firms_summary.csv")

fig6, ax6 = plt.subplots(figsize=(9, 5))
bar_width = 0.35
x_positions = list(range(len(firms_years)))
loc_idx = 0
while loc_idx < len(locations):
    loc = locations[loc_idx]
    heights = []
    yi = 0
    while yi < len(firms_years):
        heights.append(firms_counts[loc][firms_years[yi]])
        yi = yi + 1
    offsets = []
    xi = 0
    while xi < len(x_positions):
        offsets.append(x_positions[xi] + loc_idx * bar_width)
        xi = xi + 1
    ax6.bar(offsets, heights, width=bar_width, label=loc, color=colors_by_loc[loc])
    loc_idx = loc_idx + 1

xtick_positions = []
xi = 0
while xi < len(x_positions):
    xtick_positions.append(x_positions[xi] + bar_width / 2)
    xi = xi + 1
ax6.set_xticks(xtick_positions)
ax6.set_xticklabels([str(y) for y in firms_years])
ax6.set_xlabel("Year (burn season, Feb 1 - Apr 30)")
ax6.set_ylabel("VIIRS fire hotspot detections within 0.5 deg (~55 km) of station")
ax6.set_title("NASA FIRMS fire hotspot counts near Chiang Mai vs Nan, burn season")
ax6.legend()
ax6.grid(True, alpha=0.3, axis="y")
fig6.tight_layout()
fig6.savefig("outputs/figures/fig06_fire_hotspots.png", dpi=150)
plt.close(fig6)
print("saved outputs/figures/fig06_fire_hotspots.png")

print("")
print("=== Figure 7: wind direction on bad days vs bearing to fire hotspots ===")

wind_file = open("outputs/results/wind_source_analysis.csv", "w", newline="")
wind_writer = csv.writer(wind_file)
wind_writer.writerow(["location", "metric", "value_deg", "octant"])

fig7, axes7 = plt.subplots(1, 2, figsize=(12, 6), subplot_kw={"projection": "polar"})
loc_idx = 0
while loc_idx < len(locations):
    loc = locations[loc_idx]
    ax = axes7[loc_idx]

    octant_sums = []
    octant_counts = []
    k = 0
    while k < 8:
        octant_sums.append(0.0)
        octant_counts.append(0)
        k = k + 1

    bad_sin = 0.0
    bad_cos = 0.0
    bad_n = 0
    i = 0
    while i < len(data[loc]["date"]):
        wd = data[loc]["wind_dir"][i]
        rad = math.radians(wd)
        octant_index = round(wd / 45.0) % 8
        octant_sums[octant_index] = octant_sums[octant_index] + data[loc]["pm25"][i]
        octant_counts[octant_index] = octant_counts[octant_index] + 1
        if data[loc]["pm25"][i] > standard:
            bad_sin = bad_sin + math.sin(rad)
            bad_cos = bad_cos + math.cos(rad)
            bad_n = bad_n + 1
        i = i + 1

    octant_means = []
    k = 0
    while k < 8:
        if octant_counts[k] > 0:
            octant_means.append(octant_sums[k] / octant_counts[k])
        else:
            octant_means.append(0.0)
        k = k + 1

    bad_wind_bearing = (math.degrees(math.atan2(bad_sin, bad_cos)) + 360) % 360

    lat1 = math.radians(station_coords[loc][0])
    lon1 = math.radians(station_coords[loc][1])
    firms_path = "data/raw/firms_" + loc + "_raw.csv"
    ff = open(firms_path, newline="")
    freader = csv.reader(ff)
    fheader = next(freader)
    lat_col = fheader.index("latitude")
    lon_col = fheader.index("longitude")
    hs_sin = 0.0
    hs_cos = 0.0
    hs_n = 0
    for row in freader:
        lat2 = math.radians(float(row[lat_col]))
        lon2 = math.radians(float(row[lon_col]))
        dlon = lon2 - lon1
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        bearing = math.degrees(math.atan2(x, y))
        brad = math.radians(bearing)
        hs_sin = hs_sin + math.sin(brad)
        hs_cos = hs_cos + math.cos(brad)
        hs_n = hs_n + 1
    ff.close()
    hotspot_bearing = (math.degrees(math.atan2(hs_sin, hs_cos)) + 360) % 360

    bad_octant = octant_names[round(bad_wind_bearing / 45.0) % 8]
    hotspot_octant = octant_names[round(hotspot_bearing / 45.0) % 8]

    print(loc, "mean wind FROM direction on bad days:", format(bad_wind_bearing, ".0f"), "deg (" + bad_octant + ")", "n=" + str(bad_n))
    print(loc, "mean bearing TO fire hotspots from station:", format(hotspot_bearing, ".0f"), "deg (" + hotspot_octant + ")", "n=" + str(hs_n))

    wind_writer.writerow([loc, "mean_wind_from_bearing_on_bad_days", format(bad_wind_bearing, ".1f"), bad_octant])
    wind_writer.writerow([loc, "mean_bearing_to_firms_hotspots", format(hotspot_bearing, ".1f"), hotspot_octant])

    angles = []
    k = 0
    while k < 8:
        angles.append(math.radians(k * 45))
        k = k + 1
    angles_closed = angles + [angles[0]]
    values_closed = octant_means + [octant_means[0]]
    ax.plot(angles_closed, values_closed, marker="o", color=colors_by_loc[loc])
    ax.fill(angles_closed, values_closed, alpha=0.15, color=colors_by_loc[loc])
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_xticks(angles)
    ax.set_xticklabels(octant_names)
    ax.set_title(loc + "\nmean PM2.5 by wind FROM direction")
    ax.axvline(x=math.radians(hotspot_bearing), color="red", linestyle="--", linewidth=1.5, label="bearing to FIRMS hotspots")
    ax.legend(loc="upper right", fontsize=7, bbox_to_anchor=(1.3, 1.1))

    loc_idx = loc_idx + 1

wind_file.close()
fig7.suptitle("Wind direction vs PM2.5, with bearing to fire hotspot cluster overlaid")
fig7.tight_layout()
fig7.savefig("outputs/figures/fig07_wind_direction_source.png", dpi=150)
plt.close(fig7)
print("saved outputs/figures/fig07_wind_direction_source.png")
print("saved outputs/results/wind_source_analysis.csv")

print("")
print("done")
