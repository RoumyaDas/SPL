#!/usr/bin/env python
# coding: utf-8

# In[17]:


import pandas as pd
import glob
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import random

import warnings
warnings.filterwarnings('ignore')


# In[18]:


df_sim_1 = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_01/Stats/df_all_round_sim.csv')
df_sim_2 = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/df_all_round_sim.csv')

#df_sim_1 = pd.read_csv('D:/Downloads/df_all_round_sim_01.csv')
#df_sim_2 = pd.read_csv('D:/Downloads/df_all_round_sim_02.csv')

df_all = pd.concat([df_sim_1,df_sim_2[df_sim_1.columns]],axis=0).reset_index(drop=True)
#df_all = df_sim_1


# In[19]:


df_exp = df_all.copy()


# ## bowling

# #ideas ::

# In[20]:


def bowler_ranking(df_exp):

    # <!-- **1. Wicket Impact Index (WII)**

    # Assign weights to wickets

    # Top-order (positions 1–3): 1.2×

    # Middle-order (4–6): 1.0×

    # Tail (7+): 0.8×

    # WII = weighted_wickets / overs -->

    df_exp['order_batter_striker'] = df_exp['striker_batting_position'].apply(lambda x: 'top' if x<=3 else 'low' if x>=7 else 'middle')
    df_exp['order_batter_non_striker'] = df_exp['non_striker_batting_position'].apply(lambda x: 'top' if x<=3 else 'low' if x>=7 else 'middle')

    str_out_idx = (df_exp['player_dismissed'] == df_exp['striker'])
    nonstr_out_idx = (df_exp['player_dismissed'] == df_exp['non_striker'])
    df_exp['order_batter_dismissed'] = ''
    df_exp.loc[str_out_idx, 'order_batter_dismissed'] = df_exp.loc[str_out_idx, 'order_batter_striker']
    df_exp.loc[nonstr_out_idx, 'order_batter_dismissed'] = df_exp.loc[str_out_idx, 'order_batter_non_striker']

    #.sample(2)



    order_wkts = pd.pivot_table(data=df_exp[df_exp['isBowlerWicket']==1], index='bowler', columns='order_batter_dismissed', 
                            values='isBowlerWicket', aggfunc='sum').reset_index().fillna(0)

    order_wkts['wtd_wkts'] = order_wkts['top']*1.2 + order_wkts['middle']*1.0 + order_wkts['low']*0.8
    order_wkts['wtd_wkts'] = order_wkts['wtd_wkts'].astype(float)
    balls_bowl = df_exp.groupby('bowler')['islegal'].sum().reset_index()
    matches_bowl = df_exp.groupby('bowler')['match_id'].nunique().reset_index()

    order_wkts = order_wkts.merge(balls_bowl, on='bowler', how='outer')
    order_wkts = order_wkts.merge(matches_bowl, on='bowler', how='outer')
    order_wkts['WII'] = 6*order_wkts['wtd_wkts']/order_wkts['islegal']

    WII_df = order_wkts[['bowler','islegal','match_id','WII']]

    # **2.  Dot Pressure Index (DPI)**

    # Captures ability to build pressure through dot balls.

    # DPI = (Dot Balls / Balls Bowled) * (1 + 0.05 * Successive Dot Balls)

    # Step 1: Create issuccessivedot using dot_group logic
    def mark_streaks(group):
        group['dot_group'] = (group['isDotforbowler'] != 1).cumsum()
        group['dot_streak'] = group.groupby('dot_group').cumcount() + 1
        group['issuccessivedot'] = group.apply(lambda x: x['dot_streak'] if x['isDotforbowler'] == 1 else 0, axis=1)
        return group

    # Step 2: Compute required stats
    def count_streaks(group):
        # Keep only dot balls
        dot_only = group[group['isDotforbowler'] == 1].copy()
        # Detect the end of each streak
        dot_only['streak_break'] = (dot_only['dot_group'] != dot_only['dot_group'].shift(-1)).astype(int)
        # Identify streak end rows
        streak_ends = dot_only[dot_only['streak_break'] == 1]
        # Filter streaks of length >= 2
        valid_streaks = streak_ends[streak_ends['issuccessivedot'] >= 2]
        # Count of streaks and total dot balls in those
        num_streaks = len(valid_streaks)
        total_dots_in_streaks = valid_streaks['issuccessivedot'].sum()
        return pd.Series({
            'successive_dot_streaks': num_streaks,
            'dot_balls_in_streaks': total_dots_in_streaks
        })

    # Step 1: Track dot streaks per (match_id, bowler)
    def extract_streak_stats(group):
        dots = group['isDotforbowler'].values
        streaks = []
        streak_len = 0

        for val in dots:
            if val == 1:
                streak_len += 1
            else:
                if streak_len >= 2:
                    streaks.append(streak_len)
                streak_len = 0
        # Check for trailing streak
        if streak_len >= 2:
            streaks.append(streak_len)

        return pd.Series({
            'successive_dot_streaks': len(streaks),
            'dot_balls_in_streaks': sum(streaks)
        })

    #df_exp = df_exp.groupby(['match_id', 'bowler'], group_keys=False).apply(mark_streaks)
    streak_summary = df_exp.groupby(['match_id', 'bowler']).apply(extract_streak_stats).reset_index()
    streak_bowl = streak_summary.groupby('bowler')['dot_balls_in_streaks'].sum().reset_index()
    balls_bowl = df_exp.groupby('bowler')[['islegal','isDotforbowler']].sum().reset_index()

    streak_bowl = streak_bowl.merge(balls_bowl, on='bowler', how='outer')
    streak_bowl['DPI'] = (streak_bowl['isDotforbowler'] / streak_bowl['islegal']) * (1 + 0.05 * streak_bowl['dot_balls_in_streaks'])

    DPI_df = streak_bowl[['bowler','DPI']]



    # **3. Clutch Over Index (COI)**

    # Measures performance in high-stakes overs:

    # Powerplay: bonus if <6 ER

    # Death overs (17-20): bonus if <8 ER or take wickets

    # COI = Sum of (bonus_overs) / total_overs_bowled

    df_exp['over'] = df_exp['legal_balls_bowled'].apply(lambda x: x//6 if x%6==0 else 1+x//6)
    df_exp.loc[df_exp['islegal']==0,'over'] = np.nan

    df_exp['over'].fillna(method='bfill', inplace=True)
    df_exp['over'] = df_exp['over'].astype(int)

    df_exp['phase'] = df_exp['over'].apply(lambda x: 'pp' if x<=6 else 'death' if x>=16 else 'middle')

    phase_bowl = df_exp.groupby(['match_id','bowler','phase','over'])[['runs_conceeded','islegal','isBowlerWicket']].sum().reset_index()
    phase_bowl['bonus_pt'] = phase_bowl[['phase','islegal','runs_conceeded','isBowlerWicket']].apply(
                                                        lambda x: 2 if (x[0]=='pp' and x[1]==6 and x[2]<=7 and x[3]>=1)
                                                             else 2 if (x[0]=='death' and x[1]==6 and x[2]<=8 and x[3]>=1)
                                                             else 1 if (x[0]=='pp' and x[1]==6 and x[2]<=7)
                                                             else 1 if (x[0]=='death' and x[1]==6 and x[2]<=8)
                                                             else 0,
                                                        axis=1
    )

    phase_ball = phase_bowl.groupby('bowler')[['bonus_pt','islegal']].sum().reset_index()
    phase_ball['COI'] = 6*phase_ball['bonus_pt']/phase_ball['islegal']

    COI_df = phase_ball[['bowler','COI']]



    # **4. Bowling Efficiency Rating (BER)**

    # Composite of economy, wickets, and dot%

    # Normalize each metric and combine:

    # BER = 0.4*normalized_wickets + 0.3*normalized_dot% + 0.3*(1 - normalized_economy)

    wkt_bowler = df_exp.groupby(['match_id','bowler'])['isBowlerWicket'].sum().reset_index()
    wkt_match = df_exp.groupby('match_id')['isBowlerWicket'].sum().reset_index()
    bowlers_match = df_exp.groupby('match_id')['bowler'].nunique().reset_index()

    wkt_bowl = wkt_bowler.groupby('match_id')['isBowlerWicket'].std().reset_index()
    wkt_bowl.columns = ['match_id','wkts_sd']

    wkt_match = wkt_match.merge(bowlers_match, on='match_id', how='left')
    wkt_match = wkt_match.merge(wkt_bowl, on='match_id', how='left')
    wkt_match['wkts_mean'] = wkt_match['isBowlerWicket']/wkt_match['bowler']

    wkt_bowler = wkt_bowler.merge(wkt_match[['match_id','wkts_mean','wkts_sd']], on='match_id', how='left')

    wkt_bowler['norm_wkt'] = np.where(wkt_bowler['wkts_sd']>0, (wkt_bowler['isBowlerWicket']-wkt_bowler['wkts_mean'])/wkt_bowler['wkts_sd'],
                                     0)

    wkt_bowler = wkt_bowler.groupby('bowler')['norm_wkt'].median().reset_index() ###########

    #wkt_bowler

    dot_bowler = df_exp.groupby(['match_id','bowler'])[['isDotforbowler','islegal']].sum().reset_index()
    dot_bowler['dot_prp'] = dot_bowler['isDotforbowler']/dot_bowler['islegal']

    dot_match = df_exp.groupby('match_id')[['isDotforbowler','islegal']].sum().reset_index()
    dot_match['dot_prp'] = dot_match['isDotforbowler']/dot_match['islegal']

    bowlers_match = df_exp.groupby('match_id')['bowler'].nunique().reset_index()

    dot_bowl_sd = dot_bowler.groupby('match_id')['dot_prp'].std().reset_index()
    dot_bowl_sd.columns = ['match_id','dot_sd']

    dot_bowl = dot_bowler.groupby('match_id')['dot_prp'].mean().reset_index()
    dot_bowl.columns = ['match_id','dot_mean']

    dot_bowl = dot_bowl.merge(dot_bowl_sd, on='match_id', how='inner')

    dot_bowler = dot_bowler.merge(dot_bowl[['match_id','dot_mean','dot_sd']], on='match_id', how='left')

    dot_bowler['norm_dot_prp'] = np.where(dot_bowler['dot_sd']>0, (dot_bowler['dot_prp']-dot_bowler['dot_mean'])/dot_bowler['dot_sd'],
                                     0)

    dot_bowler = dot_bowler.groupby('bowler')['norm_dot_prp'].median().reset_index() #########

    #dot_bowler

    eco_bowler = df_exp.groupby(['match_id','bowler'])[['runs_conceeded','islegal']].sum().reset_index()
    eco_bowler['eco'] = eco_bowler['runs_conceeded']/eco_bowler['islegal']

    eco_match = df_exp.groupby('match_id')[['runs_conceeded','islegal']].sum().reset_index()
    eco_match['dot_prp'] = eco_match['runs_conceeded']/eco_match['islegal']

    eco_bowl_sd = eco_bowler.groupby('match_id')['eco'].std().reset_index()
    eco_bowl_sd.columns = ['match_id','eco_sd']

    eco_bowl = eco_bowler.groupby('match_id')['eco'].mean().reset_index()
    eco_bowl.columns = ['match_id','eco_mean']

    eco_bowl = eco_bowl.merge(eco_bowl_sd, on='match_id', how='inner')

    eco_bowler = eco_bowler.merge(eco_bowl[['match_id','eco_mean','eco_sd']], on='match_id', how='left')

    eco_bowler['norm_eco'] = np.where(eco_bowler['eco_sd']>0, (-eco_bowler['eco']+eco_bowler['eco_mean'])/eco_bowler['eco_sd'],
                                     0)

    eco_bowler = eco_bowler.groupby('bowler')['norm_eco'].median().reset_index() ############

    #eco_bowler

    BER_df = wkt_bowler.merge(dot_bowler.merge(eco_bowler,on='bowler',how='outer'), on='bowler',how='outer')
    BER_df['BER'] = 0.4*BER_df['norm_wkt']+0.3*BER_df['norm_dot_prp']+0.3*BER_df['norm_eco']

    BER_df = BER_df[['bowler','BER']]
    #BER_df.sort_values('BER', ascending=False)










    # **5. Match Impact Quotient for Bowlers (MIQ-B)**

    # Value of a spell based on:

    # Wickets * importance (based on match phase)

    # Economy * deviation from match average

    # MIQ-B = (Wickets * weight) + (Match ER - Bowler ER) * overs

    phase_wkt = df_exp.groupby(['match_id','bowler','phase'])['isBowlerWicket'].sum().reset_index()
    phase_wkt['true_wkt'] = phase_wkt[['isBowlerWicket','phase']].fillna(0).apply(lambda x: 1.25*x[0] if x[1]=='pp' 
                                                                        else 1.50*x[0] if x[1]=='death'
                                                                        else x[0], axis=1)

    phase_wkt = phase_wkt.groupby(['match_id','bowler'])['true_wkt'].sum().reset_index()


    match_bowl_er = df_exp.groupby(['match_id','bowler'])[['runs_conceeded','islegal']].sum().reset_index()
    match_bowl_er['ER'] = 6*match_bowl_er['runs_conceeded']/match_bowl_er['islegal']
    match_er = df_exp.groupby('match_id')[['runs_conceeded','islegal']].sum().reset_index()
    match_er['match_ER'] = 6*match_er['runs_conceeded']/match_er['islegal']

    er_bowl = match_bowl_er.merge(match_er[['match_id','match_ER']], on='match_id', how='left')

    er_bowl['er_bonus'] = (er_bowl['match_ER']-er_bowl['ER'])*er_bowl['islegal']/6
    phase_wkt_er = er_bowl.merge(phase_wkt, on=['match_id','bowler'], how='outer')
    phase_wkt_er['MIQ_B'] = phase_wkt_er['er_bonus']+phase_wkt_er['true_wkt']

    wkt_er_ball = phase_wkt_er.groupby('bowler')['MIQ_B'].mean().reset_index() ##########
    matches_bowl = df_exp.groupby('bowler')['match_id'].nunique().reset_index()

    wkt_er_ball = wkt_er_ball.merge(matches_bowl, on='bowler', how='outer')

    MIQ_df = wkt_er_ball[['bowler','MIQ_B']]



    # **6. Expected Runs Saved (ERS)**

    # Estimate what an average bowler would have conceded in same overs (e.g., by match avg ER)
    # ERS = (Expected - Actual Runs Conceded)

    inn_er = df_exp.groupby(['match_id','innings'])[['runs_conceeded','islegal']].sum().reset_index()
    inn_er['inn_ER'] = 6*inn_er['runs_conceeded']/inn_er['islegal']

    bowl_er = df_exp.groupby(['match_id','innings','bowler'])[['runs_conceeded','islegal']].sum().reset_index()
    bowl_er['ER'] = 6*bowl_er['runs_conceeded']/bowl_er['islegal']

    bowl_er = bowl_er.merge(inn_er[['match_id','innings','inn_ER']], on=['match_id','innings'], how='inner')
    bowl_er['ERS'] = bowl_er['inn_ER']*bowl_er['islegal']/6 - bowl_er['runs_conceeded']

    bowl_er = bowl_er.groupby('bowler')['ERS'].mean().reset_index() #################
    matches_bowl = df_exp.groupby('bowler')['match_id'].nunique().reset_index()

    bowl_er = bowl_er.merge(matches_bowl, on='bowler', how='outer')

    ERS_df = bowl_er[['bowler','ERS']]



    # **7. Choke Rate**

    # % of overs where bowler conceded <6 runs and took ≥1 wicket.

    over_ball = df_exp.groupby(['match_id','bowler','over'])[['runs_conceeded','islegal','isBowlerWicket']].sum().reset_index()
    over_ball['choke_bonus'] = over_ball[['islegal','runs_conceeded','isBowlerWicket']].apply(
                                                        lambda x: 1 if (x[0]==6 and x[1]<=7 and x[2]>=1)
                                                             else 0,
                                                        axis=1
    )

    over_ball = over_ball.groupby('bowler')[['choke_bonus','islegal']].sum().reset_index()
    over_ball['Choke_Rate'] = 6*over_ball['choke_bonus']/over_ball['islegal']

    Choke_Rate_df = over_ball[['bowler','Choke_Rate']]



    # **8. Partnership-breaker index (PBI)**

    # mean of #30+ partnerships broken in a game

    df_exp.loc[df_exp.isWicket==1, 'partnership_runs'] = np.nan

    df_exp['partnership_runs'] = df_exp['partnership_runs'].fillna(method='ffill')
    df_exp.loc[df_exp.isWicket==1, 'partnership_runs'] = df_exp.loc[df_exp.isWicket==1, 'partnership_runs']+                                                df_exp.loc[df_exp.isWicket==1, 'total_runs']

    p_count = df_exp[df_exp['partnership_runs']>=30].groupby(['bowler','match_id'])['isBowlerWicket'].sum().reset_index()
    w_count = df_exp.groupby(['bowler','match_id'])['isBowlerWicket'].sum().reset_index()
    p_count.columns = ['bowler','match_id','f_wkts']
    w_count.columns = ['bowler','match_id','wkts']

    p_count = p_count.merge(w_count, on=['match_id','bowler'], how='right').fillna(0)

    PBI_df = p_count.groupby('bowler')['f_wkts'].mean().reset_index()
    PBI_df.columns = ['bowler','PBI']
    PBI_df['PBI'] = PBI_df['PBI']*2.5
    #PBI_df.sort_values('PBI',ascending=False)
    
    # **bonus. Defense-Capability Index (DCI)**

    # relative Eco when Reqd-RR<=8

    eco_rr = df_exp[df_exp['reqd_run_rate']<=8].groupby('bowler')[['runs_conceeded','islegal']].sum().reset_index()
    eco_rr = eco_rr[eco_rr['islegal']>=25]
    eco_rr['Eco'] = 6*eco_rr['runs_conceeded']/eco_rr['islegal']
    eco_rr['DCI'] = eco_rr['Eco'].median()/eco_rr['Eco']
    
    DCI_df = eco_rr[['bowler','DCI']]
    
    #PBI_df.sort_values('PBI',ascending=False)



    # **9. team played for**

    # team played for in the latest season

    df_exp_new = df_exp[df_exp['season']==int(df_exp['season'].unique()[-1])]
    team = df_exp_new.groupby('bowler')['bowling_team'].unique().reset_index()
    team['team'] = team['bowling_team'].apply(lambda x: x[0])

    team_df = team[['bowler','team']]

    # **10. Count_of_wkts**

    # number of wkts taken for each bowler

    W_df = df_exp.groupby('bowler')['isBowlerWicket'].sum().reset_index()
    W_df.columns = ['bowler','wkt_pt']
    W_df['wkt_pt'] = W_df['wkt_pt']/5



    # **11. Recent Form**

    # number of wkts*(24/Bo.SR)*(Eco median/Bo.Eco) in last 3outings

    players_list = df_exp['bowler'].unique().tolist()
    bowl_pl = df_exp[df_exp.bowler.isin(players_list)]
    bowler_match_id = {}

    # Collect last 3 match IDs for each bowler in bowl_pl
    for bowler in bowl_pl.bowler.unique():
        matches = bowl_pl[bowl_pl.bowler == bowler].match_id.unique()[-3:].tolist()
        bowler_match_id[bowler] = matches

    df_bowl = pd.DataFrame()

    for bowler_name in players_list:
        last_3_matches = bowler_match_id.get(bowler_name, [1])
        df_sub = bowl_pl[(bowl_pl.bowler==bowler_name)&(bowl_pl.match_id.isin(last_3_matches))]
        if df_sub.shape[0]>0:
            df_sub.reset_index(drop=True, inplace=True)
            df_bowl = df_bowl.append(df_sub)
        else:
            continue


    df_bowl['runs_conceeded'] = df_bowl['runs_off_bat']+df_bowl['wides']+df_bowl['noballs']

    bowler_stats_form = df_bowl.groupby('bowler').agg(

    num_innings = ('match_id','nunique'),
        runs = ('runs_conceeded','sum'),
        balls = ('islegal' ,'sum'),
        wkts = ('isBowlerWicket','sum')

    ).reset_index()

    bowler_stats_form['bowl_sr'] = bowler_stats_form['balls']/bowler_stats_form['wkts']
    bowler_stats_form['bowl_eco'] = 6*bowler_stats_form['runs']/bowler_stats_form['balls']
    bowler_stats_form['bowl_eco'] = bowler_stats_form['bowl_eco'].fillna(0)


    bowler_stats_form['bowl_sr'] = bowler_stats_form.apply(
        lambda row: row['runs'] if np.isinf(row['bowl_sr']) else row['bowl_sr'], axis=1
    )

    eco_med = bowler_stats_form['bowl_eco'].median()

    bowler_stats_form['recent_form'] = bowler_stats_form['wkts']*(24/bowler_stats_form['bowl_sr'])*(eco_med/bowler_stats_form['bowl_eco'])
    bowler_stats_form['recent_form'] = (bowler_stats_form['recent_form']-bowler_stats_form['recent_form'].median())/bowler_stats_form['recent_form'].std()

    RF_df = bowler_stats_form[['bowler','recent_form']]

    #RF_df.sort_values('recent_form',ascending=False)

    # **MERGING ALL**

    df_list = [team_df,WII_df,DPI_df,COI_df,BER_df,MIQ_df,ERS_df,Choke_Rate_df,PBI_df,RF_df,DCI_df,W_df]

    all_df = team_df
    for df in df_list[1:]:

        #df[df.columns[1]] = df[df.columns[1]]/(df[df.columns[1]].max()-df[df.columns[1]].min())
        all_df = all_df.merge(df, on='bowler', how='outer')

    all_df['score'] = all_df[all_df.columns[4:].values].sum(axis=1)

    all_df = all_df[(all_df['islegal']>=100)&(all_df['match_id']>=5)][~(all_df['team'].isna())]                                .sort_values('score', ascending=False).reset_index(drop=True)

    all_df['rank'] = all_df.index+1

    return all_df


# In[ ]:





# ## comparison function

# In[21]:


def compare_bowler_ranks(old_df, new_df):
    old_df = old_df.copy()
    new_df = new_df.copy()
    
    old_df['rank'] = old_df['rank'].astype(int)
    new_df['rank'] = new_df['rank'].astype(int)

    # 1. New entries
    old_bowlers = set(old_df['bowler'])
    new_bowlers = set(new_df['bowler'])
    new_entries = new_bowlers - old_bowlers
    if new_entries:
        print("🔹 New Entries:")
        print(new_df[new_df['bowler'].isin(new_entries)].sort_values(by='rank')[['bowler', 'rank']])
    else:
        print("🔹 No new entries.")
    print()
    print('---'*10)
    print()

    # Merge for comparison
    merged = pd.merge(old_df, new_df, on='bowler', how='inner', suffixes=('_old', '_new'))

    # 2. Major rank changes (±5 or more)
    merged['rank_change'] = merged['rank_old'] - merged['rank_new']
    major_changes = merged[(merged['rank_change'].abs() >= 5) & (merged['rank_new'] <= 20)]

    if not major_changes.empty:
        print("🔹 Major Rank Changes (±5 or more):")
        print(major_changes[['bowler', 'rank_old', 'rank_new', 'rank_change']].sort_values(by='rank_change', key=abs))
    else:
        print("🔹 No major rank changes.")
    print()
    print('---'*10)
    print()

    # 3. Moved out of Top 10
    top10_old = old_df.nsmallest(10, 'rank')['bowler']
    top10_new = new_df.nsmallest(10, 'rank')['bowler']
    
    moved_out = set(top10_old) - set(top10_new)
    if moved_out:
        print("🔹 Moved out of Top 10:")
        moved_out_df = pd.merge(
            old_df[old_df['bowler'].isin(moved_out)],
            new_df[['bowler', 'rank']].rename(columns={'rank': 'rank_new'}),
            on='bowler',
            how='left'
        )
        print(moved_out_df[['bowler', 'rank', 'rank_new']].rename(columns={'rank': 'rank_old'}).sort_values(by='rank_old'))
    else:
        print("🔹 No one moved out of Top 10.")
    print()
    print('---'*10)
    print()
    
    # 4. Newly entered Top 10
    moved_in = set(top10_new) - set(top10_old)
    if moved_in:
        print("🔹 Newly Entered Top 10:")
        moved_in_df = pd.merge(
            new_df[new_df['bowler'].isin(moved_in)],
            old_df[['bowler', 'rank']].rename(columns={'rank': 'rank_old'}),
            on='bowler',
            how='left'
        )
        print(moved_in_df[['bowler', 'rank', 'rank_old']].rename(columns={'rank': 'rank_new'}).sort_values(by='rank_new'))
    else:
        print("🔹 No new entries into Top 10.")
    print()
    print('---'*10)
    print()


# ## running the function

# In[22]:


df_old = df_exp[~(df_exp['match_id'].isin(df_exp['match_id'].unique()[-2:].tolist()))]

all_df = bowler_ranking(df_exp)
all_df_old = bowler_ranking(df_old)
all_df['score'] = all_df['score'].apply(lambda x: min(x,24+random.random()))
all_df.to_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/Stats/bowler_ranking.csv', index=None)

all_df = all_df[['bowler','rank','score']]
all_df_old = all_df_old[['bowler','rank','score']]


# In[23]:


compare_bowler_ranks(all_df_old, all_df)


# In[8]:


#all_df.to_csv()


# In[ ]:





# In[ ]:




