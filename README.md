# SPL
SPL essentials
---

# Simulation Premier League (SPL) - www.simulationpremierleague.co.in

## Winners History

Season 0 (pilot run) : DC (jeyanth); 
Season 1 : PBKS (satkar); 
Season 2 : RR (moneybites); 
Season 3 : GT (jeyanth); 
Season 4 : RR (moneybites); 
Season 5 : LSG (godofthunder);


## Project Summary

The Simulation Premier League (SPL) is a custom-built T20 cricket simulation framework developed in Python. It replicates an IPL-style tournament using pre-processed ball-by-ball data, with a strong focus on analytics, player performance tracking, and dynamic ranking systems.

---

## 🏗️ Project Structure

>. SPL simulates matches based on cricket-specific datasets, maintaining realistic match progression.
>. Each match is broken down into ball-by-ball records, including batter, bowler, runs, dismissals, etc.
>. Matches are grouped into seasons with persistent tracking across seasons.
>. The simulation doesn't rely on real-time updates; all stats are computed pre-match and visualized post-match.
>. SPL does not depend on live APIs, making it a fully offline, stat-driven engine.
>. Data sources are typically Excel or CSV files manually curated and cleaned.
>. Match plots and stat summaries are stored in local folders named by season and match IDs.

---

## ⚙️ Core Components

>. Match simulation engine handles batting, bowling, innings switch, and fall-of-wicket logic.
>. Special logic is implemented to calculate partnerships and FOW sequences.
>. Dot balls, boundaries, extras, and wickets are captured with high granularity.
>. Teams and players are predefined, with dynamic updates post-match.
>. Simulation results are deterministic based on the input files (non-random).
>. Every game contributes to evolving season stats and rankings.

---

## 📈 Player Ranking System

>. SPL uses custom metrics to evaluate players beyond traditional statistics.
>. Batters and bowlers are ranked separately with unique weightings.
>. Rankings are updated after each game.
>. No player reputation or historical bias is used — stats emerge from the current season only.
>. Minimum matches/balls thresholds apply before a player is ranked.
>. Metrics include performance indices, impact scores, and consistency checks.

---

## 🧠 Batter Metrics

>. Wicket Stability Index (WSI): Measures consistency and resilience under pressure.
>. Momentum Impact Score (MIS): Quantifies game tempo acceleration by a batter.
>. Pressure Conversion Rate: Runs scored under match pressure situations.
>. Partnership Dominance Ratio: Contribution % in key stands.
>. Clutch Strike Rate: Strike rate during crucial overs (e.g., 16-20).
>. Recent Form Index: Rolling average from the last 3 matches.
and many more.

---

## 🎯 Bowler Metrics

>. Wicket Impact Index: Adjusted by batting position of dismissed players.
>. Dot Pressure Index: Measures build-up pressure via dot balls.
>. Clutch Over Index: Wickets or economy in crunch overs (e.g., 18-20).
>. Bowling Efficiency Rating: Composite of economy, wickets, dot rate.
>. Match Impact Quotient: Combines wicket count and deviation from match average.
>. Expected Runs Saved (ERS): Based on expected runs vs. actual conceded.
>. Choke Rate: Frequency of bowling tight overs in high-pressure situations.
>. Partnership-breaker Index: Measures ability to break big partnerships.
>. Last-3 Form: Averages from the last 3 games.
>. Minimum threshold: 5 matches and 100 balls bowled to qualify.
and many more.

---

## 📊 Match-Level Stats

>. Each match stores stats like 1st innings score, 2nd innings chase, pitch behavior.
>. Win/loss results, margins, and venue info are stored.
>. Team strategies (bat 1st vs 2nd) are tracked per team and season.
>. Each player’s match performance is individually logged and aggregated.
>. Run progression and partnership breakdowns are plotted for each match.

---

## 💾 File Management

>. Data, plots, and metrics are all saved locally.
>. Github database is used for some data.

---

## 🧠 Design Philosophy

>. Accuracy of simulation > randomness or unpredictability.
>. Focus on statistical fairness and consistency.
>. Player performance should emerge *from data*, not assumptions.
>. Roles (finisher, anchor, death bowler) are inferred, not assigned.
>. Visual storytelling through plots and indexes is a core feature.

---

## 🧮 Miscellaneous Features

>. Match momentum shifts are planned for future metrics.
>. DLS or rain interruptions are currently *not* simulated.
>. Simulation speed is fast due to pre-computed logic (no loops during sim).
>. Game logic is deterministic; no coin toss-based decisions.
>. External player reputation/history is intentionally excluded.
>. The simulation encourages new patterns to emerge from performance alone.

---

## 🔍 Analytical Strength

>. SPL produces novel insights like:

* Clutch player rankings
* Finisher effectiveness
* Death overs bowling value
* Partnership dependencies

>. All indices are designed to be interpretable.
>. Metrics evolve through iteration — no fixed formula is sacred.
>. Summary tables for each match, team, and player are auto-generated.
>. The system supports filtering by match, player, team, phase, or stat.

---

## 🗂️ Usage Summary

>. Run the simulation manually, season-by-season.
>. Outputs are saved as local plots and CSVs.
>. Code is written in Python, with libraries like Pandas, NumPy, Matplotlib.
>. Some automation scripts are used for batch processing of seasons.
>. Simulation engine runs on a local machine (no GPU needed).
>. SPL is modular, allowing updates to only a part (e.g., bowler metric tweaks).
>. Match IDs and player IDs are primary keys for linking data.
>. Player form tracking adds realism.
>. Each new match recalibrates the entire player ranking system.
>. SPL is a growing project, with scope for integration, web hosting, and storytelling.

-----
