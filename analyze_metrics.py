import math
import pandas as pd

MIN_GAMES_PER_SEASON = 10  # need enough games that each half is meaningful

CANDIDATE_METRICS = [
    "points_per_game",
    "yards_per_game",
    "yards_per_play",
    "yards_per_pass_attempt",
    "yards_per_rush_attempt",
    "third_down_pct",
    "completion_pct",
    "turnovers_per_game",
    "first_downs_per_game",
]

PRETTY_NAMES = {
    "points_per_game": "Points per Game",
    "yards_per_game": "Total Yards per Game",
    "yards_per_play": "Yards per Play",
    "yards_per_pass_attempt": "Yards per Pass Attempt",
    "yards_per_rush_attempt": "Yards per Rush Attempt",
    "third_down_pct": "Third-Down Conversion %",
    "completion_pct": "Completion %",
    "turnovers_per_game": "Turnovers per Game",
    "first_downs_per_game": "First Downs per Game",
}


def compute_half_metrics(half_df):
    total_plays = half_df["plays"].sum()
    total_yards = half_df["total_yards"].sum()
    pass_att_sum = half_df["pass_attempts"].sum()
    rush_att_sum = half_df["rush_attempts"].sum()
    third_att_sum = half_df["third_down_att"].sum()

    return {
        "points_per_game": half_df["points"].mean(),
        "yards_per_game": half_df["total_yards"].mean(),
        "yards_per_play": (total_yards / total_plays) if total_plays else None,
        "yards_per_pass_attempt": (half_df["pass_yards"].sum() / pass_att_sum) if pass_att_sum else None,
        "yards_per_rush_attempt": (half_df["rush_yards"].sum() / rush_att_sum) if rush_att_sum else None,
        "third_down_pct": (half_df["third_down_made"].sum() / third_att_sum) if third_att_sum else None,
        "completion_pct": (half_df["completions"].sum() / pass_att_sum) if pass_att_sum else None,
        "turnovers_per_game": half_df["turnovers"].mean(),
        "first_downs_per_game": half_df["first_downs"].mean(),
    }


def build_half_table(df):
    rows = []
    for (team, season), group in df.sort_values("week").groupby(["team", "season"]):
        if len(group) < MIN_GAMES_PER_SEASON:
            continue
        n = len(group)
        cut = math.ceil(n / 2)
        first, second = group.iloc[:cut], group.iloc[cut:]
        if len(first) < 4 or len(second) < 4:
            continue

        first_m = compute_half_metrics(first)
        second_m = compute_half_metrics(second)
        row = {"team": team, "season": season, "games": n}
        for m in CANDIDATE_METRICS:
            row[f"{m}__first"] = first_m[m]
            row[f"{m}__second"] = second_m[m]
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    df = pd.read_csv("team_game_stats.csv")
    half_table = build_half_table(df)
    half_table.to_csv("team_season_half_splits.csv", index=False)

    summary_rows = []
    for m in CANDIDATE_METRICS:
        sub = half_table[[f"{m}__first", f"{m}__second"]].dropna()
        if len(sub) < 5:
            continue
        r = sub[f"{m}__first"].corr(sub[f"{m}__second"])
        summary_rows.append({
            "metric": PRETTY_NAMES[m],
            "n_team_seasons": len(sub),
            "first_half_to_second_half_r": round(r, 3),
            "r_squared": round(r ** 2, 3),
        })

    summary = pd.DataFrame(summary_rows).sort_values(
        "first_half_to_second_half_r", ascending=False
    ).reset_index(drop=True)
    summary.to_csv("metric_reliability_summary.csv", index=False)

    print(f"\nSample: {half_table['team'].nunique()} teams, "
          f"{half_table['season'].nunique()} seasons, "
          f"{len(half_table)} team-seasons (>= {MIN_GAMES_PER_SEASON} games each)\n")
    print("=== First-half vs second-half reliability, by metric (higher r = more predictive) ===\n")
    print(summary.to_string(index=False))

    print("\n=== TOP 3 ===")
    for _, row in summary.head(3).iterrows():
        print(f" - {row['metric']}: r = {row['first_half_to_second_half_r']} "
              f"(R^2 = {row['r_squared']}, n = {row['n_team_seasons']})")


if __name__ == "__main__":
    main()