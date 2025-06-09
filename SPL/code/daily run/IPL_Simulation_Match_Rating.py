#!/usr/bin/env python
# coding: utf-8

# ## the functions

# In[67]:


import re
from contextlib import redirect_stdout

TEAM_NAMES = ["CSK", "DC", "GT", "KKR", "LSG", "MI", "PBKS", "RCB", "RR", "SRH"]


# In[68]:


def parse_matchcard(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    innings_data = {}
    player_scores = []
    bowler_stats = []
    total_boundaries = 0
    final_scores = {}
    current_team = None
    team_batting_order = []

    for line in lines:
        line = line.strip()

        # Detect team names from match headline
        if "Match between" in line:
            match = re.findall(rf"\b({'|'.join(TEAM_NAMES)})\b", line)
            if len(match) == 2:
                team_batting_order = match  # [team1, team2]

        # Detect which team is batting
        for team in TEAM_NAMES:
            if f"{team} BATTING" in line:
                current_team = team
                innings_data[current_team] = []

        # Extract player batting line
        if re.match(r"^``` .* \| .* \| .* \|", line):
            if current_team:
                parts = re.findall(r"\d+", line)
                if len(parts) >= 5:
                    runs = int(parts[0])
                    fours = int(parts[3])
                    sixes = int(parts[4])
                    player_scores.append((current_team, runs))
                    total_boundaries += (fours + sixes)

        # Extract bowler stats
        if line.startswith("```") and "|" in line and "balls" in line:
            parts = re.findall(r"\d+", line)
            if len(parts) >= 4:
                wkts = int(parts[2])
                bowler_stats.append(wkts)

        # Final score for innings
        if line.startswith("Score ::"):
            score_match = re.search(r"Score :: (\d+)-(\d+)", line)
            if score_match and current_team:
                runs, wkts = map(int, score_match.groups())
                final_scores[current_team] = (runs, wkts)

    # Result
    result_line = next((line for line in lines if any(f"{team} wins" in line for team in TEAM_NAMES)), "")
    winner = next((team for team in TEAM_NAMES if f"{team} wins" in result_line), None)

    return {
        "final_scores": final_scores,
        "boundaries": total_boundaries,
        "fifties": sum(1 for _, r in player_scores if r >= 50),
        "three_wkt_hauls": sum(1 for w in bowler_stats if w >= 3),
        "winner": winner
    }


# In[69]:


def parse_ball_by_ball(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    over_data = []
    runs_in_over = 0
    wickets_in_over = 0
    last_over_runs_required = None
    rrr_by_over = []
    teams = []
    second_innings_started = False
    over_num = 0

    for i, line in enumerate(lines):
        line = line.strip()

        # Detect teams from match header
        if line.startswith("match") and "::" in line:
            match = re.findall(rf"\b({'|'.join(TEAM_NAMES)})\b", line)
            if len(match) == 2:
                teams = match

        # Detect start of second innings
        if "INNING 1 IS OVER" in line:
            second_innings_started = True

        # Parse required run rate
        if second_innings_started and "Required Run-rate" in line:
            match = re.search(r"Required Run-rate\s*=\s*([\d.]+)", line)
            if match:
                rrr = float(match.group(1))
                rrr_by_over.append((over_num + 1, rrr))  # Map to next over (runs needed after this over)

        # Parse end of over
        if "end of over" in line:
            match = re.search(r"over (\d+); score :: \*\*(\d+)\*\* for \*\*(\d+)\*\*", line)
            if match and second_innings_started:
                over_num = int(match.group(1))
                over_data.append({
                    "over": over_num,
                    "runs": runs_in_over,
                    "wickets": wickets_in_over
                })
                runs_in_over = 0
                wickets_in_over = 0

        # Count runs/wickets in second innings
        if second_innings_started:
            if "WICKET" in line.upper():
                wickets_in_over += 1

            run_search = re.search(r": (six|four|three|two|one|\d+|wide|noball|dot)", line)
            if run_search:
                val = run_search.group(1)
                if val == "six": runs_in_over += 6
                elif val == "four": runs_in_over += 4
                elif val == "three": runs_in_over += 3
                elif val == "two": runs_in_over += 2
                elif val == "one": runs_in_over += 1
                elif val in ["wide", "noball"]: runs_in_over += 1
                elif val.isdigit(): runs_in_over += int(val)

        # Runs remaining in last over
        if second_innings_started and "Runs remaining =" in line:
            rem = re.findall(r"=\s*(\d+)", line)
            if rem:
                last_over_runs_required = int(rem[0])

    return {
        "over_data": over_data,
        "last_over_target": last_over_runs_required,
        "rrr_by_over": rrr_by_over,
        "batting_team": teams[1] if len(teams) == 2 else None
    }


# In[70]:


def compute_match_rating(matchcard_data, ball_data):
    rating = 0
    breakdown = {}

    # --- Closeness of Result (30 points) ---    
    # determine winner and second innings team
    winner = matchcard_data["winner"]
    scores = matchcard_data["final_scores"]

    team1, team2 = list(scores.keys())
    first_innings_score = scores[team1][0]  # team1 batted first
    second_innings_score = scores[team2][0]

    # if the chasing team won
    if winner == team2 and second_innings_score >= first_innings_score:
        # find when the chase ended
        chase_overs = ball_data["over_data"][-1]["over"]
        balls_in_final_over = ball_data["over_data"][-1]["runs"]  # not precise but acceptable proxy

        # conservative estimate: match ended in 20th over if over == 20
        if chase_overs == 20:
            pts = 30
        elif chase_overs >= 19:
            pts = 20
        elif chase_overs >= 18:
            pts = 10
        elif chase_overs >= 17:
            pts = 5
        else:
            pts = 0
        margin = 0
    else:
        # fallback to run-margin logic
        margin = first_innings_score - second_innings_score
        if margin <= 5:
            pts = 30
        elif margin <= 10:
            pts = 20
        elif margin <= 20:
            pts = 10
        else:
            pts = 0

    rating += pts
    breakdown["Closeness"] = pts




    """
    scores = list(matchcard_data["final_scores"].values())
    score1, score2 = scores[0][0], scores[1][0]
    margin = abs(score1 - score2)

    if margin <= 5:
        pts = 30
    elif margin <= 10:
        pts = 20
    elif margin <= 20:
        pts = 10
    else:
        pts = 0
    rating += pts
    breakdown["Closeness"] = pts

    """
    # --- Momentum Shifts (15 points) ---
    momentum_shifts = 0
    for over in ball_data["over_data"]:
        if over["runs"] >= 18 or over["wickets"] >= 2:
            momentum_shifts += 1

    if momentum_shifts >= 4:
        pts = 15
    elif momentum_shifts >= 2:
        pts = 10
    elif momentum_shifts == 1:
        pts = 5
    else:
        pts = 0
    rating += pts
    breakdown["Momentum Shifts"] = pts

    # --- High Impact Performances (15 points) ---
    high_impact = min((matchcard_data["fifties"] * 3 + matchcard_data["three_wkt_hauls"] * 3), 15)
    rating += high_impact
    breakdown["High Impact Performances"] = high_impact

    
    # --- Boundary Count (10 points) ---
    boundaries = matchcard_data["boundaries"]
    if boundaries >= 40:
        pts = 10
    elif boundaries >= 30:
        pts = 7
    elif boundaries >= 20:
        pts = 5
    else:
        pts = 0
    rating += pts
    breakdown["Boundary Count"] = pts

    
    # --- Final Over Drama (10 points) ---
    final_over_target = ball_data["last_over_target"]
    if final_over_target is not None:
        if final_over_target <= 12 and margin <= 6:
            pts = 10
        elif final_over_target <= 20:
            pts = 5
        else:
            pts = 0
    else:
        pts = 0
    rating += pts
    breakdown["Final Over Drama"] = pts

    # --- Required Run Rate Swings (20 points) ---
    rrr_swings = 0
    prev_rrr = None
    for _, rrr in ball_data.get("rrr_by_over", []):
        if prev_rrr is not None and abs(rrr - prev_rrr) >= 1.0:
            rrr_swings += 1
        prev_rrr = rrr

    if rrr_swings >= 3:
        pts = 20
    elif rrr_swings == 2:
        pts = 15
    elif rrr_swings == 1:
        pts = 10
    else:
        pts = 0
    rating += pts
    breakdown["RRR Swings"] = pts

    # --- Final Result ---
    final_rating = round(rating / 10, 1)
    return final_rating, breakdown


# In[ ]:





# ## applying

# In[72]:



matchcard_path = f"/Users/roumyadas/Desktop/IPL_Simulation/Season_02/Scorecards/matchcard_S02M0{match}.txt"
bbb_path = f'/Users/roumyadas/Desktop/IPL_Simulation/Season_02/Match_flows/ball-by-ball_{int(match)}.txt'

matchcard_data = parse_matchcard(matchcard_path)
ball_data = parse_ball_by_ball(bbb_path)
rating, breakdown = compute_match_rating(matchcard_data, ball_data)

# Specify the output file
output_file = "/Users/roumyadas/Desktop/IPL_Simulation/Season_02/Match_Rating/Match_" + str(match) + ".txt"

# Redirect the output
with open(output_file, "w") as f:
    with redirect_stdout(f):
        print(f" >> Match Rating: {rating}/10")
        print(" >> Breakdown:")
        for k, v in breakdown.items():
            print(f"- {k}: {v} points")
            
    print(f"All output has been saved to {output_file}")


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




