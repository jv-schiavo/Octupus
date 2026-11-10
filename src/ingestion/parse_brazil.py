from pathlib import Path
from datetime import datetime
import re
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "brazil_serie_a_2025.txt"

OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "brazil_serie_a_2025.csv"

current_matchday = None
current_date = None
weekdays = ("sun", "mon", "tue", "wed", "thu", "fri", "sat")
matches = []

with open(RAW_FILE, "r", encoding="utf-8-sig") as file:
    for index, line in enumerate(file, start=1):
        line = line.strip()

        if "Matchday" in line:
            current_matchday = int(line.split()[-1])
    
        is_date_line = line.lower().startswith(weekdays)
        if is_date_line:
            if len((line.split())) == 3:
                full_date = line + " 2025"
            else:
                full_date = line    
            current_date = datetime.strptime(full_date, "%a %b %d %Y")

        if " v " in line:
            result = re.search(r"\d+-\d+", line)
            if result:
                score = result.group()
                goals = score.split("-")
                home_goals = int(goals[0])
                away_goals = int(goals[-1])

                parts = line.split(" v ")
                away_team = parts[1].split(score)
                away_team = away_team[0].strip()
                home_team = parts[0]

                if ":" in home_team:
                    home_team = home_team.partition(" ")
                    home_team = home_team[-1].strip()
                    
                else:
                    home_team = parts[0].strip()
                

                match = {
                    "matchday": current_matchday,
                    "date": current_date,
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_goals": home_goals,
                    "away_goals": away_goals
                }

                matches.append(match)

# Basic data validation
df = pd.DataFrame(matches)

if len(df) != 380:
    raise ValueError(
        f"Expected 380 matches and 20 teams. Found: {len(df)}")

if df["home_team"].nunique() != 20:
    raise ValueError(
        f"Expected 20 teams. Found: {df['home_team'].nunique()}")

if df.isnull().any().any():
    raise ValueError("Found missing values")

duplicates = df.duplicated(
    subset=["date", "home_team", "away_team"]).sum()

if duplicates > 0:
    raise ValueError(f"Found {duplicates} duplicates fixtures")

df.to_csv(OUTPUT_FILE, index=False)