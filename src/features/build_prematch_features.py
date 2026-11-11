from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEASON = 2026  
MIN_HISTORY = 50
SMOOTHING = 5

OUTPUT_FILE = PROJECT_ROOT / "data" / "features" / "brazil_serie_a_2025_prematch.csv"

df_25 = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "brazil_serie_a_2025.csv")
df_26 = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "brazil_serie_a_2026.csv")

df_25["season"] = 2025
df_26["season"] = 2026

combined = pd.concat([df_25, df_26], ignore_index=True)
combined["date"] = pd.to_datetime(combined["date"])
combined = combined.sort_values("date")



def smoothed_rate(goals, league_average):
    total_goals = goals.sum()
    number_of_matches = len(goals)

    smoothed_avg = (total_goals + SMOOTHING * league_average) / (number_of_matches + SMOOTHING)

    return smoothed_avg

def build_features(df, combined, season):
    features = []
    
    for index, match in df.iterrows():
        prediction_date = match["date"]
        home_team = match["home_team"]
        away_team = match["away_team"]

        historical_matches = combined[combined["date"] < prediction_date]

        if len(historical_matches) < 50:
            continue

        # League Average
        league_home_avg = historical_matches["home_goals"].mean()
        league_away_avg = historical_matches["away_goals"].mean()

        home = historical_matches[historical_matches["home_team"] == home_team]
        away = historical_matches[historical_matches["away_team"] == away_team]

        if season == 2025 and (home.empty or away.empty):
            continue

        # Home
        avg_home_goals = smoothed_rate(home["home_goals"], league_home_avg)
        home_attack_strength = avg_home_goals / league_home_avg
        avg_goals_conceded_home = smoothed_rate(home["away_goals"], league_away_avg)
        home_defensive_weakness = avg_goals_conceded_home / league_away_avg

        # Away
        avg_away_goals = smoothed_rate(away["away_goals"], league_away_avg)
        away_attack_strength = avg_away_goals / league_away_avg
        avg_goals_conceded_away  = smoothed_rate(away["home_goals"], league_home_avg)
        away_defensive_weakness = avg_goals_conceded_away / league_home_avg

        # Lambda Calculation
        lambda_home = league_home_avg * home_attack_strength * away_defensive_weakness
        lambda_away = league_away_avg * away_attack_strength * home_defensive_weakness

        actual_home_goals = match["home_goals"]
        actual_away_goals = match["away_goals"]

        match_features = {
            "date": prediction_date,
            "home_team": home_team,
            "away_team": away_team,
            "lambda_home": lambda_home,
            "lambda_away": lambda_away,
            "actual_home_goals": actual_home_goals,
            "actual_away_goals": actual_away_goals
            }  

        features.append(match_features)
    
    return pd.DataFrame(features)

df = combined[combined["season"] == SEASON].copy()

gold = build_features(df, SEASON)

print(gold.head())

gold.to_csv(OUTPUT_FILE, index=False)

print(f"Gold dataset exported to: {OUTPUT_FILE}")
print(f"Total matches exported: {len(gold)}")

   