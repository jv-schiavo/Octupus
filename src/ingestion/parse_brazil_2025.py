
import csv
import re
from pathlib import Path
from datetime import datetime

# File paths
RAW_FILE = Path("data/raw/brazil_serie_a_2025.txt")
OUTPUT_FILE = Path("data/processed/brazil_serie_a_2025.csv")

# Match date, e.g. Sat Mar 29 2025 or Sun Mar 30
date_pattern = re.compile(
    r"^(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun) "
    r"(?P<month>[A-Z][a-z]{2}) "
    r"(?P<day>\d{1,2})(?: (?P<year>\d{4}))?$"
)

# Match result, with optional time and half-time score
match_pattern = re.compile(
    r"^(?:(?P<time>\d{1,2}:\d{2})\s+)?"
    r"(?P<home>.+?)\s+v\s+"
    r"(?P<away>.+?)\s{2,}"
    r"(?P<hg>\d+)-(?P<ag>\d+)"
    r"(?:\s+\(\d+-\d+\))?$"
)

matches = []
current_date = None
matchday = None

with RAW_FILE.open(encoding="utf-8-sig") as file:
    for line_number, line in enumerate(file, start=1):
        line = line.strip()

        if line.startswith("▪ Matchday"):
            matchday = int(line.split()[-1])
            continue

        date_match = date_pattern.match(line)
        if date_match:
            month = date_match.group("month")
            day = date_match.group("day")
            year = date_match.group("year") or "2025"

            current_date = datetime.strptime(
                f"{month} {day} {year}", "%b %d %Y"
            ).date()
            continue

        match = match_pattern.match(line)
        if match:
            if current_date is None or matchday is None:
                raise ValueError(
                    f"Missing date or matchday at line {line_number}"
                )

            matches.append({
                "date": current_date.isoformat(),
                "matchday": matchday,
                "home_team": match.group("home").strip(),
                "away_team": match.group("away").strip(),
                "home_goals": int(match.group("hg")),
                "away_goals": int(match.group("ag")),
                "kickoff_time": match.group("time") or "",
            })

# Basic data validation
if len(matches) != 380:
    raise ValueError(
        f"Expected 380 matches, found {len(matches)}"
    )

# Save as CSV
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open(
    "w", newline="", encoding="utf-8-sig"
) as file:
    writer = csv.DictWriter(
        file, fieldnames=list(matches[0].keys())
    )
    writer.writeheader()
    writer.writerows(matches)

print(f"Successfully processed {len(matches)} matches.")
print(f"Saved to: {OUTPUT_FILE}")
