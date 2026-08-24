# HW1 — Best Offensive Metrics for P4 College Football (2021–2025)

## The two Python files

**`fetch_data.py`** — this python file pulls the raw data. It calls the CollegeFootballData.com (CFBD) API to get every regular-season game (2021–2025) for the 67 teams currently in a Power 4 conference (ACC, Big Ten, Big 12, SEC), along with each team's box-score stats for that game (yards, plays, third-down conversions, turnovers, etc.). It then writes everything to `team_game_stats.csv`. Something I noticed and fixed was some data is pulled per-team rather than per-conference, because several current P4 teams — USC, UCLA, Washington, Oregon, Arizona, Arizona State, Utah, Colorado, Cal, Stanford — were still in the old Pac-12 through 2023, and filtering by current conference would have missed those years' games entirely.

**`analyze_metrics.py`** — This is the code that answers the assignment. It reads the `team_game_stats.csv` and tests 9 different offensive metrics: Points per Game, Total Yards per Game, Yards per Play, Yards per Pass Attempt, Yards per Rush Attempt, Third-Down Conversion %, Completion %, Turnovers per Game, and First Downs per Game. For every team-season, it splits that team's games chronologically into a first half and second half, then computes each metric on both halves. Lastly, it prints the ranked results and the top 3.

To run it: `python3 analyze_metrics.py`.

## The math behind the conclusion

A metric is only useful for **predicting** how a team will play if it's measuring something real and consistent about that team. Metrics that can be based on luck or chance shouldn't qualify as good metrics. My idea for the homework was to test that if you look at a team's number for a metric in the *first half* of the season, does that number tell you anything about what their number will be in the *second half* of the same season?

So to measure this, I used a statistic called **Pearson correlation**, written as **r**. 

- **r** is a number between -1 and 1 that measures how closely two sets of numbers move together.
- **r close to 1** means strong relationship — a team that's high in the first half is almost always high in the second half too.
- **r close to 0** means basically no relationship — knowing a team's first-half number tells you nothing useful about their second-half number.

I also reported **R²**, which is just an easier way to read the same result. If all you knew about a team was their first-half number, and you used it to guess their second-half number, R² tells you roughly how much of that guess you'd get right. An R² of 37% means knowing a team's first half gets you about a third of the way to knowing their second half — the rest is randomness or other factors the first half can't tell you.

So in conclusion to find the best metrics **the higher the r (and R²), the more a metric reflects real, repeatable team quality rather than luck.** This in my opinion makes the best metrics.

For each of the 9 candidate metrics, I calculated this across all 335 team-seasons (67 P4 teams × 5 seasons, 2021–2025):

| Metric | r (1st half → 2nd half) | R² (% explained) |
|---|---|---|
| **Total Yards per Game** | **0.606** | 36.8% |
| **Points per Game** | **0.568** | 32.3% |
| **Yards per Play** | **0.542** | 29.4% |
| First Downs per Game | 0.537 | 28.8% |
| Completion % | 0.464 | 21.6% |
| Yards per Rush Attempt | 0.463 | 21.5% |
| Yards per Pass Attempt | 0.439 | 19.2% |
| Third-Down Conversion % | 0.382 | 14.6% |
| Turnovers per Game | 0.144 | 2.1% |

## Conclusion — the 3 best metrics

1. **Total Yards per Game (r = 0.606, R² = 0.368)** — This was the most reliable metric I tested. It collects enough plays per half-season that random single-play variance washes out, so a team's early-season yardage output is a genuinely good predictor of its later-season output.
2. **Points per Game (r = 0.568, R² = 0.323)** — This was the second best metric, but also could be the most meaningful since it's what actually wins games. It was less reliable than total yards because it's also factored with non-offensive touchdowns (special teams, defense).
3. **Yards per Play (r = 0.542, R² = 0.294)** — This was the third best metric. It trails the volume metrics slightly because a handful of explosive plays can swing a per-play average more than they swing a per-game total built from far more plays.

## Other metrics I tried

- **First Downs per Game (r = 0.537)** — This  tells you the same thing as yards and points, so to me it doesn't add much once those are already in the mix.
- **Completion % (r = 0.464) and Yards per Rush/Pass Attempt (r = 0.463 / 0.439)** — These two metrics are based on fewer plays per half-season than total yards, so a couple long completions or drops can swing them a lot more.