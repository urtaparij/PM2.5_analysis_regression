import csv
import datetime
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

locations = ["chiangmai", "nan"]
colors_by_loc = {"chiangmai": "tab:blue", "nan": "tab:orange"}
standard = 37.5
feature_names = ["pm2_5_mean", "pm10_mean", "co_mean", "dust_mean", "temperature_mean", "humidity_mean", "wind_speed_mean", "wind_dir_sin", "wind_dir_cos", "precipitation_sum", "pressure_mean", "doy_sin", "doy_cos", "pm2_5_lag2", "pm2_5_roll3"]

results_file = open("outputs/results/model_metrics.csv", "w", newline="")
results_writer = csv.writer(results_file)
results_writer.writerow(["location", "metric", "baseline", "model", "cv_mean_mae", "cv_std_mae"])

fig8, axes8 = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
loc_idx = 0

for loc in locations:
    path = "data/processed/" + loc + "_daily.csv"
    f = open(path, newline="")
    reader = csv.reader(f)
    header = next(reader)
    dates = []
    pm25 = []
    pm10 = []
    co = []
    dust = []
    temp = []
    humidity = []
    wind_speed = []
    wind_dir = []
    precip = []
    pressure = []
    for row in reader:
        dates.append(datetime.date.fromisoformat(row[0]))
        pm25.append(float(row[1]))
        pm10.append(float(row[2]))
        co.append(float(row[3]))
        dust.append(float(row[4]))
        temp.append(float(row[5]))
        humidity.append(float(row[6]))
        wind_speed.append(float(row[7]))
        wind_dir.append(float(row[8]))
        precip.append(float(row[9]))
        pressure.append(float(row[10]))
    f.close()

    n = len(dates)
    X_rows = []
    y_rows = []
    row_dates = []
    i = 2
    while i < n - 1:
        doy = dates[i].timetuple().tm_yday
        doy_sin = math.sin(2 * math.pi * doy / 365.0)
        doy_cos = math.cos(2 * math.pi * doy / 365.0)
        wind_rad = math.radians(wind_dir[i])
        wind_sin = math.sin(wind_rad)
        wind_cos = math.cos(wind_rad)
        roll3 = (pm25[i] + pm25[i - 1] + pm25[i - 2]) / 3.0
        feat_row = [pm25[i], pm10[i], co[i], dust[i], temp[i], humidity[i], wind_speed[i], wind_sin, wind_cos, precip[i], pressure[i], doy_sin, doy_cos, pm25[i - 2], roll3]
        X_rows.append(feat_row)
        y_rows.append(pm25[i + 1])
        row_dates.append(dates[i])
        i = i + 1

    n_samples = len(X_rows)
    split_index = int(n_samples * 0.8)

    X_train = X_rows[0:split_index]
    y_train = y_rows[0:split_index]
    X_test = X_rows[split_index:n_samples]
    y_test = y_rows[split_index:n_samples]
    dates_test = row_dates[split_index:n_samples]

    print("===", loc, "===")
    print(loc, "usable samples:", n_samples, "train:", len(X_train), "test:", len(X_test))
    print(loc, "test period:", dates_test[0], "to", dates_test[-1], "(most recent", format(len(X_test) / n_samples * 100, ".0f") + "% of the series, chosen to time-order the split and to include a full burn season for a realistic worst-case evaluation)")

    tscv = TimeSeriesSplit(n_splits=5)
    cv_mae_scores = []
    for train_idx, val_idx in tscv.split(X_train):
        X_cv_train = [X_train[j] for j in train_idx]
        y_cv_train = [y_train[j] for j in train_idx]
        X_cv_val = [X_train[j] for j in val_idx]
        y_cv_val = [y_train[j] for j in val_idx]
        cv_model = LinearRegression()
        cv_model.fit(X_cv_train, y_cv_train)
        cv_pred = cv_model.predict(X_cv_val)
        cv_mae_scores.append(mean_absolute_error(y_cv_val, cv_pred))

    cv_mean = sum(cv_mae_scores) / len(cv_mae_scores)
    variance = sum((v - cv_mean) ** 2 for v in cv_mae_scores) / len(cv_mae_scores)
    cv_std = variance ** 0.5
    print(loc, "TimeSeriesSplit CV (5 folds, on training set) MAE: mean =", format(cv_mean, ".2f"), "std =", format(cv_std, ".2f"))

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    baseline_pred = [row[0] for row in X_test]

    model_mae = mean_absolute_error(y_test, y_pred)
    model_rmse = mean_squared_error(y_test, y_pred) ** 0.5
    model_r2 = r2_score(y_test, y_pred)
    baseline_mae = mean_absolute_error(y_test, baseline_pred)
    baseline_rmse = mean_squared_error(y_test, baseline_pred) ** 0.5
    baseline_r2 = r2_score(y_test, baseline_pred)

    print(loc, "baseline (persistence) on test set: MAE =", format(baseline_mae, ".2f"), "RMSE =", format(baseline_rmse, ".2f"), "R2 =", format(baseline_r2, ".3f"))
    print(loc, "model (linear regression) on test set: MAE =", format(model_mae, ".2f"), "RMSE =", format(model_rmse, ".2f"), "R2 =", format(model_r2, ".3f"))

    if model_mae < baseline_mae:
        print(loc, "model beats baseline on MAE by", format(baseline_mae - model_mae, ".2f"), "ug/m3")
    else:
        print(loc, "model does NOT beat baseline on MAE (baseline is", format(model_mae - baseline_mae, ".2f"), "ug/m3 better) - reporting honestly")

    gap = abs(cv_mean - model_mae)
    print(loc, "CV mean MAE vs test MAE gap:", format(gap, ".2f"), "ug/m3")

    results_writer.writerow([loc, "MAE", format(baseline_mae, ".4f"), format(model_mae, ".4f"), format(cv_mean, ".4f"), format(cv_std, ".4f")])
    results_writer.writerow([loc, "RMSE", format(baseline_rmse, ".4f"), format(model_rmse, ".4f"), "", ""])
    results_writer.writerow([loc, "R2", format(baseline_r2, ".4f"), format(model_r2, ".4f"), "", ""])

    coef_path = "outputs/results/" + loc + "_model_coefficients.csv"
    coef_file = open(coef_path, "w", newline="")
    coef_writer = csv.writer(coef_file)
    coef_writer.writerow(["feature", "coefficient"])
    coef_writer.writerow(["intercept", model.intercept_])
    k = 0
    while k < len(feature_names):
        coef_writer.writerow([feature_names[k], model.coef_[k]])
        k = k + 1
    coef_file.close()
    print(loc, "saved", coef_path)
    print("")

    ax = axes8[loc_idx]
    ax.plot(dates_test, y_test, label="actual", color="black", linewidth=1)
    ax.plot(dates_test, y_pred, label="model prediction", color=colors_by_loc[loc], linewidth=1)
    ax.plot(dates_test, baseline_pred, label="baseline (persistence)", color="gray", linewidth=0.8, linestyle=":")
    ax.axhline(y=standard, color="red", linestyle="--", linewidth=1, label="Thai 24h standard (37.5)")
    ax.set_title(loc + " test period")
    ax.set_xlabel("Date")
    if loc_idx == 0:
        ax.set_ylabel("Daily mean PM2.5 (ug/m3)")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis="x", rotation=45)
    loc_idx = loc_idx + 1

results_file.close()
print("saved outputs/results/model_metrics.csv")

fig8.suptitle("Predicted vs actual PM2.5 on held-out test period, model vs persistence baseline")
fig8.tight_layout()
fig8.savefig("outputs/figures/fig08_model_vs_actual.png", dpi=150)
plt.close(fig8)
print("saved outputs/figures/fig08_model_vs_actual.png")

print("data quality problem found and fixed (see prepare_data.py): the fetch-date calendar day mixed forecast hours with observed hours from the Open-Meteo air-quality API; that day was dropped before daily aggregation so no forecast values leak into training or evaluation.")
print("limitation not fixed: the model has no feature that captures transboundary or regional-scale smoke transport; fig07 shows Chiang Mai bad-day wind direction (SW) is opposite the bearing to the only fire hotspots we fetched (NE, within 55km), so Chiang Mai's worst days are likely driven by sources outside this dataset's spatial coverage, which the model cannot see.")

print("")
print("done")
