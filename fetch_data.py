import csv
import time
import requests

# --- load API key ---
api_key = None
with open(".env") as f:
    for line in f:
        line = line.strip()
        if line.startswith("CFBD_API_KEY"):
            api_key = line.split("=", 1)[1].strip()

headers = {"Authorization": f"Bearer {api_key}", "accept": "application/json"}
YEARS = [2021, 2022, 2023, 2024, 2025]
P4_CONFERENCES = ["ACC", "Big Ten", "Big 12", "SEC"]

# --- current P4 teams (as of 2025) ---
resp = requests.get("https://api.collegefootballdata.com/teams/fbs",
                     headers=headers, params={"year": 2025})
teams = resp.json()
p4_teams = {t["school"] for t in teams if t.get("conference") in P4_CONFERENCES}
print(f"Using {len(p4_teams)} current P4 teams.\n")


def split_pair(value):
    if not value or "-" not in str(value):
        return None, None
    made, att = str(value).split("-")
    return int(made), int(att)


rows = []
seen = set()  # (game_id, team) pairs already added, to avoid duplicates

for year in YEARS:
    print(f"Fetching {year}...")

    games_resp = requests.get("https://api.collegefootballdata.com/games",
                               headers=headers,
                               params={"year": year, "seasonType": "regular"})
    if games_resp.status_code != 200:
        print(f"  GAMES ERROR {games_resp.status_code}: {games_resp.text[:300]}")
        continue
    games_by_id = {g["id"]: g for g in games_resp.json()}

    year_row_count = 0
    for team_name in sorted(p4_teams):
        stats_resp = requests.get("https://api.collegefootballdata.com/games/teams",
                                   headers=headers,
                                   params={"year": year, "seasonType": "regular", "team": team_name})
        if stats_resp.status_code != 200:
            print(f"  STATS ERROR ({team_name}) {stats_resp.status_code}: {stats_resp.text[:300]}")
            continue
        team_stats = stats_resp.json()

        for game in team_stats:
            meta = games_by_id.get(game["id"])
            if meta is None:
                continue
            for t in game.get("teams", []):
                school = t.get("team")
                if school not in p4_teams:
                    continue
                key = (game["id"], school)
                if key in seen:
                    continue
                seen.add(key)

                sd = {s["category"]: s["stat"] for s in t.get("stats", [])}
                comp, pass_att = split_pair(sd.get("completionAttempts"))
                third_made, third_att = split_pair(sd.get("thirdDownEff"))
                rush_att = sd.get("rushingAttempts")
                rush_att = int(rush_att) if rush_att is not None else None

                plays = None
                if rush_att is not None and pass_att is not None:
                    plays = rush_att + pass_att

                rows.append({
                    "season": year,
                    "week": meta.get("week"),
                    "start_date": meta.get("startDate"),
                    "game_id": game["id"],
                    "team": school,
                    "points": t.get("points"),
                    "total_yards": sd.get("totalYards"),
                    "plays": plays,
                    "rush_attempts": rush_att,
                    "rush_yards": sd.get("rushingYards"),
                    "yards_per_rush_attempt": sd.get("yardsPerRushAttempt"),
                    "completions": comp,
                    "pass_attempts": pass_att,
                    "pass_yards": sd.get("netPassingYards"),
                    "yards_per_pass_attempt": sd.get("yardsPerPass"),
                    "third_down_made": third_made,
                    "third_down_att": third_att,
                    "turnovers": sd.get("turnovers"),
                    "first_downs": sd.get("firstDowns"),
                })
                year_row_count += 1
        time.sleep(0.15)

    print(f"  -> {year_row_count} P4 team-game rows")

if not rows:
    raise SystemExit("No rows collected — check errors above.")

fieldnames = list(rows[0].keys())
with open("team_game_stats.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\nWrote {len(rows)} total rows to team_game_stats.csv")