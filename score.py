import argparse
import csv
import json
from datetime import date

TARGET_INDUSTRIES = {"automotive", "real_estate", "luxury", "fintech"}
TARGET_COUNTRIES = {"uae", "uk", "usa", "saudi arabia"}


def parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def is_valid(row: dict, today: date) -> bool:
    signal = parse_date(row["signal_date"])
    return bool(row["website"].strip()) and signal is not None and signal <= today


def score(row: dict, today: date) -> int:
    points = 0
    age = (today - parse_date(row["signal_date"])).days
    if age <= 30:
        points += 40
    elif age <= 90:
        points += 20
    if row["industry"].strip().lower() in TARGET_INDUSTRIES:
        points += 30
    if row["country"].strip().lower() in TARGET_COUNTRIES:
        points += 30
    return points


def score_leads(rows: list[dict], today: date) -> list[dict]:
    scored = [{**row, "score": score(row, today)} for row in rows if is_valid(row, today)]
    return sorted(scored, key=lambda row: row["score"], reverse=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()

    with open("data/leads.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    leads = score_leads(rows, args.today)

    with open("data/scored.json", "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2)

    for lead in leads[:5]:
        print(f"{lead['score']:>3}  {lead['company']} ({lead['country']}, {lead['industry']})")


if __name__ == "__main__":
    main()
