
from pathlib import Path
import pandas as pd

from src.model.poisson import predict_match


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEASON = 2026


# LOAD DATA
file_path = PROJECT_ROOT / "data" / "features" / f"brazil_serie_a_{SEASON}_prematch.csv"

df = pd.read_csv(file_path)

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)


# GENERATE PREDICTIONS
def generate_predictions(df):
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

    # Probability Normalisation
    prob_cols = ["home_win_probability", "draw_probability", "away_win_probability"]

    results["probability_sum"] = results[prob_cols].sum(axis=1)

    results["home_win_probability"] = results["home_win_probability"] / results["probability_sum"]
    results["away_win_probability"] = results["away_win_probability"] / results["probability_sum"]
    results["draw_probability"] = results["draw_probability"] / results["probability_sum"]

    return results


# HISTORICAL BASELINE
def calculate_baseline(results, silver):
    results = results.copy()

    for index, match in results.iterrows():
        prediction_date = match["date"]

        baseline_history = silver[silver["date"] < prediction_date]

        total_matches = len(baseline_history)

        if total_matches == 0:
            raise ValueError(f"No historical data before {prediction_date}")

        home_wins = (baseline_history["home_goals"] > baseline_history["away_goals"]).sum()
        draws = (baseline_history["home_goals"] == baseline_history["away_goals"]).sum()
        away_wins = (baseline_history["home_goals"] < baseline_history["away_goals"]).sum()

        baseline_home_win = home_wins / total_matches
        baseline_draw = draws / total_matches
        baseline_away_win = away_wins / total_matches

        results.loc[index, "baseline_home_win_probability"] = baseline_home_win
        results.loc[index, "baseline_draw_probability"] = baseline_draw
        results.loc[index, "baseline_away_win_probability"] = baseline_away_win

    return results


# BRIER SCORES
def calculate_brier_scores(results):
    results = results.copy()

    results["brier_score"] = (
        (results["home_win_probability"] - results["actual_home_win"]) ** 2 +
        (results["draw_probability"] - results["actual_draw"]) ** 2 +
        (results["away_win_probability"] - results["actual_away_win"]) ** 2
    )

    results["baseline_brier_score"] = (
        (results["baseline_home_win_probability"] - results["actual_home_win"]) ** 2 +
        (results["baseline_draw_probability"] - results["actual_draw"]) ** 2 +
        (results["baseline_away_win_probability"] - results["actual_away_win"]) ** 2
    )

    results["brier_gap"] = (
        results["baseline_brier_score"] - results["brier_score"]
    )

    average_brier_score = results["brier_score"].mean()
    average_baseline_brier_score = results["baseline_brier_score"].mean()

    print(f"Poisson Brier Score: {average_brier_score:.4f}")
    print(f"Baseline Brier Score: {average_baseline_brier_score:.4f}")

    return results


# MONTHLY ANALYSIS
def monthly_analysis(results):
    results = results.copy()

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

    return monthly_performance


# MAIN
def main():
    silver_25 = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "brazil_serie_a_2025.csv")
    silver_26 = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "brazil_serie_a_2026.csv")

    silver = pd.concat([silver_25, silver_26], ignore_index=True)
    silver["date"] = pd.to_datetime(silver["date"])
    silver = silver.sort_values("date").reset_index(drop=True)

    results = generate_predictions(df)
    results = calculate_baseline(results, silver)
    results = calculate_brier_scores(results)

    monthly_performance = monthly_analysis(results)

    print(monthly_performance)


if __name__ == "__main__":
    main()
