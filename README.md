# SPL
SPL essentials
---

# Simulation Premier League (SPL) - www.simulationpremierleague.co.in

## Winners History

Season 0 (pilot run) : DC (jeyanth)
Season 1 : PBKS (satkar)
Season 2 : RR (moneybites)
Season 3 : GT (jeyanth)
Season 4 : RR (moneybites)


## Project Summary

The Simulation Premier League (SPL) is a custom-built T20 cricket simulation framework developed in Python. It replicates an IPL-style tournament using pre-processed ball-by-ball data, with a strong focus on analytics, player performance tracking, and dynamic ranking systems.

---

## 🏗️ Project Structure

1. SPL simulates matches based on cricket-specific datasets, maintaining realistic match progression.
2. Each match is broken down into ball-by-ball records, including batter, bowler, runs, dismissals, etc.
3. Matches are grouped into seasons (e.g., Season\_01, Season\_02), with persistent tracking across seasons.
4. The simulation doesn't rely on real-time updates; all stats are computed pre-match and visualized post-match.
5. SPL does not depend on live APIs, making it a fully offline, stat-driven engine.
6. Data sources are typically Excel or CSV files manually curated and cleaned.
7. Match plots and stat summaries are stored in local folders named by season and match IDs.

---

## ⚙️ Core Components

8. Match simulation engine handles batting, bowling, innings switch, and fall-of-wicket logic.
9. Special logic is implemented to calculate partnerships and FOW sequences.
10. Dot balls, boundaries, extras, and wickets are captured with high granularity.
11. Teams and players are predefined, with dynamic updates post-match.
12. Simulation results are deterministic based on the input files (non-random).
13. Every game contributes to evolving season stats and rankings.

---

## 📈 Player Ranking System

14. SPL uses custom metrics to evaluate players beyond traditional statistics.
15. Batters and bowlers are ranked separately with unique weightings.
16. Rankings are updated after each game, beginning from match 2 (not match 1).
17. No player reputation or historical bias is used — stats emerge from the current season only.
18. Minimum matches/balls thresholds apply before a player is ranked.
19. Metrics include performance indices, impact scores, and consistency checks.

---

## 🧠 Batter Metrics

20. Wicket Stability Index (WSI): Measures consistency and resilience under pressure.
21. Momentum Impact Score (MIS): Quantifies game tempo acceleration by a batter.
22. Pressure Conversion Rate: Runs scored under match pressure situations.
23. Partnership Dominance Ratio: Contribution % in key stands.
24. Clutch Strike Rate: Strike rate during crucial overs (e.g., 16-20).
25. Recent Form Index: Rolling average from the last 3 matches.

---

## 🎯 Bowler Metrics

26. Wicket Impact Index: Adjusted by batting position of dismissed players.
27. Dot Pressure Index: Measures build-up pressure via dot balls.
28. Clutch Over Index: Wickets or economy in crunch overs (e.g., 18-20).
29. Bowling Efficiency Rating: Composite of economy, wickets, dot rate.
30. Match Impact Quotient: Combines wicket count and deviation from match average.
31. Expected Runs Saved (ERS): Based on expected runs vs. actual conceded.
32. Choke Rate: Frequency of bowling tight overs in high-pressure situations.
33. Partnership-breaker Index: Measures ability to break big partnerships.
34. Last-3 Form: Averages from the last 3 games.
35. Minimum threshold: 5 matches and 100 balls bowled to qualify.

---

## 📊 Match-Level Stats

36. Each match stores stats like 1st innings score, 2nd innings chase, pitch behavior.
37. Win/loss results, margins, and venue info are stored in a `df_sim` object.
38. Team strategies (bat 1st vs 2nd) are tracked per team and season.
39. Each player’s match performance is individually logged and aggregated.
40. Run progression and partnership breakdowns are plotted for each match.

---

## 🖼️ Visual Outputs

41. Match-wise plots are generated using Matplotlib.
42. Partnership plots are aligned to avoid text overlap with y-axis.
43. Y-ticks are forced to show all partnerships (1 to N).
44. Plots are stored as `.jpg` files in `Season_XX/plots/` directories.
45. Image filenames use match IDs for traceability.

---

## 🛠️ Data Processing Logic

46. Excel sheets are loaded using `pd.read_excel(sheet_name=None)` to get all tabs.
47. Sheets are converted into a list of DataFrames for iterative processing.
48. Players’ names are cleaned (e.g., replacing full names with initials).
49. Duplicate values are dropped using subset of multiple columns.
50. Batting and bowling orders are used to infer roles (e.g., part-timer detection).
51. Dismissal types and partnerships are extracted and merged with match-level data.
52. Ball-by-ball objects are filtered and grouped using `groupby` operations.
53. Partnerships are calculated incrementally using row-wise logic.
54. Role-based filters are applied to identify specialists vs. part-timers.

---

## 🤖 Part-Timer Detection Logic

55. Part-time bowlers are defined based on balls bowled per innings.
56. Bowlers with low workload and low frequency across matches are tagged as part-timers.
57. This tagging is used in metrics like Wicket Impact Index to adjust scores.
58. Edge cases (e.g., bowlers used in just one game) are excluded unless thresholds met.

---

## 💾 File Management

59. Data, plots, and metrics are all saved locally.
60. No database or cloud storage is used (yet).
61. Future plans might include hosting on a static website (e.g., GitHub Pages).
62. CSVs and plots follow strict naming formats (`match_id.jpg`, `season_summary.csv`, etc.).

---

## 🔍 Future Enhancements

63. Integration with ranking pages or dashboards via React/Plotly.
64. Creation of a frontend layer for season-wise navigation.
65. Hosting pre-computed stats on GitHub or OneDrive as static content.
66. Introduction of MVP algorithms based on match impact.
67. Development of a team-wise tactical evaluation system.
68. Incorporation of advanced ML models for player projection.
69. Simulation of auctions or mid-season transfers.
70. Simulated injury or form fluctuations for added realism.

---

## 🧠 Design Philosophy

71. Accuracy of simulation > randomness or unpredictability.
72. Focus on statistical fairness and consistency.
73. Player performance should emerge *from data*, not assumptions.
74. Roles (finisher, anchor, death bowler) are inferred, not assigned.
75. Visual storytelling through plots and indexes is a core feature.

---

## 🧮 Miscellaneous Features

76. `df_sim` is the central simulation object with match meta.
77. Player names may be shortened or replaced consistently for brevity.
78. Team abbreviations and color codes are stored separately (if visualized).
79. Match momentum shifts are planned for future metrics.
80. DLS or rain interruptions are currently *not* simulated.
81. Batting and bowling powerplay stats are optionally extractable.
82. Simulation speed is fast due to pre-computed logic (no loops during sim).
83. Game logic is deterministic; no coin toss-based decisions.
84. External player reputation/history is intentionally excluded.
85. The simulation encourages new patterns to emerge from performance alone.

---

## 🔍 Analytical Strength

86. SPL produces novel insights like:

* Clutch player rankings
* Finisher effectiveness
* Death overs bowling value
* Partnership dependencies

87. All indices are designed to be interpretable.
88. Metrics evolve through iteration — no fixed formula is sacred.
89. Summary tables for each match, team, and player are auto-generated.
90. The system supports filtering by match, player, team, phase, or stat.

---

## 🗂️ Usage Summary

91. Run the simulation manually, season-by-season.
92. Outputs are saved as local plots and CSVs.
93. Code is written in Python, with libraries like Pandas, NumPy, Matplotlib.
94. Some automation scripts are used for batch processing of seasons.
95. Simulation engine runs on a local machine (no GPU needed).
96. SPL is modular, allowing updates to only a part (e.g., bowler metric tweaks).
97. Match IDs and player IDs are primary keys for linking data.
98. Player form tracking (rolling 3-match window) adds realism.
99. Each new match recalibrates the entire player ranking system.
100. SPL is a growing project, with scope for integration, web hosting, and storytelling.

-----
