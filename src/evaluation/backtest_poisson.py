from pathlib import Path
import pandas as pd

from src.model.poisson import predict_match 

PROJECT_ROOT = Path(__file__).resolve().parents[2]

file_path = (PROJECT_ROOT / "data" / "features" / "brazil_serie_a_2025_prematch.csv")

df = pd.read_csv(file_path)

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")

predictions = []

for index, match in df.iterrows():
    lambda_home = match["lambda_home"]
    lambda_away = match["lambda_away"]

    prediction = predict_match(lambda_home, lambda_away)

    if match["actual_home_goals"] > match["actual_away_goals"]:
        actual_outcome = "H"
    elif match["actual_away_goals"] > match["actual_home_goals"]:
        actual_outcome = "A"
    else:
        actual_outcome = "D"

    match_prediction = {
        "date": match["date"],
        "home_team": match["home_team"],
        "away_team": match["away_team"],
        "home_win_probability": prediction["home_win"],
        "draw_probability": prediction["draw"],
        "away_win_probability": prediction["away_win"],
        "actual_home_goals": match["actual_home_goals"],
        "actual_away_goals": match["actual_away_goals"],
        "actual_outcome": actual_outcome
    }

    predictions.append(match_prediction)

results = pd.DataFrame(predictions)

results["actual_home_win"] = (results["actual_outcome"] == "H").astype(int)
results["actual_away_win"] = (results["actual_outcome"] == "A").astype(int)
results["actual_draw"] = (results["actual_outcome"] == "D").astype(int)

prob_cols = ["home_win_probability", "draw_probability", "away_win_probability"]
results["probability_sum"] = results[prob_cols].sum(axis=1)
results["home_win_probability"] = (results["home_win_probability"] / results["probability_sum"])
results["away_win_probability"] = (results["away_win_probability"] / results["probability_sum"])
results["draw_probability"] = (results["draw_probability"] / results["probability_sum"])


results["brier_score"] = (
        (results["home_win_probability"] - results["actual_home_win"]) ** 2 +
        (results["draw_probability"] - results["actual_draw"]) ** 2 +
        (results["away_win_probability"] - results["actual_away_win"]) ** 2
)

average_brier_score = results["brier_score"].mean()

# BASELINE 

SILVER_FILE = PROJECT_ROOT / "data" / "processed" / "brazil_serie_a_2025.csv"

silver = pd.read_csv(SILVER_FILE)
silver["date"] = pd.to_datetime(silver["date"])

for index, match in results.iterrows():
    prediction_date = match["date"]

    baseline_history = silver[silver["date"] < prediction_date]

    total_matches = len(baseline_history)

    home_wins = (baseline_history["home_goals"] > baseline_history["away_goals"]).sum()
    draws = (baseline_history["home_goals"] == baseline_history["away_goals"]).sum()
    away_wins = (baseline_history["home_goals"] < baseline_history["away_goals"]).sum()

    baseline_home_win = home_wins / total_matches
    baseline_draw = draws / total_matches
    baseline_away_win = away_wins / total_matches

    results.loc[index, "baseline_home_win_probability"] = baseline_home_win
    results.loc[index, "baseline_draw_probability"] = baseline_draw
    results.loc[index, "baseline_away_win_probability"] = baseline_away_win


results["baseline_brier_score"] = (
        (results["baseline_home_win_probability"] - results["actual_home_win"]) ** 2 +
        (results["baseline_draw_probability"] - results["actual_draw"]) ** 2 +
        (results["baseline_away_win_probability"] - results["actual_away_win"]) ** 2
    )

average_baseline_brier_score = results["baseline_brier_score"].mean()

print(f"Poisson Brier Score: {average_brier_score:.4f}")
print(f"Baseline Brier Score: {average_baseline_brier_score:.4f}")

# BY MONTH

results["month"] = results["date"].dt.to_period("M")

monthly_performance = results.groupby("month").agg(
    matches=("brier_score", "size"),
    poisson_brier=("brier_score", "mean"),
    baseline_brier=("baseline_brier_score", "mean")
)

monthly_performance["improvement"] = (
    monthly_performance["baseline_brier"]
    - monthly_performance["poisson_brier"]
)

# Difference between baseline and Poisson Brier scores
results["brier_gap"] = (
    results["baseline_brier_score"] - results["brier_score"]
)

# Filter September 2025
september = results[
    results["date"].dt.to_period("M") == "2025-09"
]

worst_matches = september.sort_values(
    "brier_gap", ascending=True
).head(5)

# Display relevant columns
print(worst_matches[[
    "date",
    "home_team",
    "away_team",
    "actual_outcome",
    "home_win_probability",
    "draw_probability",
    "away_win_probability",
    "brier_score",
    "baseline_brier_score",
    "brier_gap"
]].to_string(index=False))

remaining_september = september.drop(worst_matches.index)

# 1. Create probability ranges
results["home_prob_bin"] = pd.cut(
    results["home_win_probability"],
    bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
    include_lowest=True
)

print(results["home_prob_bin"].value_counts().sort_index())

home_calibration = results.groupby(
    "home_prob_bin",
    observed=True
).agg(
    matches=("actual_home_win", "size"),
    avg_predicted_probability=("home_win_probability", "mean"),
    actual_win_rate=("actual_home_win", "mean")
)

home_calibration["calibration_gap"] = (
    home_calibration["actual_win_rate"]
    - home_calibration["avg_predicted_probability"]
)

# 5. Display the results as percentages
home_calibration[
    [
        "avg_predicted_probability",
        "actual_win_rate",
        "calibration_gap"
    ]
] *= 100
