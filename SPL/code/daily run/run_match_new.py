#!/usr/bin/env python
# coding: utf-8

# In[1]:


import discord
import random
import os
import asyncio
from collections import Counter, defaultdict
import pandas as pd
import requests


# In[2]:
def has_consecutive_duplicates(lst):
    return any(lst[i] == lst[i+1] for i in range(len(lst)-1))
def generate_sequence():
    sequence = [1, 2]  # Start with 1,2
    count = Counter({i: 0 for i in range(1, 6)})
    count[1], count[2] = 1, 1
    
    # Helper function to get a valid next number avoiding consecutive repeats
    def get_valid_number(choices, last_num):
        valid_choices = [n for n in choices if n != last_num]
        return random.choice(valid_choices) if valid_choices else choices[0]
    
    # 3rd and 4th number (1 or 2 with 0.8 probability)
    for _ in range(2):
        if random.random() < 0.8:
            choices = [n for n in [1, 2] if count[n] < 4]
        else:
            choices = [n for n in [3, 4, 5] if count[n] < 4]
        num = get_valid_number(choices, sequence[-1])
        sequence.append(num)
        count[num] += 1
    
    # Fill 5th to 15th numbers (prioritizing 3 to 5)
    while len(sequence) < 15:
        choices = [n for n in range(3, 6) if count[n] < 4]
        if not choices:
            choices = [n for n in [1, 2] if count[n] < 4]  # If 3-5 are exhausted, use 1 or 2
        num = get_valid_number(choices, sequence[-1])
        sequence.append(num)
        count[num] += 1
    
    # Ensure at least 2 occurrences of either 1 or 2 remain for last 5 numbers
    left_1 = 4 - count[1]
    left_2 = 4 - count[2]
    
    needed_1 = max(0, 2 - left_1)
    needed_2 = max(0, 1 - left_2)
    needed = needed_1 + needed_2
    
    for _ in range(needed):
        replace_idx = random.choice([i for i in range(5, 15) if sequence[i] in [3, 4, 5]])
        removed = sequence[replace_idx]
        count[removed] -= 1
        sequence[replace_idx] = get_valid_number([1, 2], sequence[replace_idx - 1])
        count[sequence[replace_idx]] += 1
    
    # Fill last 5 numbers ensuring exactly 4 appearances of each number
    remaining = [n for n in range(1, 6) for _ in range(4 - count[n])]
    random.shuffle(remaining)
    
    while len(sequence) < 20:
        num = get_valid_number(remaining, sequence[-1])
        sequence.append(num)
        count[num] += 1
        remaining.remove(num)
    
    return sequence

#########################
# Helper function to determine the phase of an over
def get_phase(over):
    if over <= 6:
        return 'P'
    elif over <= 15:
        return 'M'
    else:
        return 'D'

# Function to generate the bowling sequence
def generate_bowling_order(bowler_dict, max_overs=4):
    # Phase-wise bowler allocation
    phase_bowlers = defaultdict(list)
    for bowler, phases in bowler_dict.items():
        for p in phases:
            phase_bowlers[p].append(bowler)

    # Helper function to check if a bowler can bowl a specific over
    def can_bowl(bowler, count, phase, pp_tracker, middle_tracker):
        if count[bowler] >= max_overs:
            return False
        if phase == 'P' and bowler in all_phase_bowlers and pp_tracker[bowler] >= 2:
            return False
        if phase == 'M' and bowler in all_phase_bowlers and middle_tracker[bowler] >= 1:
            return False
        return True

    # Start filling the bowling order
    sequence = [None] * 20  # Initialize a sequence with 20 slots
    count = Counter()  # Counter for the number of overs bowled by each bowler
    pp_tracker = Counter()  # To track how many overs a bowler has bowled in PP
    middle_tracker = Counter()  # To track how many overs a bowler has bowled in M
    
    # Identifying bowlers who are available for all 3 phases (P, M, D)
    all_phase_bowlers = [b for b, phases in bowler_dict.items() if 'P' in phases and 'M' in phases and 'D' in phases]
    
    # Prioritize bowlers for PowerPlay and pick top 2 for the first two overs
    top_p_bowlers = [b for b in bowler_dict if 'P' in bowler_dict[b]]
    top_p_bowlers.sort(key=lambda bowler: bowler_dict[bowler].count('P'), reverse=True)  # Prioritize based on P-phase count
    
    # Ensure the first two overs are bowled by the top two priority bowlers in PP
    sequence[0], sequence[1] = top_p_bowlers[0], top_p_bowlers[1]
    count[sequence[0]] += 1
    count[sequence[1]] += 1
    if sequence[0] in all_phase_bowlers:
        pp_tracker[sequence[0]] += 1
    if sequence[1] in all_phase_bowlers:
        pp_tracker[sequence[1]] += 1

    # Now fill the rest of the overs
    prev_bowler = sequence[1]  # Start from the third over
    for over in range(2, 20):
        phase = get_phase(over + 1)
        available_bowlers = [b for b in phase_bowlers[phase] if b != prev_bowler and can_bowl(b, count, phase, pp_tracker, middle_tracker)]
        if not available_bowlers:
            raise RuntimeError(f"No valid bowlers available for over {over + 1}")
        
        # Randomly shuffle the available bowlers and choose one
        chosen_bowler = random.choice(available_bowlers)
        sequence[over] = chosen_bowler
        count[chosen_bowler] += 1
        if phase == 'P' and chosen_bowler in all_phase_bowlers:
            pp_tracker[chosen_bowler] += 1
        if phase == 'M' and chosen_bowler in all_phase_bowlers:
            middle_tracker[chosen_bowler] += 1
        
        # Update the previous bowler
        prev_bowler = chosen_bowler
    
    return sequence


# In[3]:


import pandas as pd
import glob
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

#bat_stat = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_01/Stats/batter_stats.csv')
#bowl_stat = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_01/Stats/bowler_stats.csv')

bat_stat = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/updates_/separate_stats.xlsx', sheet_name='Bat')
bowl_stat = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/updates_/separate_stats.xlsx', sheet_name='Bowl')
bat_phase = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/updates_/separate_stats.xlsx', sheet_name='BAT_phase')
bowl_phase = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/updates_/separate_stats.xlsx', sheet_name='BOWL_phase')
h2h_ = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/updates_/separate_stats.xlsx', sheet_name='h2h')
pace_stat = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/updates_/separate_stats.xlsx', sheet_name='pace')
spin_stat = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/updates_/separate_stats.xlsx', sheet_name='spin')
form_bat = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/updates_/separate_stats.xlsx', sheet_name='form_bat')
form_ball = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/updates_/separate_stats.xlsx', sheet_name='form_bowl')

#dataframes = [bat_stat,bowl_stat]
bat_stat['Bat_avg'] = np.round(bat_stat['Bat_avg'],2)
form_bat['bat_avg'] = np.round(form_bat['bat_avg'],2)
form_bat['bat_sr'] = np.round(form_bat['bat_sr'],2)
form_ball['bowl_eco'] = np.round(form_ball['bowl_eco'],2)
form_ball['bowl_sr'] = np.round(form_ball['bowl_sr'],2)



import random  

def next_batsman():
    "Fetch the next available batter from the batting order."
    global batting_order_iterator  # Use the global iterator to keep the sequence

    try:
        next_batter = next(batting_order_iterator)
        while next_batter in dismissed_batters:
            next_batter = next(batting_order_iterator)  # Skip dismissed batters
    except StopIteration:
        next_batter = None  # No more batters available (all-out scenario)

    return next_batter


#########################
from contextlib import redirect_stdout

#g_factor = g_factor
m = match_number
a = 125
#m = globals()['i']
for i in range(m, m+1):

    df_all = df_all
    ground_factor = ground_factor
    teams = matches_list.iloc[i][1:].values[0], matches_list.iloc[i][1:].values[1]
    ############
    ground = teams[0]
    #######
    random.seed(4)
    ## 1 --> Home, Bat ; 4 --> Home, Bowl ; 5 --> Away, Bowl ; 7 --> Away, Bat ##
    #######
    toss_winner = random.sample((0,1),1)[0]
    toss_win_team = teams[toss_winner]
    other_team = teams[1-toss_winner]
    decision = random.sample(('Bat','Bowl'),1)[0]

    if decision=='Bat':
        batting_team = team_map(toss_win_team)
        bowling_team = team_map(other_team)
    else:
        bowling_team = team_map(toss_win_team)
        batting_team = team_map(other_team)
        
    output_file = "/Users/roumyadas/Desktop/IPL_Simulation/Season_02/Match_flows/ball-by-ball_" + str(m+1) + ".txt"
    
    # Redirect the output
    with open(output_file, "w") as f:
        with redirect_stdout(f):

            print(f"match {i+1}:: {teams[0]} vs {teams[1]}")
            print(f"toss :: {toss_win_team} wins, and will {decision} first!")

            ####################################################################################################
            ####################################################################################################
            ####################################################################################################
            ####################################################################################################


            ## inning 1

            m_id = 'S02M00' + str(i+1) if i<9 else 'S02M0' + str(i+1)

            current_date = matches_list.iloc[i][0]

            match_context = {
                'match_id': m_id,
                'season': 2,
                'start_date': current_date,
                'venue': ground,  
                'innings': 1,
                'ball': 1
            }
            fixed = False

            # Placeholder for output DataFrame
            columns = ['match_id', 'season', 'start_date', 'venue', 'innings', 'ball',
                       'batting_team', 'bowling_team', 'striker', 'non_striker', 'bowler',
                       'runs_off_bat', 'extras', 'wides', 'noballs', 'byes', 'legbyes',
                       'wicket_type', 'player_dismissed','legal_balls_bowled']

            df_simulation = pd.DataFrame(columns=columns)

            fow = 0
            fow_balls = 0

            batting_order = batting_team.Func_Name.values
            #print(batting_order[5])
            bowling_order = bowling_team[~(bowling_team.bowl.isna())].Func_Name.values

            if len(bowling_order)==5:
                fixed = True
                # Main loop
                while True:
                    sequence = generate_sequence()
                    
                    if not has_consecutive_duplicates(sequence):
                        break
                fixed_order = sequence
                #print(fixed_order)

            fielder_list = bowling_team[~(bowling_team['wk']==1)].Func_Name.values.tolist()
            #print(fielder_list)
            wk = bowling_team[bowling_team['wk']==1].Func_Name.unique()[0]
            #print(wk)
            total_list = fielder_list + [wk]
            #print("fielder LIST -- ", total_list)

            # Initial striker, non-striker, and bowler
            striker = batting_order[0]
            non_striker = batting_order[1]
            try:
                striker_ssn_stat = bat_stat[bat_stat.striker==striker][['num_innings','runs','SR','Bat_avg']].values.tolist()[0]
                striker_form_stat = form_bat[form_bat.striker==striker][['num_innings','runs','bat_sr','bat_avg']].values.tolist()[0]
            except:
                striker_ssn_stat = [0, 0, 'not played', 'not played']
                striker_form_stat = [0, 0, 'not played', 'not played']
            try:
                non_striker_ssn_stat = bat_stat[bat_stat.striker==non_striker][['num_innings','runs','SR','Bat_avg']].values.tolist()[0]
                non_striker_form_stat = form_bat[form_bat.striker==non_striker][['num_innings','runs','bat_sr','bat_avg']].values.tolist()[0]
            except:
                non_striker_ssn_stat = [0,0, 'not played', 'not played']
                non_striker_form_stat = [0, 0, 'not played', 'not played']

            print("^'^'^'"*4)
            print(" "*10)
            print("Openers :-")
            print(" "*10)
            print(f"Striker -> {striker} \n SPL Career:: \n Innings = {int(striker_ssn_stat[0])}, Runs = {int(striker_ssn_stat[1])}, SR = {striker_ssn_stat[2]}, Avg = {striker_ssn_stat[3]}")
            print(" "*10)
            print(f"Recent Form:: \n (last {int(striker_form_stat[0])} Innings) Runs = {int(striker_form_stat[1])}, SR = {striker_form_stat[2]}, Avg = {striker_form_stat[3]}")
            print(" "*10)
            print(f"Non-Striker -> {non_striker} \n SPL Career:: \n Innings = {int(non_striker_ssn_stat[0])}, Runs = {int(non_striker_ssn_stat[1])}, SR = {non_striker_ssn_stat[2]}, Avg = {non_striker_ssn_stat[3]}")
            print(" "*10)
            print(f"Recent Form:: \n (last {int(non_striker_form_stat[0])} Innings) Runs = {int(non_striker_form_stat[1])}, SR = {non_striker_form_stat[2]}, Avg = {non_striker_form_stat[3]}")
            print(" "*10)
            print("^'^'^'"*4)
            print(" "*10)

            form_factor_bat = form_ba[form_ba.striker.isin(batting_order)].set_index('striker')['form'].to_dict()
            form_factor_bowl = form_bo[form_bo.bowler.isin(bowling_order)].set_index('bowler')['form'].to_dict()

            dismissed_batters = set()  # Set of batters who have already been dismissed

            # Function to retrieve the next batter
            batting_order_iterator = iter(batting_order)  # Iterator over batting order

            # Initialize the first two batters as striker and non-striker
            striker = next(batting_order_iterator)
            non_striker = next(batting_order_iterator)


            class BattingOrder:
                def __init__(self, batting_order):
                    self.batting_order_iterator = iter(batting_order)
                    self.dismissed_batters = set()

                def next_batsman(self):
                    try:
                        next_batter = next(self.batting_order_iterator)
                        while next_batter in self.dismissed_batters:
                            next_batter = next(self.batting_order_iterator)
                    except StopIteration:
                        next_batter = None
                    return next_batter

            
            # Filter out bowlers and create a list of bowlers with their priorities
            bowlers_df = bowling_team.dropna(subset=['bowl']).reset_index(drop=True)
            bowlers_df['bowl'] = bowlers_df['bowl'].astype(int)  # Ensure 'bowl' column is integer type

            # Initialize tracking for overs bowled and the last over bowled by each bowler
            overs_bowled = {row['Func_Name']: 0 for _, row in bowlers_df.iterrows()}
            last_over_bowled = {row['Func_Name']: -2 for _, row in bowlers_df.iterrows()}  # Start with -2 for all bowlers
            wickets_taken = {row['Func_Name']: 0 for _,row in bowlers_df.iterrows()}
            runs_conceeded_over = {row['Func_Name']: 0 for _,row in bowlers_df.iterrows()}

            ##
            ##
            ##

            # Function to calculate probabilities based on bowler priority and conditions
            def calculate_bowler_probabilities(bowlers_df, overs_bowled, last_over_bowled, over, wickets_taken,runs_conceeded_over):
                probabilities = []

                for _, row in bowlers_df.iterrows():
                    name = row['Func_Name']
                    rank = row['bowl']

                    # Initialize base probability by bowler rank
                    prob = 0.8 if rank <= 5 else 0.05

                    # Add preference for higher-priority bowlers in initial overs
                    ####
                    if over <= 3 and rank <= 2:
                        prob += 10
                        
                    if over <= 3 and rank > 3:
                        prob *= 0.1
                        
                    if rank <= 2 and over >3 and over <= 6:
                        prob *= 0.2

                    # Add less-preference for higher-priority bowlers in middle overs, to preserve their overs by end
                    ####
                    if over >= 6 and over<15 and rank <= 2:
                        prob *= 0.05
                        
                    ####   
                    

                    # Add preference for higher-priority bowlers in final overs
                    if rank <= 3 and over >= 15 and overs_bowled[name] < 4:
                        prob *= 1.25 #min(1.25, -0.2+1/prob)

                    # reducing >3 rank bowlers' prob after over 15
                    if rank > 3 and over >= 15:
                        prob *= 0.01

                    if (over >= 6) and ((wickets_taken[name] >=1) or (runs_conceeded_over[name]/(overs_bowled[name] if overs_bowled[name]>=1 else 1) <=9)) :#and last_over_bowled[name] == over - 2:
                        prob *= 3 #min(1.4, -0.05+1/prob)

                    # reduce prob if leaking runs
                    if ((runs_conceeded_over[name]/(overs_bowled[name] if overs_bowled[name]>=1 else 1) >=11)) and rank<=5 :
                        prob *= 0.05

                    # Slightly increase probability if bowler rested last over (bowled two overs ago)
                    ####
                    """
                    if last_over_bowled[name] <= over - 3:
                        prob *= min(1.15, -0.2+1/prob)
                    """
                    # Reduce probability for lower-priority bowlers who have already bowled 2 or more overs
                    if overs_bowled[name] >= 3 and rank >= 5:
                        prob *= 0.2 #min(0.2, -0.2+1/prob)

                    """if last_over_bowled[name] == over - 1:
                        prob = 0  # Ensure no consecutive overs

                    if overs_bowled[name] == 4:
                        prob = 0  # Ensure not more than 4 overs"""
                    
                    prob = max(prob, 0.001)
                    ####  
                    # Add zero-preference for lower-priority bowlers in pp, death overs, to restrict their overs by middle
                    ####
                    if (over <= 6 or over>16) and rank > 5:
                        prob *= 0 #0.0005 

                    #modifying bowling choice for rank 6 or above
                    if (over <= 15 or over>=10) and rank >= 6:
                        prob *= 5 #0.0005 
                    if overs_bowled[name] >= 1 and rank >= 6:
                        prob *= 0.0000002

                    probabilities.append(prob)

                
                total_prob = sum(probabilities)
                return [p / total_prob for p in probabilities] if total_prob > 0 else [1/len(probabilities)] * len(probabilities)

            # Initialize counters and simulation settings
            legal_balls = 0
            legal_balls_last = 0
            all_balls = 0
            wickets_down = 0
            runs_conceeded_o = 0
            runs_over = 0
            last_3_ov_runs = 0
            last_3_ov_wkts = 0


            # Initialize bowler for the first over
            over = 1
            ####
            
            if fixed == True:
                bowler = bowlers_df.loc[bowlers_df['bowl'] == fixed_order[over-1], 'Func_Name'].values[0]
            else:
                #########NEW LOGIC HARDCODE##################
                if over == 1:
                    bowler = bowlers_df.loc[bowlers_df['bowl'] == 1, 'Func_Name'].values[0]
                elif over == 2:
                    bowler = bowlers_df.loc[bowlers_df['bowl'] == 2, 'Func_Name'].values[0]
                else:
                    bowler_probabilities = calculate_bowler_probabilities(bowlers_df, overs_bowled, last_over_bowled, over, wickets_taken, overs_bowled)
                    bowler = np.random.choice(bowlers_df['Func_Name'], p=bowler_probabilities)
                #########NEW LOGIC HARDCODE##################
            
            
            
            """
            bowler_probabilities = calculate_bowler_probabilities(bowlers_df, overs_bowled, last_over_bowled, over, wickets_taken,overs_bowled)
            
            bowler = np.random.choice(bowlers_df['Func_Name'], p=bowler_probabilities)
            """
            
            
            for over in range(1, 21):
                ##
                if over==1:
                    try:
                        bowler_ssn_stat = bowl_stat[bowl_stat.bowler==bowler][['num_innings','wkts','economy']].values.tolist()[0]
                        bowler_form_stat = form_ball[form_ball.bowler==bowler][['num_innings','wkts','bowl_eco']].values.tolist()[0]
                    except:
                        bowler_ssn_stat = [0,0, 'not played']
                        bowler_form_stat = [0,0, 'not played']
                    print(f"Opening bowler -> {bowler} \n SPL Career:: \n Innings = {int(bowler_ssn_stat[0])}, Wickets = {int(bowler_ssn_stat[1])}, Economy = {bowler_ssn_stat[2]}")
                    print(f"Form : \n (last {int(bowler_form_stat[0])} innings) \n Wickets = {int(bowler_form_stat[1])}, Economy = {bowler_form_stat[2]}")
                    print("^'^'^'"*4)
                    print(" "*10)
                    print('---' * 10)

                for ball in range(1, 10):  # Accounting for max 10 balls in case of extras in each over
                    if legal_balls == 120 or wickets_down==10:
                        break  # End loop when 120 legal balls are bowled (20 overs)
                    ####


                    h2h_bat = h2h[(h2h.striker==striker)&(h2h.bowler==bowler)].h2h_factor_bat.values
                    h2h_bowl = h2h[(h2h.striker==striker)&(h2h.bowler==bowler)].h2h_factor_bowl.values

                    spin_bat = spin[(spin.striker==striker)].spin_index.values
                    pace_bat = pace[(pace.striker==striker)].pace_index.values

                    current_ball = (over - 1) * 6 + ball  # Track overall ball count
                    all_balls += 1

                    # Determine phase of play: Powerplay, Middle, Death
                    phase = 'pp' if over <= 6 else 'middle' if over <= 15 else 'death'

                    # Retrieve probabilities based on the current ground, batter, and bowler stats
                    ground_probs = df_g[(df_g.venue == match_context['venue']) & 
                                        (df_g.innings == match_context['innings']) & 
                                        (df_g.phase == phase)].iloc[0]

                    filtered_batter_probs = df_ba[(df_ba.striker == striker) & 
                                          (df_ba.innings == match_context['innings']) & 
                                          (df_ba.phase == phase)]

                    if not filtered_batter_probs.empty:
                        batter_probs = filtered_batter_probs.iloc[0]
                    else:
                        batter_probs = pd.Series({col: np.abs(np.random.normal(0.17, 0.15)) for col in df_ba.columns})   #Default values for all columns

                    # Bowler probabilities
                    filtered_bowler_probs = df_bo[(df_bo.bowler == bowler) & 
                                                  (df_bo.innings == match_context['innings']) & 
                                                  (df_bo.phase == phase)]

                    if not filtered_bowler_probs.empty:
                        bowler_probs = filtered_bowler_probs.iloc[0]
                    else:
                        #bowler_probs = pd.Series({col: np.abs(np.random.normal(0.17, 0.15)) for col in df_bo.columns}) #make adjustments here
                        bowler_probs = pd.Series({'wkt_prob': 0.07, 'one_prob': 0.33, 'two_prob': 0.05, 'three_prob': 0.002, 'four_prob': 0.09,
                            'six_prob': 0.055, 'dot_prob': 0.33, 'wide_prob': 0.035, 'no_prob': 0.004, 'bowler': 0, 'phase': 0,
                            'innings': 0, 'num_innings': 0, 'runs': 0, 'balls': 0, 'wkts': 0, 'economy': 0,
                            'strike_rate': 0, 'nrr_phase': 0, 'wkt_phase': 0})


                    ###checking bowler-type, and assigning ground-condition factor
                    bowl_type = player_list[player_list.Func_Name==bowler]['Spin/Pace'].unique()[0]
                    g_factor = ground_factor**(1/6)
                    
                    if bowl_type=='Pace':
                        bowl_type_factor = pace_bat
                    elif bowl_type=='Spin':
                        bowl_type_factor = spin_bat

                    if bowl_type=='Pace':
                        g_factor = 1/g_factor
                        
                    ###################################   
                        
                    overall_factor = 5
                    run_factor = (3 if (wickets_down<4 & over >12) else 5 if over>15 else 1)
                    death_factor = (1.8 if over>=16 else 1)##*******
                    bdry_factor = (1 if over<=6 else 0.8 if (over>6 & over<15) else 2 if (wickets_down<7 & over>15) else 1.5)
                    dot_factor = (1.25 if over<=6 else 0.8 if wickets_down<4 else 1)
                    wkt_factor = (0.75 if over<=15 else 1.05)
                    l_o_bdry_factor = (0.8 if wickets_down>=7 else 1)
                    l_o_dot_factor = (1.2 if wickets_down>=7 else 1)
                    l_o_out_factor = (1.2 if wickets_down>=8 else 1)
                    middle_factor = (0.9 if (over>6 & over<=15) else 1)

                    last_3_ov_factor = (1.15 if (last_3_ov_runs<=27 and last_3_ov_wkts<=1) else 0.75 if (last_3_ov_wkts>=2) else 1)


                    free_hit_factor = 1
                    if ball>=2:
                        free_hit_factor = (0 if event=='noball' else 1)
                    free_hit_factor_bdry = 1
                    if ball>=2:
                        free_hit_factor_bdry = (3 if event=='noball' else 1)
                    
                    st_ro_factor = (2 if over>=16 else 1)
                    #rpo based
                    rpo_factor = (11/rpo if over >=2 else 1)
                    sd = 0.015 #0.15

                    # Adjust probabilities using form and H2H factors
                    final_probs = {
                        'one': max(0.01, np.random.normal(0, sd) + (ground_probs['one_prob'] + batter_probs['one_prob'] + bowler_probs['one_prob']) * (form_factor_bat.get(striker, 1)*np.random.normal(1,0.1)) / 3) * rpo_factor*middle_factor,
                        'two': max(0.01,np.random.normal(0, sd) + (ground_probs['two_prob'] + batter_probs['two_prob'] + bowler_probs['two_prob']) * (form_factor_bat.get(striker, 1)*np.random.normal(1,0.1)) / 3) * rpo_factor*middle_factor,
                        'three': max(0.01,np.random.normal(0,sd) + (ground_probs['three_prob'] + batter_probs['three_prob'] + bowler_probs['three_prob']) * (form_factor_bat.get(striker, 1)*np.random.normal(1,0.1)) / 3),
                        'four': max(0.01,np.random.normal(0, sd) + (ground_probs['four_prob'] + batter_probs['four_prob'] + bowler_probs['four_prob']) * (form_factor_bat.get(striker, 1)*np.random.normal(1,0.1))/ 3) * rpo_factor * death_factor*bdry_factor*l_o_bdry_factor*middle_factor*free_hit_factor_bdry,
                        'six': max(0.01,np.random.normal(0, sd) + (ground_probs['six_prob'] + batter_probs['six_prob'] + bowler_probs['six_prob']) * (form_factor_bat.get(striker, 1)*np.random.normal(1,0.1)) / 3) * rpo_factor * death_factor*bdry_factor*l_o_bdry_factor*middle_factor*free_hit_factor_bdry,
                        'dot': max(0.01,np.random.normal(0,0.03) + (ground_probs['dot_prob'] + batter_probs['dot_prob'] + bowler_probs['dot_prob']) * (1 / (form_factor_bat.get(striker, 1)*np.random.normal(1,0.1))) / 3) * g_factor*dot_factor*l_o_dot_factor * (1/death_factor) * (1/last_3_ov_factor) * (1/bowl_type_factor[0] if len(bowl_type_factor)>0 else 1),
                        'wicket': max(0.01,np.random.normal(0, 0.045) + (ground_probs['wkt_prob'] + batter_probs['out_prob'] + bowler_probs['wkt_prob']) * (form_factor_bowl.get(bowler, 1)*np.random.normal(1,0.1)) * (h2h_bowl[0] if len(h2h_bowl)>0 else 1) / 3) * wkt_factor * free_hit_factor*l_o_out_factor * g_factor * (1/bowl_type_factor[0] if len(bowl_type_factor)>0 else 1),
                        '0+runout': (0.003)/3,
                        '1+runout': (0.0025)/3,
                        '2+runout': (0.002)/3,
                        '3+runout': 0.0002,
                        'wide': max(0.01,np.random.normal(0, 0.02) + ground_probs['wide_prob']),
                        'noball': ground_probs.get('no_prob', 0.01),
                        'bye': ground_probs.get('bye_prob', 0.01),
                        'legbye': ground_probs.get('legbye_prob', 0.01)
                    }

                    # Normalize probabilities so they sum up to 1
                    total = sum(final_probs.values())
                    final_probs = {k: v / total for k, v in final_probs.items()}

                    # Simulate outcome of the ball
                    event = np.random.choice(list(final_probs.keys()), p=np.ravel(list(final_probs.values())))

                    # Update legal ball count for valid deliveries
                    legal_balls += 1 if event not in ['wide', 'noball'] else 0
                    wickets_down += 1 if event in ['wicket', '0+runout','1+runout','2+runout','3+runout'] else 0

                    wkt_type = ''
                    fielder= ''
                    if event == 'wicket':
                        wkt_type = random.choices(['Caught', 'Bowled', 'Stumped/Runout by Keeper', 'HitWicket'], weights=[0.7, 0.28, 0.01, 0.01])[0]
                        #row.update({'wicket_event': wkt_type})
                        if wkt_type == 'Caught':
                            weights = [0.075] * 10 + [0.25]
                            # Randomly choose a fielder based on weights
                            fielder = random.choices(total_list, weights=weights)[0]
                        elif wkt_type == 'Stumped/Runout by Keeper':
                            fielder = total_list[-1]
                    elif event in ['0+runout','1+runout','2+runout','3+runout']:
                        weights = [0.0975] * 10 + [0.025]
                        # Randomly choose a fielder based on weights
                        fielder = random.choices(total_list, weights=weights)[0]
                                
                    # Capture details of this ball
                    row = match_context.copy()
                    row.update({
                        'innings': match_context['innings'],
                        'ball': all_balls, 
                        'striker': striker,
                        'non_striker': non_striker,
                        'bowler': bowler,
                        'runs_off_bat': 1 if event in ['one','1+runout'] else 2 if event in ['2+runout','two'] else 3 if event in ['3+runout','three'] else 4 if event == 'four' else 6 if event == 'six' else 0,
                        'extras': 1 if event in ['wide', 'noball', 'bye', 'legbye'] else 0,
                        'wides': 1 if event == 'wide' else 0,
                        'noballs': 1 if event == 'noball' else 0,
                        'byes': 1 if event == 'bye' else 0,
                        'legbyes': 1 if event == 'legbye' else 0,
                        'wicket_type': 'out' if event == 'wicket' else 'runout' if event in ['0+runout','1+runout','2+runout','3+runout'] else None,
                        'player_dismissed': striker if event in ['wicket','0+runout','2+runout'] else non_striker if event in ['1+runout','3+runout'] else None,
                        'legal_balls_bowled': legal_balls,
                        'wicket_event' : wkt_type,
                        'fielder': fielder
                    })

                    # Append data for each ball to simulation DataFrame
                    df_simulation = pd.concat([df_simulation, pd.DataFrame([row])], ignore_index=True)
                    

                    print(f"{bowler} to {striker} : {event}")
                    if event == 'noball':
                        print("**FREE HIT!!**")

                    

                    
                    #striker, non_striker = handle_event(event, df_simulation, striker, non_striker)

                    # Switch batters on odd runs or for a wicket
                    if event in ['wicket','0+runout','2+runout']:
                        striker_runs = df_simulation[df_simulation.striker==striker].runs_off_bat.sum()
                        print("**WICKET!!**")
                        if event == 'wicket':
                            if wkt_type == 'Caught':
                                print(f"Caught by {fielder}!")
                            elif wkt_type == 'Stumped/Runout by Keeper':
                                print(f"{wkt_type}!")
                            else:
                                print(f"{wkt_type}!!")
                        else:
                            print(f"Runout by {fielder}!")
                        

                        print(f"batter out: {striker}, for {striker_runs}")
                        striker = next_batsman() #############
                        print("<><>"*7)
                        try:
                            new_batter_ssn_stat = bat_stat[bat_stat.striker==striker][['num_innings','runs','SR','Bat_avg']].values.tolist()[0]
                            new_batter_form_stat = form_bat[form_bat.striker==striker][['num_innings','runs','bat_sr','bat_avg']].values.tolist()[0]
                        except:
                            new_batter_ssn_stat = [0,0, 'not played','not played']
                            new_batter_form_stat = [0, 0, 'not played','not played']
                        if wickets_down<10:
                            print(f"NEW Batter in: {striker} \n SPL Career:: \n Innings = {int(new_batter_ssn_stat[0])}, Runs = {int(new_batter_ssn_stat[1])}, SR = {new_batter_ssn_stat[2]}, Avg = {new_batter_ssn_stat[3]}")
                            print(" "*10)
                            print(f"Recent Form :: \n (last {int(new_batter_form_stat[0])} innings) Runs = {int(new_batter_form_stat[1])}, SR = {new_batter_form_stat[2]}, Avg = {new_batter_form_stat[3]}")
                            print(" "*10)
                            print('---' * 10)
                        print("<><>"*7)
                        fow = df_simulation.runs_off_bat.sum()+df_simulation.extras.sum()
                        fow_balls = str(legal_balls//6)+'.'+str(legal_balls%6)
                        ##INSERT SEASON STATS HERE
                    elif event in ['1+runout','3+runout']:
                        non_striker_runs = df_simulation[df_simulation.striker==non_striker].runs_off_bat.sum()
                        print("**WICKET!!**")
                        print(f"Runout by {fielder}!")
                        #row.update({'fielder': ro_by})
                        print(f"batter out: {non_striker}, for {non_striker_runs}")
                        non_striker = next_batsman()
                        print("<><>"*7)
                        try:
                            new_batter_ssn_stat = bat_stat[bat_stat.striker==non_striker][['num_innings','runs','SR','Bat_avg']].values.tolist()[0]
                            new_batter_form_stat = form_bat[form_bat.striker==non_striker][['num_innings','runs','bat_sr','bat_avg']].values.tolist()[0]
                        except:
                            new_batter_ssn_stat = [0,0, 'not played','not played']
                            new_batter_form_stat = [0, 0, 'not played','not played']
                        if wickets_down<10:
                            print(f"NEW Batter in: {non_striker} \n SPL Career:: \n Innings = {int(new_batter_ssn_stat[0])}, Runs = {int(new_batter_ssn_stat[1])}, SR = {new_batter_ssn_stat[2]}, Avg = {new_batter_ssn_stat[3]}")
                            print(" "*10)
                            print(f"Recent Form :: \n (last {int(new_batter_form_stat[0])} innings) Runs = {int(new_batter_form_stat[1])}, SR = {new_batter_form_stat[2]}, Avg = {new_batter_form_stat[3]}")
                            print(" "*10)
                        print("<><>"*7)
                        fow = df_simulation.runs_off_bat.sum()+df_simulation.extras.sum()
                        fow_balls = str(legal_balls//6)+'.'+str(legal_balls%6)
                    elif event in ['one', 'three','bye','legbye']:
                        striker, non_striker = non_striker, striker  # Swap striker and non-striker


                    if legal_balls in [38, 55, 87]:
                        #print('  '*10)
                        try:
                            h2h__ = h2h_[(h2h_['striker']==striker)&(h2h_['bowler']==bowler)][['runs_scored','balls_faced','outs']].values.tolist()[0]
                        except:
                            h2h__ = ['not played','not played','not played']
                        if h2h__[1] != 'not played':
                            print('  '*10)
                            print(f"Random Statbite :- \n {striker} vs {bowler} --> runs = {int(h2h__[0])}, balls = {int(h2h__[1])}, dismissals = {int(h2h__[2])} (before this game)")
                            print('---'*10)
                        else:
                            print('  '*10)
                            print(f"Random Statbite :- \n {striker} hasn't faced {bowler} before!!")
                            print('---'*10)


                    if legal_balls in [46, 62, 71]:
                        #print('  '*10)
                        if bowl_type=='Pace':
                            try:
                                pace_score = pace_stat[pace_stat['striker']==striker][['SR','Bat_avg','bpb']].values.tolist()[0]
                            except:
                                pace_score = ['not played','not played','not played']
                            if pace_score[1] != 'not played':
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} vs {bowl_type} --> SR = {int(pace_score[0])}, Avg = {int(pace_score[1])}, BpB = {(pace_score[2])} (before this game)")
                                print('---'*10)
                            else:
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} hasn't faced {bowl_type} bowling before!!")
                                print('---'*10)
                        elif bowl_type=='Spin':
                            try:
                                spin_score = spin_stat[spin_stat['striker']==striker][['SR','Bat_avg','bpb']].values.tolist()[0]
                            except:
                                spin_score = ['not played','not played','not played']
                            if spin_score[1] != 'not played':
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} vs {bowl_type} --> SR = {int(spin_score[0])}, Avg = {int(spin_score[1])}, BpB = {(spin_score[2])} (before this game)")
                                print('---'*10)
                            else:
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} hasn't faced {bowl_type} bowling before!!")
                                print('---'*10)

                        #print('---'*10)


                    if event in ['bye','legbye']:
                        runs_conceeded_o += row['runs_off_bat']
                    else:
                        runs_conceeded_o += row['runs_off_bat']+row['extras']

                    runs_over += row['runs_off_bat']+row['extras']

                    if event == 'wicket':

                        wickets_taken[bowler] += 1
                    # Change bowler every 6 legal balls (end of an over)
                    if (legal_balls % 6 == 0)&(legal_balls!=legal_balls_last):
                        
                        striker, non_striker = non_striker, striker #over ends
                        overs_bowled[bowler] += 1
                        runs_conceeded_over[bowler] += runs_conceeded_o
                        ###
                        last_over_bowled[bowler] = over  # Update last over bowled for current bowler
                        
                        ##CHANGE THE LOGIC, DROP THE INDEX OF THE BOWLER BOWLING THE LAST OVER
                        ######removing the latest bowler from the calc
                        """overs_bowled.pop(bowler, None)
                        last_over_bowled.pop(bowler, None)
                        wickets_taken.pop(bowler, None)
                        runs_conceeded_over.pop(bowler, None)"""
                        ##############
                        if overs_bowled[bowler] == 4:
                            bowlers_df = bowlers_df[bowlers_df['Func_Name']!=bowler]
                        
                        if fixed == False:
                            if over+1 == 2:
                                bowler = bowlers_df.loc[bowlers_df['bowl'] == 2, 'Func_Name'].values[0]
                            else:
                                bowler_probabilities = calculate_bowler_probabilities(bowlers_df[bowlers_df['Func_Name']!=bowler], overs_bowled, last_over_bowled, over+1, wickets_taken, overs_bowled)
                                bowler = np.random.choice(bowlers_df[bowlers_df['Func_Name']!=bowler]['Func_Name'], p=bowler_probabilities)
                        #print(over,bowler)
                        a = a+3
                        score = df_simulation['runs_off_bat'].sum()+df_simulation['extras'].sum()
                        rpo = score/(legal_balls//6)
                        last_3_ov_runs = df_simulation[(df_simulation['legal_balls_bowled']>max(0,legal_balls-18))]['runs_off_bat'].sum()
                        last_3_ov_wkts = df_simulation[(df_simulation['legal_balls_bowled']>max(0,legal_balls-18))]['wicket_type'].count()

                        print(' '*10)
                        #print("---****________****", last_3_ov_runs, last_3_ov_wkts)

                        print(f"runs in this over : {runs_over}")
                        print(' '*10)
                        print(f"end of over {legal_balls//6}; score :: **{score}** for **{wickets_down}**")
                        over = min(20, legal_balls//6 + 1) #over updation
                        if fixed == True :
                            if legal_balls//6<20:
                                bowler = bowlers_df.loc[bowlers_df['bowl'] == fixed_order[over-1], 'Func_Name'].values[0]
                            #print(over,bowler)
                        #print(over, "th OVER starts next")
                        print(f"last fall-of-wicket : {fow}-{wickets_down} ({fow_balls})")
                        print(' '*10)
                        #print(f"current partnership : {int(score)-int(fow)} ({int(legal_balls)-int(fow_balls)} legal balls)")
                        print('---'*10)

                        if (legal_balls//6)==3: #3rd over done
                            try:
                                striker_phase = bat_phase[(bat_phase['striker']==striker)&(bat_phase['phase']=='pp')][['runs','strike_rate']].values.tolist()[0]
                            except:
                                striker_phase = [0, 'not played']
                            if striker_phase[1] != 'not played':
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} in PowerPlay (before this game) - runs = {int(striker_phase[0])}, SR = {striker_phase[1]}")
                                print('---'*10)
                            else:
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} batting in PowerPlay for the first time!!")
                                print('---'*10)

                        if (legal_balls//6)==10: #10th over done
                            try:
                                striker_phase = bat_phase[(bat_phase['striker']==striker)&(bat_phase['phase']=='middle')][['runs','strike_rate']].values.tolist()[0]
                            except:
                                striker_phase = [0, 'not played']
                            if striker_phase[1] != 'not played':
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} in Middle-Overs (before this game) - runs = {int(striker_phase[0])}, SR = {striker_phase[1]}")
                                print('---'*10)
                            else:
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} batting in Middle-Overs for the first time!!")
                                print('---'*10)

                        if (legal_balls//6)==16: #16th over done
                            try:
                                striker_phase = bat_phase[(bat_phase['striker']==striker)&(bat_phase['phase']=='death')][['runs','strike_rate']].values.tolist()[0]
                            except:
                                striker_phase = [0, 'not played']
                            if striker_phase[1] != 'not played':
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} in Death-Overs (before this game) - runs = {int(striker_phase[0])}, SR = {striker_phase[1]}")
                                print('---'*10)
                            else:
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} batting in Death-Overs for the first time!!")
                                print('---'*10)
                        
                        

                        print('-.-.-.'*10)
                        print(' '*10)
                        if overs_bowled[bowler] == 0 and (legal_balls//6)<20:
                            try:
                                new_bowler_ssn_stat = bowl_stat[bowl_stat.bowler==bowler][['num_innings','wkts','economy']].values.tolist()[0]
                                new_bowler_form_stat = form_ball[form_ball.bowler==bowler][['num_innings','wkts','bowl_eco']].values.tolist()[0]
                            except:
                                new_bowler_ssn_stat = [0,0, 'not played']
                                new_bowler_form_stat = [0,0, 'not played']
                            print(f"NEW bowler -> {bowler} \n SPL Career:: \n Innings = {int(new_bowler_ssn_stat[0])}, Wickets = {int(new_bowler_ssn_stat[1])}, Economy = {new_bowler_ssn_stat[2]}")
                            print(f"Form : (last {int(new_bowler_form_stat[0])} innnigs) \n  Wickets = {int(new_bowler_form_stat[1])}, Economy = {new_bowler_form_stat[2]}")

                            print('---' * 10)
                        if (legal_balls//6)==2: #2nd over done
                            try:
                                bowler_phase = bowl_phase[(bowl_phase['bowler']==bowler)&(bowl_phase['phase']=='pp')][['balls','economy']].values.tolist()[0]
                            except:
                                bowler_phase = [0, 'not played']
                            if bowler_phase[1] != 'not played':
                                print('  '*10)
                                print(f"Random Statbite :- \n {bowler} in PowerPlay (before this game) - balls = {int(bowler_phase[0])}, Eco = {bowler_phase[1]}")
                                print('---'*10)
                            else:
                                print('  '*10)
                                print(f"Random Statbite :- \n {bowler} bowling in PowerPlay for the first time!!")
                                print('---'*10)

                        if (legal_balls//6)==12: #12th over done
                            try:
                                bowler_phase = bowl_phase[(bowl_phase['bowler']==bowler)&(bowl_phase['phase']=='middle')][['balls','economy']].values.tolist()[0]
                            except:
                                bowler_phase = [0, 'not played']
                            if bowler_phase[1] != 'not played':
                                print('  '*10)
                                print(f"Random Statbite :- \n {bowler} in Middle-Overs (before this game) - balls = {int(bowler_phase[0])}, Eco = {bowler_phase[1]}")
                                print('---'*10)
                            else:
                                print('  '*10)
                                print(f"Random Statbite :- \n {bowler} bowling in Middle-Overs for the first time!!")
                                print('---'*10)

                        if (legal_balls//6)==17: #17th over done
                            try:
                                bowler_phase = bowl_phase[(bowl_phase['bowler']==bowler)&(bowl_phase['phase']=='death')][['balls','economy']].values.tolist()[0]
                            except:
                                bowler_phase = [0, 'not played']
                            if bowler_phase[1] != 'not played':
                                print('  '*10)
                                print(f"Random Statbite :- \n {bowler} in Death-Overs (before this game) - balls = {int(bowler_phase[0])}, Eco = {bowler_phase[1]}")
                                print('---'*10)
                            else:
                                print('  '*10)
                                print(f"Random Statbite :- \n {bowler} bowling in Death-Overs for the first time!!")
                                print('---'*10)

                        print(' '*10)
                        runs_conceeded_o = 0
                        runs_over = 0
                    legal_balls_last += 1 if event not in ['wide', 'noball'] else 0

            print(' '*10)
            print('---'*10)    
            print(' '*10)

            df_mod = func_1(df_simulation)

            df_mod_1 = func_2(df_mod)

            bat_1st = (other_team if decision=='Bowl' else toss_win_team)
            bowl_1st = (toss_win_team if decision=='Bowl' else other_team)

            df_mod_1['batting_team'] = bat_1st
            df_mod_1['bowling_team'] = bowl_1st

            columns = ['innings','striker','non_striker','bowler','runs_off_bat','extras','wicket_type','player_dismissed',
                      'legal_balls_bowled','runs_scored','bowler_wicket','run_rate','last_fow','reqd_run_rate']
            #df_mod_1#[columns]

            print(f"total: {df_mod_1['runs_scored'].max()}, wickets: {df_mod_1['wickets_down'].max()}")

            print("**"*40)
            print("INNING 1 IS OVER!!")
            print("**"*40)

            print("the chase is underway!!!!!!!!!!!!")
            print("**"*40)

            print(' '*10)
            print('---'*10)    
            print(' '*10)

            ## inning 2
            ##XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


            ##XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


            ##XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX



            # Setup initial game context
            match_context = {
                'match_id': m_id,
                'season': 2,
                'start_date': current_date,
                'venue': ground,  # Ground name as provided
                'innings': 2,
                'ball': 1,

            }
            fixed = False
            # Placeholder for output DataFrame
            columns = ['match_id', 'season', 'start_date', 'venue', 'innings', 'ball',
                       'batting_team', 'bowling_team', 'striker', 'non_striker', 'bowler',
                       'runs_off_bat', 'extras', 'wides', 'noballs', 'byes', 'legbyes',
                       'wicket_type', 'player_dismissed','legal_balls_bowled']

            df_simulation_2 = pd.DataFrame(columns=columns)

            fow = 0
            fow_balls = 0

            ##
            batting_team, bowling_team = bowling_team, batting_team
            ##

            batting_order = batting_team.Func_Name.values
            bowling_order = bowling_team[~(bowling_team.bowl.isna())].Func_Name.values
            if len(bowling_order)==5:
                fixed = True
                # Main loop
                while True:
                    sequence = generate_sequence()
                    if not has_consecutive_duplicates(sequence):
                        break
                fixed_order = sequence

            fielder_list = bowling_team[~(bowling_team['wk']==1)].Func_Name.values.tolist()
            #print(fielder_list)
            wk = bowling_team[bowling_team['wk']==1].Func_Name.unique()[0]
            #print(wk)
            total_list = fielder_list + [wk]
            #print("fielder LIST -- ", total_list)

            # Initial striker, non-striker, and bowler
            striker = batting_order[0]
            non_striker = batting_order[1]
            try:
                striker_ssn_stat = bat_stat[bat_stat.striker==striker][['num_innings','runs','SR','Bat_avg']].values.tolist()[0]
                striker_form_stat = form_bat[form_bat.striker==striker][['num_innings','runs','bat_sr','bat_avg']].values.tolist()[0]
            except:
                striker_ssn_stat = [0,0, 'not played', 'not played']
                striker_form_stat = [0, 0, 'not played', 'not played']
            try:
                non_striker_ssn_stat = bat_stat[bat_stat.striker==non_striker][['num_innings','runs','SR','Bat_avg']].values.tolist()[0]
                non_striker_form_stat = form_bat[form_bat.striker==non_striker][['num_innings','runs','bat_sr','bat_avg']].values.tolist()[0]
            except:
                non_striker_ssn_stat = [0,0, 'not played', 'not played']
                non_striker_form_stat = [0, 0, 'not played', 'not played']

            print("^'^'^'"*4)
            print(" "*10)
            print("Openers :-")
            print(" "*10)
            print(f"Striker -> {striker} \n SPL Career:: \n Innings = {int(striker_ssn_stat[0])}, Runs = {int(striker_ssn_stat[1])}, SR = {striker_ssn_stat[2]}, Avg = {striker_ssn_stat[3]}")
            print(" "*10)
            print(f"Recent Form:: \n (last {int(striker_form_stat[0])} Innings) Runs = {int(striker_form_stat[1])}, SR = {striker_form_stat[2]}, Avg = {striker_form_stat[3]}")
            print(" "*10)
            print(f"Non-Striker -> {non_striker} \n SPL Career:: \n Innings = {int(non_striker_ssn_stat[0])}, Runs = {int(non_striker_ssn_stat[1])}, SR = {non_striker_ssn_stat[2]}, Avg = {non_striker_ssn_stat[3]}")
            print(" "*10)
            print(f"Recent Form:: \n (last {int(non_striker_form_stat[0])} Innings) Runs = {int(non_striker_form_stat[1])}, SR = {non_striker_form_stat[2]}, Avg = {non_striker_form_stat[3]}")
            print(" "*10)
            print("^'^'^'"*4)
            print(" "*10)

            form_factor_bat = form_ba[form_ba.striker.isin(batting_order)].set_index('striker')['form'].to_dict()
            form_factor_bowl = form_bo[form_bo.bowler.isin(bowling_order)].set_index('bowler')['form'].to_dict()


            #h2h_bat = h2h[(h2h.striker==striker)&(h2h.bowler==bowler)].h2h_factor_bat.values
            #h2h_bowl = h2h[(h2h.striker==striker)&(h2h.bowler==bowler)].h2h_factor_bowl.values

            dismissed_batters = set()  # Set of batters who have already been dismissed

            # Function to retrieve the next batter
            batting_order_iterator = iter(batting_order)  # Iterator over batting order

            # Initialize the first two batters as striker and non-striker
            striker = next(batting_order_iterator)
            non_striker = next(batting_order_iterator)

            def next_batsman():
                """Fetch the next available batter from the batting order."""
                global batting_order_iterator  # Use the global iterator to keep the sequence

                try:
                    next_batter = next(batting_order_iterator)
                    while next_batter in dismissed_batters:
                        next_batter = next(batting_order_iterator)  # Skip dismissed batters
                except StopIteration:
                    next_batter = None  # No more batters available (all-out scenario)

                return next_batter

            # Filter out bowlers and create a list of bowlers with their priorities
            bowlers_df = bowling_team.dropna(subset=['bowl']).reset_index(drop=True)
            bowlers_df['bowl'] = bowlers_df['bowl'].astype(int)  # Ensure 'bowl' column is integer type

            # Initialize tracking for overs bowled and the last over bowled by each bowler
            overs_bowled = {row['Func_Name']: 0 for _, row in bowlers_df.iterrows()}
            last_over_bowled = {row['Func_Name']: -2 for _, row in bowlers_df.iterrows()}  # Start with -2 for all bowlers
            wickets_taken = {row['Func_Name']: 0 for _,row in bowlers_df.iterrows()}
            runs_conceeded_over = {row['Func_Name']: 0 for _,row in bowlers_df.iterrows()}


            legal_balls = 0
            legal_balls_last = 0
            all_balls = 0
            wickets_down = 0
            runs_scored = 0
            runs_conceeded_o = 0
            runs_over = 0
            last_3_ov_runs = 0
            last_3_ov_wkts = 0


            target = df_simulation['runs_off_bat'].sum()+df_simulation['extras'].sum()+1
            reqd_run_rate = 6*target/120


            # Initialize bowler for the first over
            over = 1

            if fixed == True:
                bowler = bowlers_df.loc[bowlers_df['bowl'] == fixed_order[over-1], 'Func_Name'].values[0]
            else:
                #########NEW LOGIC HARDCODE##################
                if over == 1:
                    bowler = bowlers_df.loc[bowlers_df['bowl'] == 1, 'Func_Name'].values[0]
                elif over == 2:
                    bowler = bowlers_df.loc[bowlers_df['bowl'] == 2, 'Func_Name'].values[0]
                else:
                    bowler_probabilities = calculate_bowler_probabilities(bowlers_df, overs_bowled, last_over_bowled, over, wickets_taken, overs_bowled)
                    bowler = np.random.choice(bowlers_df['Func_Name'], p=bowler_probabilities)
                #########NEW LOGIC HARDCODE##################

            for over in range(1, 21):
                #print(f"start of over {over}, last fall_of_wicket : ")
                if over==1:
                    try:
                        bowler_ssn_stat = bowl_stat[bowl_stat.bowler==bowler][['num_innings','wkts','economy']].values.tolist()[0]
                        bowler_form_stat = form_ball[form_ball.bowler==bowler][['num_innings','wkts','bowl_eco']].values.tolist()[0]
                    except:
                        bowler_ssn_stat = [0, 0, 'not played']
                        bowler_form_stat = [0,0, 'not played']
                    print(f"Opening bowler -> {bowler} \n SPL Career:: \n Innings = {int(bowler_ssn_stat[0])}, Wickets = {int(bowler_ssn_stat[1])}, Economy = {bowler_ssn_stat[2]}")
                    print(f"Form : \n (last {int(bowler_form_stat[0])} innings) \n Wickets = {int(bowler_form_stat[1])}, Economy = {bowler_form_stat[2]}")
                    print("^'^'^'"*4)
                    print(" "*10)
                for ball in range(1, 10):  # Accounting for max 10 balls in case of extras in each over

                    legal_balls_remaining = 120 - legal_balls

                    #runs_remaining = target - runs_scored

                    if (legal_balls == 120) or (wickets_down==10) or (runs_scored>=target):
                        break  

                    h2h_bat = h2h[(h2h.striker==striker)&(h2h.bowler==bowler)].h2h_factor_bat.values
                    h2h_bowl = h2h[(h2h.striker==striker)&(h2h.bowler==bowler)].h2h_factor_bowl.values

                    spin_bat = spin[(spin.striker==striker)].spin_index.values
                    pace_bat = pace[(pace.striker==striker)].pace_index.values

                    current_ball = (over - 1) * 6 + ball  # Track overall ball count
                    all_balls += 1

                    # Determine phase of play: Powerplay, Middle, Death
                    phase = 'pp' if over <= 6 else 'middle' if over <= 15 else 'death'

                    bowl_nrr_phase = 'easy' if reqd_run_rate >=10 else 'crucial' if reqd_run_rate<=8 else 'moderate'
                    bat_nrr_phase = 'crucial' if reqd_run_rate >=10 else 'easy' if reqd_run_rate<=8 else 'moderate'

                    bowl_wkt_phase = 'easy' if wickets_down >=7 else 'crucial' if wickets_down<=3 else 'medium'
                    bat_wkt_phase = 'tough' if wickets_down >=7 else 'easy' if wickets_down<=3 else 'medium'


                    # Retrieve probabilities based on the current ground, batter, and bowler stats
                    ground_probs = df_g[(df_g.venue == match_context['venue']) & 
                                        (df_g.innings == match_context['innings']) & 
                                        (df_g.phase == phase)].iloc[0]

                    filtered_batter_probs = df_ba[(df_ba.striker == striker) & 
                                          (df_ba.innings == match_context['innings']) & 
                                          (df_ba.phase == phase)&
                                          (df_ba.wkt_phase == bat_wkt_phase)&
                                          (df_ba.nrr_phase == bat_nrr_phase)]

                    if not filtered_batter_probs.empty:
                        batter_probs = filtered_batter_probs.iloc[0]
                    else:
                        batter_probs = pd.Series({col: np.abs(np.random.normal(0.17, 0.15)) for col in df_ba.columns})   #Default values for all columns

                    # Bowler probabilities
                    filtered_bowler_probs = df_bo[(df_bo.bowler == bowler) & 
                                                  (df_bo.innings == match_context['innings']) & 
                                                  (df_bo.phase == phase)&
                                                  (df_bo.wkt_phase == bowl_wkt_phase)&
                                                  (df_bo.nrr_phase == bowl_nrr_phase)]

                    if not filtered_bowler_probs.empty:
                        bowler_probs = filtered_bowler_probs.iloc[0]
                    else:
                        #bowler_probs = pd.Series({col: np.abs(np.random.normal(0.17, 0.15)) for col in df_bo.columns}) 
                        bowler_probs = pd.Series({'wkt_prob': 0.07, 'one_prob': 0.33, 'two_prob': 0.05, 'three_prob': 0.002, 'four_prob': 0.09,
                            'six_prob': 0.055, 'dot_prob': 0.33, 'wide_prob': 0.035, 'no_prob': 0.004, 'bowler': 0, 'phase': 0,
                            'innings': 0, 'num_innings': 0, 'runs': 0, 'balls': 0, 'wkts': 0, 'economy': 0,
                            'strike_rate': 0, 'nrr_phase': 0, 'wkt_phase': 0})
                        
                    ###checking bowler-type, and assigning ground-condition factor
                    bowl_type = player_list[player_list.Func_Name==bowler]['Spin/Pace'].unique()[0]
                    g_factor = ground_factor**(1/6)
                    
                    if bowl_type=='Pace':
                        bowl_type_factor = pace_bat
                    elif bowl_type=='Spin':
                        bowl_type_factor = spin_bat

                    if bowl_type=='Pace':
                        g_factor = 1/g_factor
                    ################################### 

                    overall_factor = 3.5
                    death_factor = (1.8 if over>=16 else 1)
                    #run_factor = (3 if (wickets_down<4 & over >12) else 5 if over>15 else 1)
                    run_factor = (3 if over>16 else 1)
                    bdry_factor = (1 if over<=6 else 0.8 if (over>6 & over<15) else 3 if (wickets_down<7 & over>15) else 1.5)
                    dot_factor = (1.25 if over<=6 else 0.8 if wickets_down<4 else 1)
                    wkt_factor = (0.75 if over<=15 else 1.05)
                    l_o_bdry_factor = (0.8 if wickets_down>=7 else 1)
                    l_o_dot_factor = (1.2 if wickets_down>=7 else 1)
                    l_o_out_factor = (1.2 if wickets_down>=8 else 1)
                    middle_factor = (0.9 if (over>6 & over<=15) else 1)

                    last_3_ov_factor = (1.15 if (last_3_ov_runs<=27 and last_3_ov_wkts<=1) else 0.75 if (last_3_ov_wkts>=2) else 1)


                    free_hit_factor = 1
                    if ball>=2:
                        free_hit_factor = (0 if event=='noball' else 1)
                    free_hit_factor_bdry = 1
                    if ball>=2:
                        free_hit_factor_bdry = (3 if event=='noball' else 1)
                    st_ro_factor = (2 if over>=16 else 1)
                    rr_factor = 1.25#(0.75 if reqd_run_rate<=8 else 1.33 if reqd_run_rate>12 else 1)
                    sd = 0.015 #0.15

                    # Adjust probabilities using form and H2H factors
                    final_probs = {
                        'one': max(0.01, np.random.normal(0, sd) + (ground_probs['one_prob'] + batter_probs['one_prob'] + bowler_probs['one_prob']) * (form_factor_bat.get(striker, 1)*np.random.normal(1,0.1)) / 3) * rr_factor*middle_factor,
                        'two': max(0.01,np.random.normal(0, sd) + (ground_probs['two_prob'] + batter_probs['two_prob'] + bowler_probs['two_prob']) * (form_factor_bat.get(striker, 1)*np.random.normal(1,0.1)) / 3) * rr_factor*middle_factor,
                        'three': max(0.01,np.random.normal(0,sd) + (ground_probs['three_prob'] + batter_probs['three_prob'] + bowler_probs['three_prob']) * (form_factor_bat.get(striker, 1)*np.random.normal(1,0.1)) / 3),
                        'four': max(0.01,np.random.normal(0, sd) + (ground_probs['four_prob'] + batter_probs['four_prob'] + bowler_probs['four_prob']) * (form_factor_bat.get(striker, 1)*np.random.normal(1,0.1))/ 3) * rr_factor * death_factor*bdry_factor*l_o_bdry_factor*middle_factor*free_hit_factor_bdry,
                        'six': max(0.01,np.random.normal(0, sd) + (ground_probs['six_prob'] + batter_probs['six_prob'] + bowler_probs['six_prob']) * (form_factor_bat.get(striker, 1)*np.random.normal(1,0.1)) / 3) * rr_factor * death_factor*bdry_factor*l_o_bdry_factor*middle_factor*free_hit_factor_bdry,
                        'dot': max(0.01,np.random.normal(0,0.03) + (ground_probs['dot_prob'] + batter_probs['dot_prob'] + bowler_probs['dot_prob']) * (1 / (form_factor_bat.get(striker, 1)*np.random.normal(1,0.1))) / 3) * g_factor*dot_factor*l_o_dot_factor * (1/death_factor) * (1/last_3_ov_factor) * (1/bowl_type_factor[0] if len(bowl_type_factor)>0 else 1),
                        'wicket': max(0.01,np.random.normal(0, 0.045) + (ground_probs['wkt_prob'] + batter_probs['out_prob'] + bowler_probs['wkt_prob']) * (form_factor_bowl.get(bowler, 1)*np.random.normal(1,0.1)) * (h2h_bowl[0] if len(h2h_bowl)>0 else 1) / 3) * wkt_factor * free_hit_factor*l_o_out_factor * g_factor * (1/bowl_type_factor[0] if len(bowl_type_factor)>0 else 1),
                        '0+runout': (0.003)/3,
                        '1+runout': (0.0025)/3,
                        '2+runout': (0.002)/3,
                        '3+runout': 0.0002,
                        'wide': max(0.01,np.random.normal(0, 0.02) + ground_probs['wide_prob']),
                        'noball': ground_probs.get('no_prob', 0.01),
                        'bye': ground_probs.get('bye_prob', 0.01),
                        'legbye': ground_probs.get('legbye_prob', 0.01)
                    }

                    # Normalize probabilities so they sum up to 1
                    total = sum(final_probs.values())
                    final_probs = {k: v / total for k, v in final_probs.items()}

                    # Simulate outcome of the ball
                    event = np.random.choice(list(final_probs.keys()), p=np.ravel(list(final_probs.values())))

                    # Update legal ball count for valid deliveries
                    legal_balls += 1 if event not in ['wide', 'noball'] else 0
                    wickets_down += 1 if event in ['wicket', '0+runout','1+runout','2+runout','3+runout'] else 0
                    legal_balls_remaining = 120 - legal_balls
                    #runs_remaining = target - runs_scored
                    wkt_type = ''
                    fielder= ''
                    if event == 'wicket':
                        wkt_type = random.choices(['Caught', 'Bowled', 'Stumped/Runout by Keeper', 'HitWicket'], weights=[0.7, 0.28, 0.01, 0.01])[0]
                        #row.update({'wicket_event': wkt_type})
                        if wkt_type == 'Caught':
                            weights = [0.075] * 10 + [0.25]
                            # Randomly choose a fielder based on weights
                            fielder = random.choices(total_list, weights=weights)[0]
                        elif wkt_type == 'Stumped/Runout by Keeper':
                            fielder = total_list[-1]
                    elif event in ['0+runout','1+runout','2+runout','3+runout']:
                        weights = [0.0975] * 10 + [0.025]
                        # Randomly choose a fielder based on weights
                        fielder = random.choices(total_list, weights=weights)[0]

                    # Capture details of this ball
                    row = match_context.copy()
                    row.update({
                        'innings': match_context['innings'],
                        'ball': all_balls, 
                        'striker': striker,
                        'non_striker': non_striker,
                        'bowler': bowler,
                        'runs_off_bat': 1 if event in ['one','1+runout'] else 2 if event in ['2+runout','two'] else 3 if event in ['3+runout','three'] else 4 if event == 'four' else 6 if event == 'six' else 0,
                        'extras': 1 if event in ['wide', 'noball', 'bye', 'legbye'] else 0,
                        'wides': 1 if event == 'wide' else 0,
                        'noballs': 1 if event == 'noball' else 0,
                        'byes': 1 if event == 'bye' else 0,
                        'legbyes': 1 if event == 'legbye' else 0,
                        'wicket_type': 'out' if event == 'wicket' else 'runout' if event in ['0+runout','1+runout','2+runout','3+runout'] else None,
                        'player_dismissed': striker if event in ['wicket','0+runout','2+runout'] else non_striker if event in ['1+runout','3+runout'] else None,
                        'legal_balls_bowled': legal_balls,
                        'legal_balls_remaining': legal_balls_remaining,
                        'target': target,
                        'wicket_event' : wkt_type,
                        'fielder': fielder
                    })

                    # Append data for each ball to simulation DataFrame
                    df_simulation_2 = pd.concat([df_simulation_2, pd.DataFrame([row])], ignore_index=True)

                    runs_ = row['runs_off_bat']+row['extras']
                    runs_scored = runs_scored+ runs_

                    reqd_run_rate = ((6 * (target-runs_scored) / legal_balls_remaining)                                                if legal_balls_remaining  > 0 else 6 + (target-runs_scored)) 


                    print(f"{bowler} to {striker} : {event}, score: {runs_scored}")
                    if event == 'noball':
                        print("**FREE HIT!!**")

                    # Switch batters on odd runs or for a wicket
                    # Switch batters on odd runs or for a wicket
                    if event in ['wicket','0+runout','2+runout']:
                        striker_runs = df_simulation_2[df_simulation_2.striker==striker].runs_off_bat.sum()
                        print("**WICKET!!**")
                        if event == 'wicket':
                            if wkt_type == 'Caught':
                                print(f"Caught by {fielder}!")
                            elif wkt_type == 'Stumped/Runout by Keeper':
                                print(f"{wkt_type}!")
                            else:
                                print(f"{wkt_type}!!")
                        else:
                            print(f"Runout by {fielder}!")
                        print(f"batter out: {striker}, for {striker_runs}")
                        striker = next_batsman() #############
                        print("<><>"*7)
                        try:
                            new_batter_ssn_stat = bat_stat[bat_stat.striker==striker][['num_innings','runs','SR','Bat_avg']].values.tolist()[0]
                            new_batter_form_stat = form_bat[form_bat.striker==striker][['num_innings','runs','bat_sr','bat_avg']].values.tolist()[0]
                        except:
                            new_batter_ssn_stat = [0,0, 'not played','not played']
                            new_batter_form_stat = [0, 0, 'not played','not played']
                        if wickets_down<10:
                            print(f"NEW Batter in: {striker} \n SPL Career:: \n Innings = {int(new_batter_ssn_stat[0])}, Runs = {int(new_batter_ssn_stat[1])}, SR = {new_batter_ssn_stat[2]}, Avg = {new_batter_ssn_stat[3]}")
                            print(" "*10)
                            print(f"Recent Form :: \n (last {int(new_batter_form_stat[0])} innings) Runs = {int(new_batter_form_stat[1])}, SR = {new_batter_form_stat[2]}, Avg = {new_batter_form_stat[3]}")
                            print(" "*10)
                            print('---' * 10)
                        print("<><>"*7)

                        fow = df_simulation_2.runs_off_bat.sum()+df_simulation_2.extras.sum()
                        fow_balls = str(legal_balls//6)+'.'+str(legal_balls%6)

                        ##INSERT SEASON STATS HERE
                    elif event in ['1+runout','3+runout']:
                        non_striker_runs = df_simulation_2[df_simulation_2.striker==non_striker].runs_off_bat.sum()
                        print("**WICKET!!**")
                        print(f"Runout by {fielder}!")
                        print(f"batter out: {non_striker}, for {non_striker_runs}")
                        non_striker = next_batsman()
                        print("<><>"*7)
                        try:
                            new_batter_ssn_stat = bat_stat[bat_stat.striker==non_striker][['num_innings','runs','SR','Bat_avg']].values.tolist()[0]
                            new_batter_form_stat = form_bat[form_bat.striker==non_striker][['num_innings','runs','bat_sr','bat_avg']].values.tolist()[0]
                        except:
                            new_batter_ssn_stat = [0,0, 'not played','not played']
                            new_batter_form_stat = [0, 0, 'not played','not played']
                        if wickets_down<10:
                            print(f"NEW Batter in: {non_striker} \n SPL Career:: \n Innings = {int(new_batter_ssn_stat[0])}, Runs = {int(new_batter_ssn_stat[1])}, SR = {new_batter_ssn_stat[2]}, Avg = {new_batter_ssn_stat[3]}")
                            print(" "*10)
                            print(f"Recent Form :: \n (last {int(new_batter_form_stat[0])} innings) Runs = {int(new_batter_form_stat[1])}, SR = {new_batter_form_stat[2]}, Avg = {new_batter_form_stat[3]}")
                            print(" "*10)
                            print('---' * 10)
                        print("<><>"*7)

                        fow = df_simulation_2.runs_off_bat.sum()+df_simulation_2.extras.sum()
                        fow_balls = str(legal_balls//6)+'.'+str(legal_balls%6)

                    elif event in ['one', 'three','bye','legbye']:
                        striker, non_striker = non_striker, striker  # Swap striker and non-striker

                    if event in ['bye','legbye']:
                        runs_conceeded_o += row['runs_off_bat']
                    else:
                        runs_conceeded_o += row['runs_off_bat']+row['extras']
                        
                    runs_over += row['runs_off_bat'] + row['extras']

                    if event == 'wicket':
                        wickets_taken[bowler] += 1

                    if legal_balls in [38, 55, 87]:
                        #print('  '*10)
                        try:
                            h2h__ = h2h_[(h2h_['striker']==striker)&(h2h_['bowler']==bowler)][['runs_scored','balls_faced','outs']].values.tolist()[0]
                        except:
                            h2h__ = ['not played','not played','not played']
                        if h2h__[1] != 'not played':
                            print('  '*10)
                            print(f"Random Statbite :- \n {striker} vs {bowler} --> runs = {int(h2h__[0])}, balls = {int(h2h__[1])}, dismissals = {int(h2h__[2])} (before this game)")
                            print('---'*10)
                        else:
                            print('  '*10)
                            print(f"Random Statbite :- \n {striker} hasn't faced {bowler} before!!")
                            print('---'*10)

                    if legal_balls in [46, 62, 71]:
                        #print('  '*10)
                        if bowl_type=='Pace':
                            try:
                                pace_score = pace_stat[pace_stat['striker']==striker][['SR','Bat_avg','bpb']].values.tolist()[0]
                            except:
                                pace_score = ['not played','not played','not played']
                            if pace_score[1] != 'not played':
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} vs {bowl_type} --> SR = {int(pace_score[0])}, Avg = {int(pace_score[1])}, BpB = {(pace_score[2])} (before this game)")
                                print('---'*10)
                            else:
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} hasn't faced {bowl_type} bowling before!!")
                                print('---'*10)
                        elif bowl_type=='Spin':
                            try:
                                spin_score = spin_stat[spin_stat['striker']==striker][['SR','Bat_avg','bpb']].values.tolist()[0]
                            except:
                                spin_score = ['not played','not played','not played']
                            if spin_score[1] != 'not played':
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} vs {bowl_type} --> SR = {int(spin_score[0])}, Avg = {int(spin_score[1])}, BpB = {(spin_score[2])} (before this game)")
                                print('---'*10)
                            else:
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} hasn't faced {bowl_type} bowling before!!")
                                print('---'*10)

                    # Change bowler every 6 legal balls (end of an over)
                    if (legal_balls % 6 == 0)&(legal_balls!=legal_balls_last):
                        striker, non_striker = non_striker, striker #over ends
                        overs_bowled[bowler] += 1
                        runs_conceeded_over[bowler] += runs_conceeded_o

                        ##############
                        if overs_bowled[bowler] == 4:
                            bowlers_df = bowlers_df[bowlers_df['Func_Name']!=bowler]
                            
                        if fixed == False : 
                            if over+1 == 2:
                                bowler = bowlers_df.loc[bowlers_df['bowl'] == 2, 'Func_Name'].values[0]
                            else:
                                bowler_probabilities = calculate_bowler_probabilities(bowlers_df[bowlers_df['Func_Name']!=bowler], overs_bowled, last_over_bowled, over+1, wickets_taken, overs_bowled)
                                bowler = np.random.choice(bowlers_df[bowlers_df['Func_Name']!=bowler]['Func_Name'], p=bowler_probabilities)

                        print(' '*10)
                        print(f"runs in this over : {runs_over}")
                        print(' '*10)
                        print(f"end of over {legal_balls//6}; score :: **{runs_scored}** for **{wickets_down}**")
                        over = min(20, legal_balls//6 + 1)
                        if fixed == True:
                            if legal_balls//6<20:
                                bowler = bowlers_df.loc[bowlers_df['bowl'] == fixed_order[over-1], 'Func_Name'].values[0]
                            #print(over, bowler)
                        print(f"last fall-of-wicket : {fow}-{wickets_down} ({fow_balls})")
                        print(' '*10)
                        #print(f"current partnership : {int(runs_scored)-int(fow)} ({int(legal_balls)-int(fow_balls)} legal balls)")
                        
                        print(' '*10)
                        if (legal_balls//6)>19:
                            print(f"Runs remaining = {max(target-runs_scored, 0)}")
                        else:
                            print(f"Runs remaining = {max(target-runs_scored, 0)}, Required Run-rate = {np.round(max(reqd_run_rate,0), 2)}")

                        print('---'*10)
                        if (legal_balls//6)==3: #3rd over done
                            try:
                                striker_phase = bat_phase[(bat_phase['striker']==striker)&(bat_phase['phase']=='pp')][['runs','strike_rate']].values.tolist()[0]
                            except:
                                striker_phase = [0, 'not played']
                            if striker_phase[1] != 'not played':
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} in PowerPlay (before this game) - runs = {int(striker_phase[0])}, SR = {striker_phase[1]}")
                                print('---'*10)
                            else:
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} batting in PowerPlay for the first time!!")
                                print('---'*10)

                        if (legal_balls//6)==10: #10th over done
                            try:
                                striker_phase = bat_phase[(bat_phase['striker']==striker)&(bat_phase['phase']=='middle')][['runs','strike_rate']].values.tolist()[0]
                            except:
                                striker_phase = [0, 'not played']
                            if striker_phase[1] != 'not played':
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} in Middle-Overs (before this game) - runs = {int(striker_phase[0])}, SR = {striker_phase[1]}")
                                print('---'*10)
                            else:
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} batting in Middle-Overs for the first time!!")
                                print('---'*10)

                        if (legal_balls//6)==16: #16th over done
                            try:
                                striker_phase = bat_phase[(bat_phase['striker']==striker)&(bat_phase['phase']=='death')][['runs','strike_rate']].values.tolist()[0]
                            except:
                                striker_phase = [0, 'not played']
                            if striker_phase[1] != 'not played':
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} in Death-Overs (before this game) - runs = {int(striker_phase[0])}, SR = {striker_phase[1]}")
                                print('---'*10)
                            else:
                                print('  '*10)
                                print(f"Random Statbite :- \n {striker} batting in Death-Overs for the first time!!")
                                print('---'*10)    

                        #print('---'*10)
                        print('-.-.-.'*10)
                        print(' '*10)
                        
                        if overs_bowled[bowler] == 0 and (legal_balls//6)<20:
                            try:
                                new_bowler_ssn_stat = bowl_stat[bowl_stat.bowler==bowler][['num_innings','wkts','economy']].values.tolist()[0]
                                new_bowler_form_stat = form_ball[form_ball.bowler==bowler][['num_innings','wkts','bowl_eco']].values.tolist()[0]
                            except:
                                new_bowler_ssn_stat = [0,0, 'not played']
                                new_bowler_form_stat = [0,0, 'not played']
                            print(f"NEW bowler -> {bowler} \n SPL Career:: \n Innings = {int(new_bowler_ssn_stat[0])}, Wickets = {int(new_bowler_ssn_stat[1])}, Economy = {new_bowler_ssn_stat[2]}")
                            print(f"Form : (last {int(new_bowler_form_stat[0])} innnigs) \n  Wickets = {int(new_bowler_form_stat[1])}, Economy = {new_bowler_form_stat[2]}")

                            print('---' * 10)
                        if (legal_balls//6)==2: #2nd over done
                            try:
                                bowler_phase = bowl_phase[(bowl_phase['bowler']==bowler)&(bowl_phase['phase']=='pp')][['balls','economy']].values.tolist()[0]
                            except:
                                bowler_phase = [0, 'not played']
                            if bowler_phase[1] != 'not played':
                                print('  '*10)
                                print(f"Random Statbite :- \n {bowler} in PowerPlay (before this game) - balls = {int(bowler_phase[0])}, Eco = {bowler_phase[1]}")
                                print('---'*10)
                            else:
                                print('  '*10)
                                print(f"Random Statbite :- \n {bowler} bowling in PowerPlay for the first time!!")
                                print('---'*10)

                        if (legal_balls//6)==12: #12th over done
                            try:
                                bowler_phase = bowl_phase[(bowl_phase['bowler']==bowler)&(bowl_phase['phase']=='middle')][['balls','economy']].values.tolist()[0]
                            except:
                                bowler_phase = [0, 'not played']
                            if bowler_phase[1] != 'not played':
                                print('  '*10)
                                print(f"Random Statbite :- \n {bowler} in Middle-Overs (before this game) - balls = {int(bowler_phase[0])}, Eco = {bowler_phase[1]}")
                                print('---'*10)
                            else:
                                print('  '*10)
                                print(f"Random Statbite :- \n {bowler} bowling in Middle-Overs for the first time!!")
                                print('---'*10)

                        if (legal_balls//6)==17: #17th over done
                            try:
                                bowler_phase = bowl_phase[(bowl_phase['bowler']==bowler)&(bowl_phase['phase']=='death')][['balls','economy']].values.tolist()[0]
                            except:
                                bowler_phase = [0, 'not played']
                            if bowler_phase[1] != 'not played':
                                print('  '*10)
                                print(f"Random Statbite :- \n {bowler} in Death-Overs (before this game) - balls = {int(bowler_phase[0])}, Eco = {bowler_phase[1]}")
                                print('---'*10)
                            else:
                                print('  '*10)
                                print(f"Random Statbite :- \n {bowler} bowling in Death-Overs for the first time!!")
                                print('---'*10)


                        print(' '*10)
                        runs_conceeded_o = 0
                        runs_over = 0
                        last_3_ov_runs = df_simulation_2[(df_simulation_2['legal_balls_bowled']>max(0,legal_balls-18))]['runs_off_bat'].sum()
                        last_3_ov_wkts = df_simulation_2[(df_simulation_2['legal_balls_bowled']>max(0,legal_balls-18))]['wicket_type'].count()

                        #print("---****________****", last_3_ov_runs, last_3_ov_wkts)

                    legal_balls_last += 1 if event not in ['wide', 'noball'] else 0
                    #runs_remaining = target - runs_scored

            df_mod = func_1(df_simulation_2)

            df_mod_2 = func_2(df_mod)

            df_mod_2['runs_remaining'] = df_mod_2['target']-df_mod_2['runs_scored']
            df_mod_2['reqd_run_rate'] = np.where(
                df_mod_2['legal_balls_remaining'] > 0,
                (6 * (df_mod_2['target'] - df_mod_2['runs_scored']) / df_mod_2['legal_balls_remaining']),
                6 + (df_mod_2['target'] - df_mod_2['runs_scored'])
            )

            bat_2nd = (other_team if decision=='Bat' else toss_win_team)
            bowl_2nd = (toss_win_team if decision=='Bat' else other_team)

            df_mod_2['batting_team'] = bat_2nd
            df_mod_2['bowling_team'] = bowl_2nd

            columns = ['innings','striker','non_striker','bowler','runs_off_bat','extras','wicket_type','player_dismissed',
                      'legal_balls_bowled','bowler_wicket','run_rate','last_fow','reqd_run_rate']
            #df_mod_2#[columns]

            print(f"total: {df_mod_2['runs_scored'].max()}, wickets: {df_mod_2['wickets_down'].max()}")

            df_mod_2[df_mod_2.isWicket>0]

            ##bowling stats

            df_mod_1['runs_conceeded'] = df_mod_1['runs_off_bat']+df_mod_1['wides']+df_mod_1['noballs']

            df_mod_1['isDotforbowler'] = np.where((df_mod_1['runs_conceeded']==0)&(df_mod_1['islegal']==1), 1, 0)

            df_mod_2['runs_conceeded'] = df_mod_2['runs_off_bat']+df_mod_2['wides']+df_mod_2['noballs']

            df_mod_2['isDotforbowler'] = np.where((df_mod_2['runs_conceeded']==0)&(df_mod_2['islegal']==1), 1, 0)

            df_mod = pd.concat([df_mod_1,df_mod_2],axis=0).reset_index(drop=True)

            inn1_score = df_mod[df_mod.innings==1].runs_scored.max()
            inn2_score = df_mod[df_mod.innings==2].runs_scored.max()

            if inn1_score>inn2_score:
                print(f"{bowl_2nd} wins!")
            elif inn1_score<inn2_score:
                print(f"{bat_2nd} wins!")
            else:
                print("it's a tie!!!!!")

            #################
            
    print(f"All output has been saved to {output_file}")

    df_all = df_all.append(df_mod).reset_index(drop=True)


    ##########################################
    t2 = time.time()

########################################################################################
########################################################################################

########################################################################################
########################################################################################

########################################################################################
########################################################################################

########################################################################################
########################################################################################
## bowler stats

bowler_stats = df_all.groupby(['bowler','bowling_team']).agg(   ##,'innings'
    num_innings = ('match_id','nunique'),
    runs = ('runs_conceeded','sum'),
    balls = ('islegal' ,'sum'),
    wkts = ('isBowlerWicket','sum'),
    fours = ('isFour', 'sum'),
    sixes = ('isSix','sum'),
    dots = ('isDotforbowler','sum'),
    
    ones = ('isOne','sum'),
    twos = ('isTwo','sum'),
    threes = ('isThree','sum'),
    wides = ('wides','sum'),
    noballs = ('noballs','sum')
        
    
).reset_index()

bowler_stats['economy'] = 6*bowler_stats['runs']/bowler_stats['balls']
bowler_stats['strike_rate'] = bowler_stats['balls']/bowler_stats['wkts']
bowler_stats['bpb'] = bowler_stats['balls']/(bowler_stats['fours']+bowler_stats['sixes'])
bowler_stats['dot_%'] = 100*bowler_stats['dots']/bowler_stats['balls']

#########ADDING 3+,4+,5+ wkts#########
mbm_bowl = df_all.groupby(['bowler','match_id'])['isBowlerWicket'].sum().reset_index().sort_values(by='bowler')

_3plus = mbm_bowl[mbm_bowl.isBowlerWicket>=3].groupby('bowler')['match_id'].count().reset_index()
_4plus = mbm_bowl[mbm_bowl.isBowlerWicket>=4].groupby('bowler')['match_id'].count().reset_index()
_5plus = mbm_bowl[mbm_bowl.isBowlerWicket>=5].groupby('bowler')['match_id'].count().reset_index()

_3plus.columns = ['bowler','3+_wkts']
_4plus.columns = ['bowler','4+_wkts']
_5plus.columns = ['bowler','5+_wkts']


bowler_stats = bowler_stats.merge(_3plus, on='bowler', how='left')
bowler_stats = bowler_stats.merge(_4plus, on='bowler', how='left')
bowler_stats = bowler_stats.merge(_5plus, on='bowler', how='left')

bowler_stats[['3+_wkts','4+_wkts','5+_wkts']] = \
                    bowler_stats[['3+_wkts','4+_wkts','5+_wkts']].fillna(0).astype(int)
#########ADDING 3+,4+,5+ wkts#########
"""
#########ADDING BEST PERFORMANCE##############
mbm_ball_bat = df_all.groupby(['bowler','match_id'])[['runs_conceeded','islegal','isBowlerWicket']]\
                                    .sum().reset_index().sort_values(by='bowler')

mbm_ball_bat = mbm_ball_bat.rename(columns={'bowler':'player'})


mbm_ball_bat['isBowlerWicket'] = mbm_ball_bat['isBowlerWicket'].fillna(0).astype(int)

# Get the index of the highest score for each striker (resolving ties using fewer balls)
idx = mbm_ball_bat.groupby('player')['isBowlerWicket'].idxmax()

# Filter the rows
most_wkts = mbm_ball_bat.loc[idx]

most_wkts['best_performance'] = most_wkts['isBowlerWicket'].astype(str)+ str('-')+\
            most_wkts['runs_conceeded'].astype(str)+str(' (')+most_wkts['islegal'].astype(str)+str(')')
        

most_wkts = most_wkts.rename(columns={'player':'bowler'})

bowler_stats = bowler_stats.merge(most_wkts[['bowler','best_performance']], on='bowler',how='left')
#########ADDING BEST PERFORMANCE##############
"""

# Sort DataFrame based on the custom order
bowler_stats = bowler_stats.sort_values(['wkts','economy'], ascending=[False, True]).reset_index(drop=True)

#batting stats

batter_stats = df_all.groupby(['striker','batting_team']).agg(  ##,'innings'
    num_innings = ('match_id','nunique'),
    runs = ('runs_off_bat','sum'),
    balls = ('is_faced_by_batter' ,'sum'),
    outs = ('is_striker_Out','sum'),
    fours = ('isFour', 'sum'),
    sixes = ('isSix','sum'),
    dots = ('isDotforBatter','sum'),
    
    ones = ('isOne','sum'),
    twos = ('isTwo','sum'),
    threes = ('isThree','sum')
    
    
    
    
).reset_index()

##addition of runouts
runout_count = df_all[df_all.wicket_type=='runout'].groupby('player_dismissed')['isWicket'].count().reset_index()

for index,row in batter_stats.iterrows():
    outs = row['outs']
    batter = row['striker']
    runout_add = 0
    
    runouts_add_df = runout_count[runout_count.player_dismissed==batter]
    if runouts_add_df.shape[0]>0:
        runout_add = runouts_add_df['isWicket'].unique()[0]
        
    outs = outs+runout_add
    batter_stats.at[index, 'outs'] = outs
#############    

############ STRIKER RUNOUT MINUS
own_runout_count = df_all[df_all.wicket_type=='runout'].groupby('player_dismissed')['is_striker_Out'].sum().reset_index()

for index,row in batter_stats.iterrows():
    outs = row['outs']
    batter = row['striker']
    own_runout_minus = 0
    
    runouts_add_df = own_runout_count[own_runout_count.player_dismissed==batter]
    if runouts_add_df.shape[0]>0:
        own_runout_minus = runouts_add_df['is_striker_Out'].unique()[0]
        
    outs = outs-own_runout_minus
    batter_stats.at[index, 'outs'] = outs
#############    
    
batter_stats['strike_rate'] = 100*batter_stats['runs']/batter_stats['balls']
batter_stats['balls_per_dismissal'] = batter_stats['balls']/batter_stats['outs']
batter_stats['bat_avg'] = batter_stats['runs']/batter_stats['outs']
batter_stats['bpb'] = batter_stats['balls']/(batter_stats['fours']+batter_stats['sixes'])
batter_stats['dot_%'] = 100*batter_stats['dots']/batter_stats['balls']

batter_stats = batter_stats.sort_values(['runs','strike_rate'], ascending=[False,False]).reset_index(drop=True)

#########ADDING 30+,50+,100+ scores#########
mbm_bat = df_all.groupby(['striker','match_id'])['runs_off_bat'].sum().reset_index().sort_values(by='striker')

_30plus = mbm_bat[mbm_bat.runs_off_bat>=30].groupby('striker')['match_id'].count().reset_index()
_50plus = mbm_bat[mbm_bat.runs_off_bat>=50].groupby('striker')['match_id'].count().reset_index()
_100plus = mbm_bat[mbm_bat.runs_off_bat>=100].groupby('striker')['match_id'].count().reset_index()

_30plus.columns = ['striker','30+_scores']
_50plus.columns = ['striker','50+_scores']
_100plus.columns = ['striker','100+_scores']


batter_stats = batter_stats.merge(_30plus, on='striker', how='left')
batter_stats = batter_stats.merge(_50plus, on='striker', how='left')
batter_stats = batter_stats.merge(_100plus, on='striker', how='left')

batter_stats[['30+_scores','50+_scores','100+_scores']] = \
                    batter_stats[['30+_scores','50+_scores','100+_scores']].fillna(0).astype(int)
#########ADDING 30+,50+,100+ scores#########
"""
#########ADDING HIGHEST SCORES##############
mbm_bat_ball = df_all.groupby(['striker','match_id'])[['runs_off_bat','is_faced_by_batter']]\
                                    .sum().reset_index().sort_values(by='striker')

mbm_bat_ball = mbm_bat_ball.rename(columns={'striker':'player'})

mbm_out = df_all.groupby(['player_dismissed','match_id'])['start_date']\
                                    .count().reset_index().sort_values(by='player_dismissed')

mbm_out = mbm_out.rename(columns={'player_dismissed':'player','start_date':'out'})
mbm_out['out'] = mbm_out['out'].fillna(0).astype(int)

mbm = mbm_bat_ball.merge(mbm_out, on=['player','match_id'], how='left')
mbm['out'] = mbm['out'].fillna(0).astype(int)

mbm['out_str'] = ''
mbm.loc[mbm['out']==0,'out_str'] = '*'

# Get the index of the highest score for each striker (resolving ties using fewer balls)
idx = mbm.groupby('player')['runs_off_bat'].idxmax()

# Filter the rows
highest_scores = mbm.loc[idx]

highest_scores['high_score'] = highest_scores['runs_off_bat'].astype(str)+ highest_scores['out_str']+ str('(')+\
                                    highest_scores['is_faced_by_batter'].astype(str)+str(')')
        

highest_scores = highest_scores.rename(columns={'player':'striker'})

batter_stats = batter_stats.merge(highest_scores[['striker','high_score']], on='striker',how='left')
#########ADDING HIGHEST SCORES##############
"""

batter_stats = batter_stats.round(2)
bowler_stats = bowler_stats.round(2)

#################                                  
df_match_info = pd.DataFrame()

df_match_info['match_id'] = df_all.match_id.unique()
df_match_info['team_1'] = ''
df_match_info['team_2'] = ''
df_match_info['team_1_total'] = 0
df_match_info['team_1_balls'] = 0
df_match_info['team_2_total'] = 0
df_match_info['team_2_balls'] = 0
df_match_info['winner'] = ''


for index,row in df_match_info.iterrows():
    subset_df = df_all[df_all.match_id==row['match_id']][df_all.innings==1]
    t1 = subset_df['batting_team'].unique()[0]
    t1_runs = subset_df['runs_scored'].max()
    t1_balls = subset_df['legal_balls_bowled'].max()
    team_1_total = t1_runs
    team_1_balls = t1_balls
    
    subset_df = df_all[df_all.match_id==row['match_id']][df_all.innings==2]
    t2 = subset_df['batting_team'].unique()[0]
    t2_runs = subset_df['runs_scored'].max()
    t2_balls = subset_df['legal_balls_bowled'].max()
    team_2_total = t2_runs
    team_2_balls = t2_balls
    
    winner = t1 if team_1_total>team_2_total else t2 if team_1_total<team_2_total else 'TIE'
    
    df_match_info.at[index, 'team_1'] = t1
    df_match_info.at[index, 'team_2'] = t2
    df_match_info.at[index, 'team_1_total'] = team_1_total
    df_match_info.at[index, 'team_1_balls'] = team_1_balls
    df_match_info.at[index, 'team_2_total'] = team_2_total
    df_match_info.at[index, 'team_2_balls'] = team_2_balls
    df_match_info.at[index, 'winner'] = winner
    


pts_table = pd.DataFrame(df_match_info.groupby('winner')['team_2_balls'].count()*2).reset_index()

pts_table.columns = ['team','points']


CSK_runs_for = []
CSK_balls_for = []
DC_runs_for = []
DC_balls_for = []
GT_runs_for = []
GT_balls_for = []
KKR_runs_for = []
KKR_balls_for = []
LSG_runs_for = []
LSG_balls_for = []
MI_runs_for = []
MI_balls_for = []
PBKS_runs_for = []
PBKS_balls_for = []
RCB_runs_for = []
RCB_balls_for = []
RR_runs_for = []
RR_balls_for = []
SRH_runs_for = []
SRH_balls_for = []

CSK_runs_against = []
CSK_balls_against = []
DC_runs_against = []
DC_balls_against = []
GT_runs_against = []
GT_balls_against = []
KKR_runs_against = []
KKR_balls_against = []
LSG_runs_against = []
LSG_balls_against = []
MI_runs_against = []
MI_balls_against = []
PBKS_runs_against = []
PBKS_balls_against = []
RCB_runs_against = []
RCB_balls_against = []
RR_runs_against = []
RR_balls_against = []
SRH_runs_against = []
SRH_balls_against = []

for m in df_all.match_id.unique():
    m_df = df_all[df_all.match_id==m].reset_index(drop=True)
    
    m_df_1 = m_df[m_df.innings==1]
    runs_1 = m_df_1.runs_scored.max()
    balls_1 = m_df_1.legal_balls_bowled.max()
    balls_1 = max(120,balls_1)
    
    m_df_2 = m_df[m_df.innings==2]
    runs_2 = m_df_2.runs_scored.max()
    balls_2 = m_df_2.legal_balls_bowled.max()
    wkts_2 = m_df_2.wickets_down.max()
    balls_2 = 120 if wkts_2==10 else balls_2
    
    
        

    if 'CSK' in m_df_1.batting_team.unique():
        CSK_runs_for.append(runs_1)
        CSK_balls_for.append(balls_1)
    if 'DC' in m_df_1.batting_team.unique():
        DC_runs_for.append(runs_1)
        DC_balls_for.append(balls_1)
    if 'GT' in m_df_1.batting_team.unique():
        GT_runs_for.append(runs_1)
        GT_balls_for.append(balls_1)
    if 'KKR' in m_df_1.batting_team.unique():
        KKR_runs_for.append(runs_1)
        KKR_balls_for.append(balls_1)
    if 'LSG' in m_df_1.batting_team.unique():
        LSG_runs_for.append(runs_1)
        LSG_balls_for.append(balls_1)
    if 'MI' in m_df_1.batting_team.unique():
        MI_runs_for.append(runs_1)
        MI_balls_for.append(balls_1)
    if 'PBKS' in m_df_1.batting_team.unique():
        PBKS_runs_for.append(runs_1)
        PBKS_balls_for.append(balls_1)
    if 'RCB' in m_df_1.batting_team.unique():
        RCB_runs_for.append(runs_1)
        RCB_balls_for.append(balls_1)
    if 'RR' in m_df_1.batting_team.unique():
        RR_runs_for.append(runs_1)
        RR_balls_for.append(balls_1)
    if 'SRH' in m_df_1.batting_team.unique():
        SRH_runs_for.append(runs_1)
        SRH_balls_for.append(balls_1)


    if 'CSK' in m_df_2.batting_team.unique():
        CSK_runs_for.append(runs_2)
        CSK_balls_for.append(balls_2)
    if 'DC' in m_df_2.batting_team.unique():
        DC_runs_for.append(runs_2)
        DC_balls_for.append(balls_2)
    if 'GT' in m_df_2.batting_team.unique():
        GT_runs_for.append(runs_2)
        GT_balls_for.append(balls_2)
    if 'KKR' in m_df_2.batting_team.unique():
        KKR_runs_for.append(runs_2)
        KKR_balls_for.append(balls_2)
    if 'LSG' in m_df_2.batting_team.unique():
        LSG_runs_for.append(runs_2)
        LSG_balls_for.append(balls_2)
    if 'MI' in m_df_2.batting_team.unique():
        MI_runs_for.append(runs_2)
        MI_balls_for.append(balls_2)
    if 'PBKS' in m_df_2.batting_team.unique():
        PBKS_runs_for.append(runs_2)
        PBKS_balls_for.append(balls_2)
    if 'RCB' in m_df_2.batting_team.unique():
        RCB_runs_for.append(runs_2)
        RCB_balls_for.append(balls_2)
    if 'RR' in m_df_2.batting_team.unique():
        RR_runs_for.append(runs_2)
        RR_balls_for.append(balls_2)
    if 'SRH' in m_df_2.batting_team.unique():
        SRH_runs_for.append(runs_2)
        SRH_balls_for.append(balls_2)

    if 'CSK' in m_df_1.bowling_team.unique():
        CSK_runs_against.append(runs_1)
        CSK_balls_against.append(balls_1)
    if 'DC' in m_df_1.bowling_team.unique():
        DC_runs_against.append(runs_1)
        DC_balls_against.append(balls_1)
    if 'GT' in m_df_1.bowling_team.unique():
        GT_runs_against.append(runs_1)
        GT_balls_against.append(balls_1)
    if 'KKR' in m_df_1.bowling_team.unique():
        KKR_runs_against.append(runs_1)
        KKR_balls_against.append(balls_1)
    if 'LSG' in m_df_1.bowling_team.unique():
        LSG_runs_against.append(runs_1)
        LSG_balls_against.append(balls_1)
    if 'MI' in m_df_1.bowling_team.unique():
        MI_runs_against.append(runs_1)
        MI_balls_against.append(balls_1)
    if 'PBKS' in m_df_1.bowling_team.unique():
        PBKS_runs_against.append(runs_1)
        PBKS_balls_against.append(balls_1)
    if 'RCB' in m_df_1.bowling_team.unique():
        RCB_runs_against.append(runs_1)
        RCB_balls_against.append(balls_1)
    if 'RR' in m_df_1.bowling_team.unique():
        RR_runs_against.append(runs_1)
        RR_balls_against.append(balls_1)
    if 'SRH' in m_df_1.bowling_team.unique():
        SRH_runs_against.append(runs_1)
        SRH_balls_against.append(balls_1)


    if 'CSK' in m_df_2.bowling_team.unique():
        CSK_runs_against.append(runs_2)
        CSK_balls_against.append(balls_2)
    if 'DC' in m_df_2.bowling_team.unique():
        DC_runs_against.append(runs_2)
        DC_balls_against.append(balls_2)
    if 'GT' in m_df_2.bowling_team.unique():
        GT_runs_against.append(runs_2)
        GT_balls_against.append(balls_2)
    if 'KKR' in m_df_2.bowling_team.unique():
        KKR_runs_against.append(runs_2)
        KKR_balls_against.append(balls_2)
    if 'LSG' in m_df_2.bowling_team.unique():
        LSG_runs_against.append(runs_2)
        LSG_balls_against.append(balls_2)
    if 'MI' in m_df_2.bowling_team.unique():
        MI_runs_against.append(runs_2)
        MI_balls_against.append(balls_2)
    if 'PBKS' in m_df_2.bowling_team.unique():
        PBKS_runs_against.append(runs_2)
        PBKS_balls_against.append(balls_2)
    if 'RCB' in m_df_2.bowling_team.unique():
        RCB_runs_against.append(runs_2)
        RCB_balls_against.append(balls_2)
    if 'RR' in m_df_2.bowling_team.unique():
        RR_runs_against.append(runs_2)
        RR_balls_against.append(balls_2)
    if 'SRH' in m_df_2.bowling_team.unique():
        SRH_runs_against.append(runs_2)
        SRH_balls_against.append(balls_2)

CSK_runs_for = sum(CSK_runs_for)
CSK_balls_for = sum(CSK_balls_for)
CSK_runs_against = sum(CSK_runs_against)
CSK_balls_against = sum(CSK_balls_against)
DC_runs_for = sum(DC_runs_for)
DC_balls_for = sum(DC_balls_for)
DC_runs_against = sum(DC_runs_against)
DC_balls_against = sum(DC_balls_against)
GT_runs_for = sum(GT_runs_for)
GT_balls_for = sum(GT_balls_for)
GT_runs_against = sum(GT_runs_against)
GT_balls_against = sum(GT_balls_against)
KKR_runs_for = sum(KKR_runs_for)
KKR_balls_for = sum(KKR_balls_for)
KKR_runs_against = sum(KKR_runs_against)
KKR_balls_against = sum(KKR_balls_against)
LSG_runs_for = sum(LSG_runs_for)
LSG_balls_for = sum(LSG_balls_for)
LSG_runs_against = sum(LSG_runs_against)
LSG_balls_against = sum(LSG_balls_against)
MI_runs_for = sum(MI_runs_for)
MI_balls_for = sum(MI_balls_for)
MI_runs_against = sum(MI_runs_against)
MI_balls_against = sum(MI_balls_against)
PBKS_runs_for = sum(PBKS_runs_for)
PBKS_balls_for = sum(PBKS_balls_for)
PBKS_runs_against = sum(PBKS_runs_against)
PBKS_balls_against = sum(PBKS_balls_against)
RCB_runs_for = sum(RCB_runs_for)
RCB_balls_for = sum(RCB_balls_for)
RCB_runs_against = sum(RCB_runs_against)
RCB_balls_against = sum(RCB_balls_against)
RR_runs_for = sum(RR_runs_for)
RR_balls_for = sum(RR_balls_for)
RR_runs_against = sum(RR_runs_against)
RR_balls_against = sum(RR_balls_against)
SRH_runs_for = sum(SRH_runs_for)
SRH_balls_for = sum(SRH_balls_for)
SRH_runs_against = sum(SRH_runs_against)
SRH_balls_against = sum(SRH_balls_against)


teams = ["CSK", "DC", "GT","KKR","LSG","MI","PBKS","RCB","RR","SRH"]
pts_table_p2 = pd.DataFrame()
pts_table_p2['team'] = np.array(teams)
pts_table_p2['matches_played'] = 0

for index, row in pts_table_p2.iterrows():
    team = row['team']
    matches_played = df_all[df_all.batting_team==team].match_id.nunique()
    
    pts_table_p2.at[index, 'matches_played'] = matches_played

runs_for = pd.Series([CSK_runs_for, DC_runs_for, GT_runs_for, KKR_runs_for, LSG_runs_for,
           MI_runs_for, PBKS_runs_for, RCB_runs_for, RR_runs_for, SRH_runs_for])

balls_for = pd.Series([CSK_balls_for, DC_balls_for, GT_balls_for, KKR_balls_for, LSG_balls_for,
           MI_balls_for, PBKS_balls_for, RCB_balls_for, RR_balls_for, SRH_balls_for])

runs_against = pd.Series([CSK_runs_against, DC_runs_against, GT_runs_against, KKR_runs_against, LSG_runs_against,
           MI_runs_against, PBKS_runs_against, RCB_runs_against, RR_runs_against, SRH_runs_against])

balls_against = pd.Series([CSK_balls_against, DC_balls_against, GT_balls_against, KKR_balls_against, LSG_balls_against,
           MI_balls_against, PBKS_balls_against, RCB_balls_against, RR_balls_against, SRH_balls_against])

pts_table_p2['runs_for'] = runs_for
pts_table_p2['balls_for'] = balls_for

pts_table_p2['runs_against'] = runs_against
pts_table_p2['balls_against'] = balls_against

pts_table_p2['NRR'] = (6*pts_table_p2['runs_for']/pts_table_p2['balls_for']) - \
                                6*pts_table_p2['runs_against']/pts_table_p2['balls_against']


pts_table = pd.merge(left=pts_table, right=pts_table_p2, on='team', how='outer')
pts_table.fillna(0, inplace=True)
pts_table['points'] = pts_table['points'].astype(int)

pts_table = pts_table.sort_values(by=['points','NRR'], ascending=False).reset_index(drop=True)

# In[ ]:




