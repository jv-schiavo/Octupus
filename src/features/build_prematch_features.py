
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "brazil_serie_a_2025.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "features" / "brazil_serie_a_2025_prematch.csv"
)

MIN_HISTORY = 50
SMOOTHING = 5

# 1. Load Silver data
df = pd.read_csv(INPUT_FILE)

required = {
    "date", "home_team", "away_team",
    "home_goals", "away_goals"
}

missing = required - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {missing}")

df["date"] = pd.to_datetime(df["date"])

for column in ["home_goals", "away_goals"]:
    df[column] = pd.to_numeric(df[column], errors="raise")

if df[list(required)].isna().any().any():
    raise ValueError("Missing required match data")

if (df[["home_goals", "away_goals"]] < 0).any().any():
    raise ValueError("Negative goals detected")

df = df.sort_values("date").reset_index(drop=True)


# 2. Smooth averages towards the league baseline
def smoothed_rate(goals, league_average):
    return (
        goals.sum() + SMOOTHING * league_average
    ) / (len(goals) + SMOOTHING)


# 3. Generate features using only earlier matches
features = []

for _, match in df.iterrows():

    history = df[df["date"] < match["date"]]

    # Initial warm-up period
    if len(history) < MIN_HISTORY:
        continue

    league_home_avg = history["home_goals"].mean()
    league_away_avg = history["away_goals"].mean()

    if league_home_avg <= 0 or league_away_avg <= 0:
        raise ValueError("Invalid league scoring baseline")

    home_history = history[
        history["home_team"] == match["home_team"]
    ]

    away_history = history[
        history["away_team"] == match["away_team"]
    ]

    # Home team attack
    home_attack = (
        smoothed_rate(
            home_history["home_goals"],
            league_home_avg
        ) / league_home_avg
    )

    # Away team defence
    away_defence = (
        smoothed_rate(
            away_history["home_goals"],
            league_home_avg
        ) / league_home_avg
    )

    # Away team attack
    away_attack = (
        smoothed_rate(
            away_history["away_goals"],
            league_away_avg
        ) / league_away_avg
    )

    # Home team defence
    home_defence = (
        smoothed_rate(
            home_history["away_goals"],
            league_away_avg
        ) / league_away_avg
    )

    lambda_home = league_home_avg * home_attack * away_defence
    lambda_away = league_away_avg * away_attack * home_defence

    features.append({
        "date": match["date"].date().isoformat(),
        "home_team": match["home_team"],
        "away_team": match["away_team"],
        "historical_matches": len(history),
        "home_attack_strength": round(home_attack, 4),
        "away_defence_weakness": round(away_defence, 4),
        "away_attack_strength": round(away_attack, 4),
        "home_defence_weakness": round(home_defence, 4),
        "lambda_home": round(lambda_home, 4),
        "lambda_away": round(lambda_away, 4),
        "actual_home_goals": match["home_goals"],
        "actual_away_goals": match["away_goals"],
    })


# 4. Save Gold dataset
gold = pd.DataFrame(features)

if gold.empty:
    raise ValueError("Not enough history to generate features")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
gold.to_csv(OUTPUT_FILE, index=False)

print(f"Gold records created: {len(gold)}")
print(f"Saved to: {OUTPUT_FILE}")
print(gold.head().to_string(index=False))
