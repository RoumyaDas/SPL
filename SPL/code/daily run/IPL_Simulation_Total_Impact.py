#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import glob
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import warnings
from contextlib import redirect_stdout

# Ignore all warnings
warnings.filterwarnings("ignore")


# In[2]:


df_a = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_03/df_all_round_sim.csv')
m_m = df_a.match_id.unique()[-1]
#m_m = 'S03M065'
df = df_a[df_a.match_id==m_m]


# In[ ]:





# In[3]:


def info_calc(df):

    # Pivot table for 'batting_team' without 'phase'
    batting_team_pivot = pd.pivot_table(
        df, 
        index=['match_id'],
        columns='innings', 
        values='batting_team',
        aggfunc=unique_value_without_nan
    ).reset_index()

    # Pivot table for the rest of the columns with 'phase'
    other_pivot = pd.pivot_table(
        df, 
        index=['match_id'],
        columns=['innings'], 
        values=['runs_off_bat','total_runs','isDotforBatter','isFour','isSix','islegal', 'isWicket'],
        aggfunc=np.sum
    ).reset_index()

    # Merge the two pivot tables on 'match_id'
    info_df = batting_team_pivot.merge(other_pivot, on='match_id')

    info_df.columns = ['match_id','team_1_bat','team_2_bat','inn1_dots','inn2_dots','inn1_4s','inn2_4s',
                      'inn1_6s','inn2_6s','inn1_wkts','inn2_wkts','inn1_balls','inn2_balls',
                      'inn1_runs_bat','inn2_runs_bat',
                  'inn1_runs_total','inn2_runs_total']

    
    info_df['winner'] = None
    info_df['win_fl_inn1'] = None
    info_df['win_fl_inn2'] = None
    info_df['win_margin_runs'] = None
    info_df['win_margin_wkts'] = None
    
    for index,row in info_df.iterrows():
        inn1_total = row['inn1_runs_total']
        inn2_total = row['inn2_runs_total']
        
        if inn2_total>inn1_total:
            info_df.at[index, 'winner'] = row['team_2_bat']
            info_df.at[index, 'win_fl_inn1'] = 0
            info_df.at[index, 'win_fl_inn2'] = 1
            info_df.at[index, 'win_margin_wkts'] = 10-row['inn2_wkts']
            
        elif inn1_total>inn2_total:
            info_df.at[index, 'winner'] = row['team_1_bat']
            info_df.at[index, 'win_fl_inn1'] = 1
            info_df.at[index, 'win_fl_inn2'] = 0
            info_df.at[index, 'win_margin_runs'] = inn1_total-inn2_total
        
    return info_df


# In[4]:


def info_calc_conditional(df):

    # Pivot table for the rest of the columns with 'phase'
    info_df = pd.pivot_table(
        df, 
        index=['match_id'],
        columns=['innings'], 
        values=['runs_off_bat','total_runs','isDotforBatter','isFour','isSix','islegal', 'isWicket'],
        aggfunc=np.sum
    ).reset_index()

    info_df.columns = ['match_id','phase_dots','phase_4s',
                      'phase_6s','phase_wkts','phase_balls',
                      'phase_runs_bat','phase_runs_total']

    
    return info_df


# In[5]:


def other_derived_cols(df):
    
    df['isno'] = (df.noballs>0)
    df['iswide'] = (df.wides>0)

    df['is_faced_by_batter'] = (df.islegal==1) | (df.isno==True)
    
    #df['is_faced_by_batter_cum'] = 
    
    # Calculate the cumulative sum for 'islegal' within each group of 'match_id' and 'innings'
    df['is_faced_by_batter_cum'] = df.groupby(['match_id', 'innings'])['is_faced_by_batter'].cumsum()

    # Reset the cumulative sum for each new 'match_id' or 'innings'
    df.loc[df['innings'].diff().eq(1), 'is_faced_by_batter_cum'] = df['is_faced_by_batter']

    # Reset the cumulative sum for the first row of each 'match_id'
    df.loc[df['match_id'].ne(df['match_id'].shift(1)), 'is_faced_by_batter_cum'] = df['is_faced_by_batter']

    # Optional: If you want to fill NaN values in 'legal_balls_bowled' with 0
    df['is_faced_by_batter_cum'] = df['is_faced_by_batter_cum'].fillna(0)
    
    df['is_faced_by_batter_cum'].replace(True, 1, inplace=True)
    df['is_faced_by_batter_cum'].replace(False, 0, inplace=True)
    
    # Reset the DataFrame index
    df.reset_index(drop=True, inplace=True)
    
    
    ################################################################
    
    # Initialize the 'last_fow_run_rate' column with NaN
    df['last_fow_run_rate'] = np.nan
    df['last_fow'] = np.nan
    df['last_fow_balls'] = np.nan
    df['last_fow_balls_faced'] = np.nan

    # Initialize variables to keep track of the last wickets down, innings, and match_id
    last_wickets_down = None
    current_innings = None
    current_match_id = None
    last_fow_run_rate = None
    last_fow = None
    last_fow_balls = None

    # Iterate through the DataFrame rows
    for index, row in df.iterrows():
        match_id = row['match_id']
        innings = row['innings']
        wickets_down = row['wickets_down']
        run_rate = row['run_rate']
        runs = row['runs_scored']
        balls = row['legal_balls_bowled']
        balls_faced = row['is_faced_by_batter_cum']

        # Check if innings or match_id has changed
        if innings != current_innings or match_id != current_match_id:
            last_fow_run_rate = None  # Reset last_fow_run_rate to None
            last_fow = None
            last_fow_balls = None
            last_fow_balls_faced = None

        # Update the current 'wickets_down', 'innings', 'match_id'
        current_wickets_down = wickets_down
        current_innings = innings
        current_match_id = match_id

        # Update the 'last_fow_run_rate' column if 'wickets_down' changes or becomes 1
        if (wickets_down != last_wickets_down) and (wickets_down != 0):
            last_fow_run_rate = run_rate
            df.at[index, 'last_fow_run_rate'] = run_rate

            last_fow_run = runs
            df.at[index, 'last_fow'] = last_fow_run

            last_fow_balls = balls
            df.at[index, 'last_fow_balls'] = last_fow_balls
            
            last_fow_balls_faced = balls_faced
            df.at[index, 'last_fow_balls_faced'] = last_fow_balls_faced



        # Update 'last_fow_run_rate' immediately when 'wickets_down' becomes 1 or changes
        if (last_wickets_down != 0 and type(last_wickets_down)!=None 
                                 and wickets_down != last_wickets_down): #wickets_down == 1 or 
            df.at[index, 'last_fow_run_rate'] = run_rate
            last_fow_run_rate = run_rate

            last_fow_run = runs
            df.at[index, 'last_fow'] = last_fow_run

            last_fow_balls = balls
            df.at[index, 'last_fow_balls'] = last_fow_balls
            
            last_fow_balls_faced = balls_faced
            df.at[index, 'last_fow_balls_faced'] = last_fow_balls_faced



        if wickets_down == 0:
            last_fow_run_rate = None
            df.at[index, 'last_fow_run_rate'] = last_fow_run_rate

            last_fow_run = None
            df.at[index, 'last_fow'] = last_fow_run

            last_fow_balls = None
            df.at[index, 'last_fow_balls'] = last_fow_balls
            
            last_fow_balls_faced = None
            df.at[index, 'last_fow_balls_faced'] = last_fow_balls_faced


        # Update 'last_wickets_down'
        last_wickets_down = wickets_down


    ####### need to forward fill

    # Reset the DataFrame index
    df.reset_index(drop=True, inplace=True)

    cols_ffill = ['last_fow', 'last_fow_run_rate', 'last_fow_balls', 'last_fow_balls_faced']

    for match in df.match_id.unique():
        for inning in df[df.match_id == match].innings.unique():
            for column in cols_ffill:
                mask = (df.match_id == match) & (df.innings == inning)
                df.loc[mask, column] = df.loc[mask, column].fillna(method='ffill')


    df.reset_index(drop=True, inplace=True)

    
    #######################################################

    partnership_runs = []
    for match in df.match_id.unique():
        for inning in df[df.match_id==match].innings.unique():
            partnership_runs.append(df[df.match_id==match][df.innings==inning]['runs_scored'].iloc[0])
            for row in range(1, len(df[df.match_id==match][df.innings==inning])):
                previous_fow = df[df.match_id==match][df.innings==inning]['last_fow'].iloc[row-1]
                to_append = df[df.match_id==match][df.innings==inning]['runs_scored'].iloc[row] -                                             (previous_fow if pd.notna(previous_fow) else 0)
                partnership_runs.append(to_append)

    df['partnership_runs'] = partnership_runs
    
    # Reset the DataFrame index
    df.reset_index(drop=True, inplace=True)
    
    partnership_balls = []
    for match in df.match_id.unique():
        for inning in df[df.match_id==match].innings.unique():
            partnership_balls.append(df[df.match_id==match][df.innings==inning]['is_faced_by_batter_cum'].iloc[0])
            for row in range(1, len(df[df.match_id==match][df.innings==inning])):
                previous_fow = df[df.match_id==match][df.innings==inning]['last_fow_balls_faced'].iloc[row-1]
                to_append = df[df.match_id==match][df.innings==inning]['is_faced_by_batter_cum'].iloc[row] -                                             (previous_fow if pd.notna(previous_fow) else 0)
                partnership_balls.append(to_append)

    df['partnership_balls'] = partnership_balls
    df['partnership_balls'].replace(True, 1, inplace=True)
    
    # Reset the DataFrame index
    df.reset_index(drop=True, inplace=True)

    ### creation of striker_runs, non_striker_runs

    striker_runs = []
    non_striker_runs = []
    i = 0


    for match in df.match_id.unique():
        i = i+1
        df_part = df[df.match_id==match]
        for inning in df_part.innings.unique():
            first_loc = df_part[df_part.innings==inning].index[0]

            for row in (df_part[df_part.innings==inning].index):
                s_r = df_part[df_part.innings==inning][df_part.striker==df_part.striker.loc[row]].loc[first_loc:row]                                                        .runs_off_bat.sum()
                n_s_r = df_part[df_part.innings==inning][df_part.striker==df_part.non_striker.loc[row]].loc[first_loc:row]                                                        .runs_off_bat.sum()
                striker_runs.append(s_r)
                non_striker_runs.append(n_s_r)

    df['striker_runs'] = striker_runs
    df['non_striker_runs'] = non_striker_runs
    
    # Reset the DataFrame index
    df.reset_index(drop=True, inplace=True)

    striker_balls = []
    non_striker_balls = []
    i = 0


    for match in df.match_id.unique():
        i = i+1
        df_part = df[df.match_id==match]
        for inning in df_part.innings.unique():
            first_loc = df_part[df_part.innings==inning].index[0]

            for row in (df_part[df_part.innings==inning].index):
                s_b = df_part[df_part.innings==inning][df_part.striker==df_part.striker.loc[row]].loc[first_loc:row]                                                        .is_faced_by_batter.sum()
                n_s_b = df_part[df_part.innings==inning][df_part.striker==df_part.non_striker.loc[row]].loc[first_loc:row]                                                        .is_faced_by_batter.sum()
                striker_balls.append(s_b)
                non_striker_balls.append(n_s_b)



    df['striker_balls'] = striker_balls
    df['non_striker_balls'] = non_striker_balls

    # Reset the DataFrame index
    df.reset_index(drop=True, inplace=True)
    
    # Calculate strike rates with handling for zero balls faced
    df['striker_strike_rate'] = np.where(df['striker_balls'] > 0, 100 * df['striker_runs'] / df['striker_balls'],                                          None)
    df['non_striker_strike_rate'] = np.where(df['non_striker_balls'] > 0, 100 * df['non_striker_runs'] /                                              df['non_striker_balls'], None)

    # Reset the DataFrame index
    df.reset_index(drop=True, inplace=True)
    
    # Create a 'runs_conceded_by_bowler' column
    df['runs_conceded_by_bowler'] = df['runs_off_bat'] + df['wides'] + df['noballs']

    # Initialize lists to store the results
    bowler_runs = []
    bowler_balls = []
    bowler_wkts = []

    # Group by match_id, innings, and bowler
    grouped = df.groupby(['match_id', 'innings', 'bowler'])

    # Calculate cumulative sums within each group
    df['bowler_runs'] = grouped['runs_conceded_by_bowler'].cumsum()
    df['bowler_balls'] = grouped['islegal'].cumsum()
    df['bowler_wkts'] = grouped['isBowlerWicket'].cumsum()

    # Reset the DataFrame index
    df.reset_index(drop=True, inplace=True)

    
    # Sort the DataFrame by 'match_id', 'innings' for forward filling
    df.sort_values(by=['match_id', 'innings'], inplace=True)

    # Group by 'match_id' and 'innings' and forward-fill NaN values within each group
    df['last_fow_run_rate'] = df.groupby(['match_id', 'innings'])['last_fow_run_rate'].fillna(method='ffill')

    # Reset the DataFrame index
    df.reset_index(drop=True, inplace=True)


    #### correcting the last_fow in some cases


    # Sort the DataFrame by 'match_id', 'innings' for forward filling
    df.sort_values(by=['match_id', 'innings'], inplace=True)

    # Group by 'match_id' and 'innings' and forward-fill NaN values within each group
    df['last_fow'] = df.groupby(['match_id', 'innings'])['last_fow'].fillna(method='ffill')

    # Reset the DataFrame index
    df.reset_index(drop=True, inplace=True)


    #### creation of fours_hit, sixes_hit

    # Sort the DataFrame by 'match_id', 'innings' for forward filling
    df.sort_values(by=['start_date','match_id', 'innings'], inplace=True)

    # Group by 'match_id' and 'innings' and forward-fill NaN values within each group
    df['fours'] = df.groupby(['match_id', 'innings'])['isFour'].cumsum()
    df['sixes'] = df.groupby(['match_id', 'innings'])['isSix'].cumsum()

    # Reset the DataFrame index
    df.reset_index(drop=True, inplace=True)

    
   #--------------------------------------------------------------------------------------------------------
     
    return df


# In[6]:


def merging_match_stats_conditional(bat_stats_df):
    
    match_info_df_conditional = pd.DataFrame()
    
    for index, row in bat_stats_df.reset_index(drop=True).iterrows():
        condition_vals = np.array(bat_stats_df[condition_cols].iloc[index])
        cond_1 = (df.match_id==condition_vals[0])
        cond_2 = (df.batting_team==condition_vals[2])
        cond_3 = (df.legal_balls_bowled>=condition_vals[3])
        cond_4 = (df.legal_balls_bowled<=condition_vals[4])

        a = info_calc_conditional(df[cond_1 & cond_2 & cond_3 & cond_4].reset_index(drop=True))
        a = a.drop('match_id', axis=1)

        match_info_df_conditional = match_info_df_conditional.append(a)
    
    match_info_df_conditional.reset_index(drop=True, inplace=True)
    
    bat_stats_df_merged = pd.concat([bat_stats_df.reset_index(drop=True),match_info_df_conditional],
                                   axis=1)
    
    return bat_stats_df_merged


# In[7]:


def bat_stats(df):

    striker_groupby = ['match_id','innings','striker']


    # Group by 'match_id', 'innings', and 'striker' and apply the aggregation functions
    bat_stats = df.groupby(striker_groupby).agg(

        team = ('batting_team', unique_value_without_nan),
        opposition = ('bowling_team', unique_value_without_nan),
        batting_position= ('striker_batting_position',unique_value_without_nan), #unique_value_without_nan
        runs= ('runs_off_bat','sum'),         
        #mode_of_dismissal= ('wicket_type',unique_value_without_nan),        
        balls= ('is_faced_by_batter','sum'),

        dots= ('isDotforBatter','sum'),
        
        strike_rotations= ('isStrikeRotation','sum'),
        fours= ('isFour','sum'),
        sixes= ('isSix','sum')
    
    ).reset_index()

    bat_stats['SR'] = np.where(bat_stats['balls'] > 0, 100 * bat_stats['runs'] / bat_stats['balls'],                                              np.nan)
    
    dismissed_df = df.groupby(['match_id','innings','player_dismissed']).agg(
        mode_of_dismissal = ('wicket_type',unique_value_without_nan)
    ).reset_index()
    
    dismissed_df = dismissed_df.rename(columns={'player_dismissed':'striker'})
    
    
    bat_stats = bat_stats.merge(dismissed_df, on=['match_id','innings','striker'], how='left')
    
    bat_stats['mode_of_dismissal'] = bat_stats['mode_of_dismissal'].fillna('not out')

    #df.groupby(['match_id','innings'])['wickets_down'].unique().reset_index()#[['last_fow','last_fow']]

    fow_df = pd.pivot_table(df, index=['match_id','innings','wickets_down'], #columns=, 
                   values=['last_fow','last_fow_balls'] , aggfunc=pd.Series.unique).reset_index()
    exit_fow_df = df[df.player_dismissed.str.len()>0].groupby(['match_id','innings','player_dismissed']).last()                [['last_fow','last_fow_balls','wickets_down']].reset_index()

    exit_fow_df = exit_fow_df.rename(columns={'last_fow':'exit_point','last_fow_balls':'exit_point_balls',
                                              'player_dismissed':'striker','wickets_down':'exit_point_wickets'})

    bat_stats['wickets_down'] = bat_stats['batting_position']-2

    bat_stats = bat_stats.merge(fow_df, on=['match_id','innings','wickets_down'], how='left')

    bat_stats = bat_stats.rename(columns={'last_fow':'entry_point', 'last_fow_balls':'entry_point_balls'})

    bat_stats.drop('wickets_down', axis=1, inplace=True)

    bat_stats.entry_point.fillna(0, inplace=True)
    bat_stats.entry_point_balls.fillna(0, inplace=True)

    bat_stats = bat_stats.merge(exit_fow_df, on=['match_id','innings','striker'], how='left')

    #bat_stats.exit_point.fillna(0, inplace=True)
    #bat_stats.exit_point_balls.fillna(0, inplace=True)


    

    for index,row in bat_stats.iterrows():
        
        if ',' in str(row['mode_of_dismissal']):
            value = str(row['mode_of_dismissal']).split(',')[1].strip().replace("'",'').replace(']','')
        elif len(row['mode_of_dismissal'])>0:
            value = str(row['mode_of_dismissal']).strip()
        else:
            value = 'not out'

        bat_stats.at[index, 'mode_of_dismissal'] = value
    
    

    for index, row in bat_stats[bat_stats.exit_point.isna()].iterrows():
        match = row['match_id']
        inning = row['innings']
        exit_point = df[(df.match_id==match)&(df.innings==inning)].runs_scored.max()
        exit_point_balls = df[(df.match_id==match)&(df.innings==inning)].legal_balls_bowled.max()
        exit_point_wickets = df[(df.match_id==match)&(df.innings==inning)].wickets_down.max()

        bat_stats.at[index, 'exit_point'] = exit_point
        bat_stats.at[index, 'exit_point_balls'] = exit_point_balls
        bat_stats.at[index, 'exit_point_wickets'] = exit_point_wickets

   
    bat_stats['partnerships_part_of'] = np.nan
    
    for index, row in bat_stats.iterrows():
        wkt = row['mode_of_dismissal']
        
        if wkt!='not out':
            partnerships = row['exit_point_wickets']-max(row['batting_position']-2,0)
        else:
            partnerships = row['exit_point_wickets']-max(row['batting_position']-2,0)+1
            
        bat_stats.at[index, 'partnerships_part_of'] = partnerships
        
    
    # Reset the DataFrame index
    bat_stats.reset_index(drop=True, inplace=True)
    
    
    cols_to_int = ['entry_point','entry_point_balls','exit_point','exit_point_balls','exit_point_wickets',
                  'partnerships_part_of']

    def to_int(column):
            try:
                return int(column)
            except:
                return column

    for column in cols_to_int:
        bat_stats[column] = bat_stats[column].apply(to_int)


    # Reset the DataFrame index
    bat_stats.reset_index(drop=True, inplace=True)
    
    #--------------------------------------------------------------------------------------------------------
     
    return bat_stats.sort_values(by=['match_id','innings','batting_position'])


# In[8]:


def bowl_stats(df):

    bowler_groupby = ['match_id','innings','bowler']

    # Group by 'match_id', and 'bowler' and apply the aggregation functions
    bowl_stats = df.groupby(bowler_groupby).agg(

        team = ('bowling_team', unique_value_without_nan),
        opposition = ('batting_team', unique_value_without_nan),
        
        runs= ('runs_conceded_by_bowler','sum'),              
        balls= ('islegal','sum'),
        wickets= ('isBowlerWicket','sum'),

        dots= ('isDotforBowler','sum'),
        
        strike_rotations= ('isStrikeRotation','sum'),
        fours= ('isFour','sum'),
        sixes= ('isSix','sum'),
        wides= ('iswide','sum'),
        nos= ('isno','sum')
    
    ).reset_index()

    """
    bowl_stats['SR'] = np.where(bowl_stats['wickets'] > 0, bowl_stats['balls'] / bowl_stats['wickets'], \
                                             np.nan)
    bowl_stats['ER'] = np.where(bowl_stats['balls'] > 0, 6*bowl_stats['runs'] / bowl_stats['balls'], \
                                             np.nan)
    bowl_stats['dot_%'] = np.where(bowl_stats['balls'] > 0, 100*bowl_stats['dots'] / bowl_stats['balls'], \
                                             np.nan)
    """
    
    # Reset the DataFrame index
    bowl_stats.reset_index(drop=True, inplace=True)
    
    #--------------------------------------------------------------------------------------------------------
     
    return bowl_stats.sort_values(by=['match_id'])


# In[9]:


# Define the custom aggregation function
def unique_value_without_nan(series):
    return series.dropna().unique()


# In[ ]:





# #### impact calc for one match
# 

# ##### bat impact

# In[ ]:





# In[10]:


df['striker_position'] = np.where(df['striker_batting_position'] <= 3, 'top',
                              np.where(df['striker_batting_position'] <= 6, 'middle',
                                       np.where(df['striker_batting_position'] <= 8, 'lower', 'tail_end')))

df['non_striker_position']= np.where(df['non_striker_batting_position'] <= 3, 'top',
                              np.where(df['non_striker_batting_position'] <= 6, 'middle',
                                       np.where(df['non_striker_batting_position'] <= 8, 'lower', 'tail_end')))

df = df.rename(columns={'isDotforbowler':'isDotforBowler'})

df['over_1'] = df['legal_balls_bowled']//6
df['over_2'] = df['legal_balls_bowled']%6
df['over_1'] = df['over_1'].astype(str)
df['over_2'] = df['over_2'].astype(str)

df['over'] = df['over_1'] + "." +  df['over_2']
df['over'] = df['over'].astype(float)

df.drop(['over_1','over_2'],axis=1,inplace=True)
df['over_'] = np.ceil(df['over'])
df['over_'] = df['over_'].astype(int)

df['phase'] = np.where(df['over']<=6, "PP", np.where(df['over']<=15, "Middle", "Death"))

df = other_derived_cols(df)

cols_to_int = ['match_id','innings','runs_off_bat', 'extras', 'wides', 'noballs', 'byes', 'legbyes',
            'striker_batting_position','non_striker_batting_position',
              'islegal',
       'isDotforBatter', 'isOne', 'isTwo', 'isThree', 'isStrikeRotation',
       'isFour', 'isSix', 'isBowlerWicket', 'is_striker_Out',
       'is_nonstriker_Out', 'isWicket', 'total_runs', 'runs_scored',
       'wickets_down', 'legal_balls_bowled','target',
       'legal_balls_remaining', 'runs_remaining','is_faced_by_batter_cum',
              'last_fow', 'last_fow_balls', 'last_fow_balls_faced',
       'partnership_runs', 'partnership_balls', 'striker_runs',
       'non_striker_runs', 'striker_balls', 'non_striker_balls',
       'runs_conceded_by_bowler', 'bowler_runs', 'bowler_balls', 'bowler_wkts',
        'fours', 'sixes']
    
def to_int(column):
    try:
        return int(column)
    except:
        return column

for column in cols_to_int:
    df[column] = df[column].apply(to_int)

info_df = info_calc(df)
bat_stats_df = bat_stats(df)

condition_cols = ['match_id','innings','team','entry_point_balls','exit_point_balls']

import time

t1 = time.time()
bat_stats_df_merged = merging_match_stats_conditional(bat_stats_df)
t2 = time.time()

print(f"time taken to calculate bat_stats_df_merged: {np.round((t2-t1)/60,2)} minutes")

# run(off bat) & balls proportion
# dot_%, BpB, BpSt_Ro : for both
# then, proportion of each

# Calculating run and ball proportions
bat_stats_df_merged['run_prpn'] = np.where(
    bat_stats_df_merged['phase_runs_bat'] != 0,
    bat_stats_df_merged['runs'] / bat_stats_df_merged['phase_runs_bat'],
    np.nan
)

bat_stats_df_merged['ball_prpn'] = np.where(
    bat_stats_df_merged['phase_balls'] != 0,
    bat_stats_df_merged['balls'] / bat_stats_df_merged['phase_balls'],
    np.nan
)

# Calculating dot ball percentage
bat_stats_df_merged['dot_%'] = np.where(
    bat_stats_df_merged['balls'] != 0,
    100 * bat_stats_df_merged['dots'] / bat_stats_df_merged['balls'],
    np.nan
)

# Calculating Balls per Boundary (BpB)
bat_stats_df_merged['BpB'] = np.where(
    (bat_stats_df_merged['fours'] + bat_stats_df_merged['sixes']) != 0,
    bat_stats_df_merged['balls'] / (bat_stats_df_merged['fours'] + bat_stats_df_merged['sixes']),
    0
)

# Calculating phase dot ball percentage
bat_stats_df_merged['phase_dot_%'] = np.where(
    bat_stats_df_merged['phase_balls'] != 0,
    100 * bat_stats_df_merged['phase_dots'] / bat_stats_df_merged['phase_balls'],
    np.nan
)

# Calculating phase Balls per Boundary (BpB)
bat_stats_df_merged['phase_BpB'] = np.where(
    (bat_stats_df_merged['phase_4s'] + bat_stats_df_merged['phase_6s']) != 0,
    bat_stats_df_merged['phase_balls'] / (bat_stats_df_merged['phase_4s'] + bat_stats_df_merged['phase_6s']),
    0
)

# Calculating comparison proportions
bat_stats_df_merged['dot_compare_prpn'] = np.where(
    bat_stats_df_merged['dot_%'] != 0,
    bat_stats_df_merged['phase_dot_%'] / bat_stats_df_merged['dot_%'],
    np.nan
)

bat_stats_df_merged['BpB_compare_prpn'] = np.where(
    bat_stats_df_merged['BpB'] != 0,
    bat_stats_df_merged['phase_BpB'] / bat_stats_df_merged['BpB'],
    np.nan
)

bat_stats_df_merged = bat_stats_df_merged.merge(info_df, on='match_id', how='left')

# Calculating run and ball proportions
bat_stats_df_merged['final_run_prpn'] = np.where(
    (bat_stats_df_merged['innings'] == 1) & (bat_stats_df_merged['inn1_runs_bat'] != 0),
    bat_stats_df_merged['runs'] / bat_stats_df_merged['inn1_runs_bat'],
    np.where(
        (bat_stats_df_merged['innings'] == 2) & (bat_stats_df_merged['inn2_runs_bat'] != 0),
        bat_stats_df_merged['runs'] / bat_stats_df_merged['inn2_runs_bat'],
        np.nan
    )
)

bat_stats_df_merged['final_ball_prpn'] = np.where(
    (bat_stats_df_merged['innings'] == 1) & (bat_stats_df_merged['inn1_balls'] != 0),
    bat_stats_df_merged['balls'] / bat_stats_df_merged['inn1_balls'],
    np.where(
        (bat_stats_df_merged['innings'] == 2) & (bat_stats_df_merged['inn2_balls'] != 0),
        bat_stats_df_merged['balls'] / bat_stats_df_merged['inn2_balls'],
        np.nan
    )
)


bat_stats_df_inn1 = bat_stats_df_merged[bat_stats_df_merged.innings==1]

bat_stats_df_inn1['entry_point_SR'] = np.where(bat_stats_df_inn1['entry_point_balls']>0,                    100*bat_stats_df_inn1['entry_point']/bat_stats_df_inn1['entry_point_balls'],-1)

# Bin the entry_point_balls and entry_point_SR
bat_stats_df_inn1['entry_point_bins'] = pd.cut(bat_stats_df_inn1['entry_point_balls'], bins=range(0, 121, 10),                                               include_lowest=True, right=False)
bat_stats_df_inn1['entry_point_SR_bins'] = pd.cut(bat_stats_df_inn1['entry_point_SR'], 
                bins=[-1,100,125,150,180,210,275], \
                                                  include_lowest=True, right=True)

## pick the probabilities from pre-computed excel

bat_inn1_prob = pd.read_csv        ('/Users/roumyadas/Desktop/IPL_Simulation/Stats/impact_stats/bat_stats_df_inn1_prob_bins.csv')

for col in bat_inn1_prob:
    if col!='prob_dismissal':
        bat_inn1_prob[col] = bat_inn1_prob[col].astype(str)
        bat_stats_df_inn1[col] = bat_stats_df_inn1[col].astype(str)

bat_stats_df_inn1 = bat_stats_df_inn1.merge(bat_inn1_prob, on=['entry_point_bins','entry_point_SR_bins'],
                                           how='left')
bat_stats_df_inn1['prob_dismissal'] = bat_stats_df_inn1['prob_dismissal'].fillna(0).astype(float)

# Assuming bat_stats_df_merged is already defined somewhere in your code
# Drop columns containing '2' in their name
cols_to_drop = bat_stats_df_merged.columns[bat_stats_df_merged.columns.str.contains('2')]
bat_stats_df_inn1.drop(cols_to_drop, axis=1, inplace=True, errors='ignore')  # Add errors='ignore' to prevent errors if no such column exists

# Drop other specified columns
bat_stats_df_inn1.drop(['entry_point_bins', 'winner', 'win_margin_wkts', 'team_1_bat'], axis=1, inplace=True, errors='ignore')  # Add errors='ignore' to prevent errors if no such column exists



bat_stats_df_inn1['entry_SR_multiplier']=np.where(bat_stats_df_inn1['entry_point_SR']>0,
                        bat_stats_df_inn1['SR']/bat_stats_df_inn1['entry_point_SR'],
                                                  0)

# Calculate phase SR multiplier
bat_stats_df_inn1['phase_SR_multiplier'] = np.where(
    bat_stats_df_inn1['ball_prpn'] != 0,
    bat_stats_df_inn1['run_prpn'] / bat_stats_df_inn1['ball_prpn'],
    np.nan
)

# Calculate final SR multiplier
bat_stats_df_inn1['final_SR_multiplier'] = np.where(
    bat_stats_df_inn1['final_ball_prpn'] != 0,
    bat_stats_df_inn1['final_run_prpn'] / bat_stats_df_inn1['final_ball_prpn'],
    np.nan
)

# Calculate final dot compare proportion
bat_stats_df_inn1['final_dot_compare_prpn'] = np.where(
    bat_stats_df_inn1['dot_%'] != 0,
    (100 * bat_stats_df_inn1['inn1_dots'] / bat_stats_df_inn1['inn1_balls']) / bat_stats_df_inn1['dot_%'],
    np.nan
)

# Calculate final Balls per Boundary (BpB) compare proportion
bat_stats_df_inn1['final_BpB_compare_prpn'] = np.where(
    ((bat_stats_df_inn1['inn1_4s'] + bat_stats_df_inn1['inn1_6s']) != 0) & ((bat_stats_df_inn1['fours'] + bat_stats_df_inn1['sixes']) != 0),
    (bat_stats_df_inn1['inn1_balls'] / (bat_stats_df_inn1['inn1_4s'] + bat_stats_df_inn1['inn1_6s'])) / 
    (bat_stats_df_inn1['balls'] / (bat_stats_df_inn1['fours'] + bat_stats_df_inn1['sixes'])),
    np.nan
)

fill_with_0 = ['dot_compare_prpn','BpB_compare_prpn','phase_SR_multiplier',
               'final_SR_multiplier','final_dot_compare_prpn','final_BpB_compare_prpn']

bat_stats_df_inn1[fill_with_0] = bat_stats_df_inn1[fill_with_0].fillna(0)

cols = ['match_id', 'innings', 'striker', 'team', 'opposition',
       'batting_position','entry_point','entry_point_balls', 'runs', 'balls','SR','mode_of_dismissal','phase_balls',
       'partnerships_part_of','inn1_balls','dot_compare_prpn', 'BpB_compare_prpn',
       'win_fl_inn1', 'win_margin_runs','entry_SR_multiplier','phase_SR_multiplier',
       'final_SR_multiplier', 'final_dot_compare_prpn',
       'final_BpB_compare_prpn','prob_dismissal']

bat_inn1_sub = bat_stats_df_inn1[cols]

# Initialize 'impact_runs' column with NaN
bat_inn1_sub['impact_runs'] = np.nan

# Iterate over rows and compute 'impact_runs'
for index, row in bat_inn1_sub.iterrows():
    
    mod = row['mode_of_dismissal']
    prob = row['prob_dismissal']
    frac_entry = row['entry_point_balls'] / row['balls'] if row['balls'] > 0 else 0
    
    wt_phase = np.sqrt(row['phase_balls'] / row['balls']) if row['balls'] > 0 else 0
    wt_total = np.sqrt(row['inn1_balls'] / row['balls']) if row['balls'] > 0 else 0
    wt_entry = frac_entry**(0.5 if frac_entry > 1 else 1) if (row['entry_point_balls'] > 0 and row['balls'] > 0) else 0
    
    wt = row['balls'] / row['inn1_balls'] if row['inn1_balls'] > 0 else 0
    
    total_wt = wt_phase + wt_total + wt_entry if (wt_phase + wt_total + wt_entry) > 0 else 1
    
    SR_contribution = (row['phase_SR_multiplier'] * wt_phase + row['final_SR_multiplier'] * wt_total + 
                       row['entry_SR_multiplier'] * wt_entry) / total_wt
    
    dot_contribution = -1 + (row['dot_compare_prpn'] * wt_phase + row['final_dot_compare_prpn'] * wt_total) / total_wt
    bpb_contribution = -1 + (row['BpB_compare_prpn'] * wt_phase + row['final_BpB_compare_prpn'] * wt_total) / total_wt
    
    wkts_contribution = wt * row['partnerships_part_of']**2 if row['partnerships_part_of'] > 1 else 0
    dismissal_contribution = wt * prob * row['runs']**0.75 if mod != 'not out' else 0
    
    adjusted_runs = row['runs'] * SR_contribution + (dot_contribution + bpb_contribution) +                     (wkts_contribution + dismissal_contribution)
    
    bat_inn1_sub.at[index, 'impact_runs'] = adjusted_runs

# Calculate 'run_diff'
bat_inn1_sub['run_diff'] = bat_inn1_sub['impact_runs'] - bat_inn1_sub['runs']

# Function to adjust run_diff so that its sum is zero while maintaining sign
def adjust_run_diff(df):
    current_sum = df['run_diff'].sum()
    
    if current_sum != 0:
        total_abs_sum = df['run_diff'].abs().sum()
        adjustment_factor = current_sum / total_abs_sum
        df['run_diff_adjusted'] = df['run_diff'].apply(lambda x: x - x * adjustment_factor)
    
    return df

# Apply the function to each match_id
bat_inn1_sub = bat_inn1_sub.groupby('match_id').apply(adjust_run_diff).reset_index(drop=True)

# Calculate 'adjusted_runs' and 'addnl_impact_per_ball'
bat_inn1_sub['adjusted_runs'] = bat_inn1_sub['runs'] + bat_inn1_sub['run_diff_adjusted']
bat_inn1_sub['addnl_impact_per_ball'] = bat_inn1_sub['run_diff'] / bat_inn1_sub['balls']

bat_stats_df_inn2 = bat_stats_df_merged[bat_stats_df_merged.innings==2]

bat_stats_df_inn2['target'] = bat_stats_df_inn2['inn1_runs_total']+1
bat_stats_df_inn2['entry_point_reqd_SR'] = np.where(bat_stats_df_inn2['entry_point']<bat_stats_df_inn2['target']
                                    ,100*(bat_stats_df_inn2['target']-bat_stats_df_inn2['entry_point'])\
                            /(120-bat_stats_df_inn2['entry_point_balls']),0)

bat_stats_df_inn2['entry_point_SR'] = np.where(bat_stats_df_inn2['entry_point_balls']>0,                    100*bat_stats_df_inn2['entry_point']/bat_stats_df_inn2['entry_point_balls'],-1)

# Bin the entry_point_balls and entry_point_SR
bat_stats_df_inn2['entry_point_bins'] = pd.cut(bat_stats_df_inn2['entry_point_balls'], bins=range(0, 121, 10),                                               include_lowest=True, right=False)
bat_stats_df_inn2['entry_point_reqd_SR_bins'] = pd.cut(bat_stats_df_inn2['entry_point_reqd_SR'], 
                bins=[0,100,125,150,180,210,5900], \
                                                       include_lowest=True, right=True)


## pick the probabilities from pre-computed excel

bat_inn2_prob = pd.read_csv        ('/Users/roumyadas/Desktop/IPL_Simulation/Stats/impact_stats/bat_stats_df_inn2_prob_bins.csv')

for col in bat_inn2_prob:
    if col!='prob_dismissal':
        bat_inn2_prob[col] = bat_inn2_prob[col].astype(str)
        bat_stats_df_inn2[col] = bat_stats_df_inn2[col].astype(str)

bat_stats_df_inn2 = bat_stats_df_inn2.merge(bat_inn2_prob.drop_duplicates(), on=['entry_point_bins','entry_point_reqd_SR_bins'],
                                           how='left')
bat_stats_df_inn2['prob_dismissal'] = bat_stats_df_inn2['prob_dismissal'].fillna(0).astype(float)

# Assuming bat_stats_df_merged is already defined somewhere in your code
# Drop columns containing '1' in their name
cols_to_drop = bat_stats_df_merged.columns[bat_stats_df_merged.columns.str.contains('1')]
bat_stats_df_inn2.drop(cols_to_drop, axis=1, inplace=True, errors='ignore')  
# Add errors='ignore' to prevent errors if no such column exists

# Drop other specified columns
bat_stats_df_inn2.drop(['entry_point_bins', 'winner', 'win_margin_wkts', 'team_2_bat'],                        axis=1, inplace=True, errors='ignore')  


bat_stats_df_inn2['entry_SR_multiplier']=np.where(bat_stats_df_inn2['entry_point_SR']>0,
                        bat_stats_df_inn2['SR']/bat_stats_df_inn2['entry_point_SR'],
                                                  0)

bat_stats_df_inn2['entry_reqd_SR_multiplier']=np.where(bat_stats_df_inn2['entry_point_reqd_SR']>0,
                        bat_stats_df_inn2['SR']/bat_stats_df_inn2['entry_point_reqd_SR'],
                                                  0)

# Calculate phase SR multiplier
bat_stats_df_inn2['phase_SR_multiplier'] = np.where(
    bat_stats_df_inn2['ball_prpn'] != 0,
    bat_stats_df_inn2['run_prpn'] / bat_stats_df_inn2['ball_prpn'],
    np.nan
)

# Calculate final SR multiplier
bat_stats_df_inn2['final_SR_multiplier'] = np.where(
    bat_stats_df_inn2['final_ball_prpn'] != 0,
    bat_stats_df_inn2['final_run_prpn'] / bat_stats_df_inn2['final_ball_prpn'],
    np.nan
)

# Calculate final dot compare proportion
bat_stats_df_inn2['final_dot_compare_prpn'] = np.where(
    bat_stats_df_inn2['dot_%'] != 0,
    (100 * bat_stats_df_inn2['inn2_dots'] / bat_stats_df_inn2['inn2_balls']) / bat_stats_df_inn2['dot_%'],
    np.nan
)

# Calculate final Balls per Boundary (BpB) compare proportion
bat_stats_df_inn2['final_BpB_compare_prpn'] = np.where(
    ((bat_stats_df_inn2['inn2_4s'] + bat_stats_df_inn2['inn2_6s']) != 0) & ((bat_stats_df_inn2['fours'] + bat_stats_df_inn2['sixes']) != 0),
    (bat_stats_df_inn2['inn2_balls'] / (bat_stats_df_inn2['inn2_4s'] + bat_stats_df_inn2['inn2_6s'])) / 
    (bat_stats_df_inn2['balls'] / (bat_stats_df_inn2['fours'] + bat_stats_df_inn2['sixes'])),
    np.nan
)

fill_with_0 = ['dot_compare_prpn','BpB_compare_prpn','phase_SR_multiplier',
               'final_SR_multiplier','final_dot_compare_prpn','final_BpB_compare_prpn']

bat_stats_df_inn2[fill_with_0] = bat_stats_df_inn2[fill_with_0].fillna(0)

cols = ['match_id', 'innings', 'striker', 'team', 'opposition',
       'batting_position','target','entry_point','entry_point_balls', 'runs', 'balls','SR','mode_of_dismissal','phase_balls',
       'partnerships_part_of','inn2_balls','dot_compare_prpn', 'BpB_compare_prpn',
       'win_fl_inn2', 'win_margin_runs','entry_SR_multiplier','entry_reqd_SR_multiplier','phase_SR_multiplier',
       'final_SR_multiplier', 'final_dot_compare_prpn',
       'final_BpB_compare_prpn','prob_dismissal']

bat_inn2_sub = bat_stats_df_inn2[cols]



# Initialize 'impact_runs' column
bat_inn2_sub['impact_runs'] = np.nan

# Iterate over rows and compute 'impact_runs'
for index, row in bat_inn2_sub.iterrows():
    
    mod = row['mode_of_dismissal']
    prob = row['prob_dismissal']
    
    frac_entry = row['entry_point_balls'] / row['balls']
    frac_reqd = (120 - row['entry_point_balls']) / row['balls']

    wt_phase = np.where(row['balls'] > 0, np.sqrt(row['phase_balls'] / row['balls']), 0)
    wt_total = np.where(row['balls'] > 0, (row['inn2_balls'] / row['balls'])**0.25, 0)
    wt_entry = np.where((row['entry_point_balls'] > 0) & (row['balls'] > 0), 
                        frac_entry**np.where(frac_entry>1,0.25,1), 0)
    wt_reqd = np.where((row['entry_point_balls'] < 120) & ((row['target'] - row['entry_point']) > 0), 
                       frac_reqd**0.5, 0)
    
    wt = row['balls'] / row['inn2_balls']
    
    total_wt = wt_phase + wt_total + wt_entry + wt_reqd
    
    SR_contribution = (row['phase_SR_multiplier'] * wt_phase + row['final_SR_multiplier'] * wt_total + 
                       row['entry_SR_multiplier'] * wt_entry + row['entry_reqd_SR_multiplier'] * wt_reqd) / total_wt
    
    dot_contribution = -1 + (row['dot_compare_prpn'] * wt_phase + row['final_dot_compare_prpn'] * wt_total) / total_wt
    bpb_contribution = -1 + (row['BpB_compare_prpn'] * wt_phase + row['final_BpB_compare_prpn'] * wt_total) / total_wt
    
    wkts_contribution = np.where(row['partnerships_part_of'] > 1, wt * row['partnerships_part_of']**2, 0)
    dismissal_contribution = np.where(mod != 'not out', wt * prob * row['runs']**0.75, 0)
    
    adjusted_runs = row['runs'] * SR_contribution + (dot_contribution + bpb_contribution) +                     (wkts_contribution + dismissal_contribution)
    
    bat_inn2_sub.at[index, 'impact_runs'] = adjusted_runs

# Calculate 'run_diff'
bat_inn2_sub['run_diff'] = bat_inn2_sub['impact_runs'] - bat_inn2_sub['runs']

# Function to adjust run_diff so that its sum is zero while maintaining sign
def adjust_run_diff(df):
    current_sum = df['run_diff'].sum()
    
    if current_sum != 0:
        total_abs_sum = df['run_diff'].abs().sum()
        adjustment_factor = current_sum / total_abs_sum
        df['run_diff_adjusted'] = df['run_diff'].apply(lambda x: x - x * adjustment_factor)
    
    return df

# Apply the function to each match_id
bat_inn2_sub = bat_inn2_sub.groupby('match_id').apply(adjust_run_diff).reset_index(drop=True)

# Calculate 'adjusted_runs' and 'addnl_impact_per_ball'
bat_inn2_sub['adjusted_runs'] = bat_inn2_sub['runs'] + bat_inn2_sub['run_diff_adjusted']
bat_inn2_sub['addnl_impact_per_ball'] = bat_inn2_sub['run_diff_adjusted'] / bat_inn2_sub['balls']



bat_impact_df = pd.concat([bat_inn1_sub,bat_inn2_sub], axis=0)
bat_impact_df.sort_values(by=['match_id','innings','batting_position']).reset_index(drop=True, inplace=True)


# In[ ]:





# ##### bowl impact

# In[11]:


def info_calc(df):

    # Pivot table for 'bowling_team' without 'phase'
    bowling_team_pivot = pd.pivot_table(
        df, 
        index=['match_id'],
        columns='innings', 
        values='bowling_team',
        aggfunc=unique_value_without_nan
    ).reset_index()

    # Pivot table for the rest of the columns 
    other_pivot = pd.pivot_table(
        df, 
        index=['match_id'],
        columns=['innings'], 
        values=['runs_conceded_by_bowler','total_runs','isDotforBowler','isFour','isSix','isStrikeRotation',
                'islegal', 'isBowlerWicket','iswide','isno'],
        aggfunc=np.sum
    ).reset_index()

    # Merge the two pivot tables on 'match_id'
    info_df = bowling_team_pivot.merge(other_pivot, on='match_id')

    info_df.columns = ['match_id','team_1_bowl','team_2_bowl','inn1_wkts','inn2_wkts','inn1_dots','inn2_dots',
                       'inn1_4s','inn2_4s','inn1_6s','inn2_6s',
                       'inn1_stros','inn2_stros','inn1_balls','inn2_balls',
                       'inn1_nos','inn2_nos','inn1_wides','inn2_wides',
                      'inn1_runs_conceeded','inn2_runs_conceeded',
                  'inn1_runs_total','inn2_runs_total']

    
    info_df['winner'] = None
    info_df['win_fl_inn1'] = None
    info_df['win_fl_inn2'] = None
    info_df['win_margin_runs'] = None
    info_df['win_margin_wkts'] = None
    
    for index,row in info_df.iterrows():
        inn1_total = row['inn1_runs_total']
        inn2_total = row['inn2_runs_total']
        
        if inn2_total>inn1_total:
            info_df.at[index, 'winner'] = row['team_1_bowl']
            info_df.at[index, 'win_fl_inn1'] = 0
            info_df.at[index, 'win_fl_inn2'] = 1
            info_df.at[index, 'win_margin_wkts'] = 10-row['inn2_wkts']
            
        elif inn1_total>inn2_total:
            info_df.at[index, 'winner'] = row['team_2_bowl']
            info_df.at[index, 'win_fl_inn1'] = 1
            info_df.at[index, 'win_fl_inn2'] = 0
            info_df.at[index, 'win_margin_runs'] = inn1_total-inn2_total
        
    return info_df


# In[12]:


def info_calc_conditional(df):

    # Pivot table for the rest of the columns with 'phase'
    info_df = pd.pivot_table(
        df, 
        index=['match_id','innings'],
        #columns=['innings'], 
        values=['runs_conceded_by_bowler','total_runs','isDotforBowler','isFour','isSix','isStrikeRotation',
                'islegal', 'isBowlerWicket','iswide','isno'],
        aggfunc=np.sum
    ).reset_index()
    
    partnership_info= df.groupby('match_id')[['partnership_runs','partnership_balls']].last()

    # Merge the two pivot tables on 'match_id'
    info_df = info_df.merge(partnership_info, on='match_id', how='left')
    
    info_df.columns = ['match_id','innings','inn1_bowl_wkts','inn1_bowl_dots',
                       'inn1_4s','inn1_6s','inn1_stros','inn1_balls',
                       'inn1_nos','inn1_wides',
                      'inn1_runs_conceeded',
                  'inn1_runs_total','inn1_partnership_runs','inn1_partnership_balls']

    
    return info_df


# In[13]:


def info_calc_conditional_2(df):

    # Pivot table for the rest of the columns with 'phase'
    info_df = pd.pivot_table(
        df, 
        index=['match_id','innings'],
        #columns=['innings'], 
        values=['runs_conceded_by_bowler','total_runs','isDotforBowler','isFour','isSix','isStrikeRotation',
                'islegal', 'isBowlerWicket','iswide','isno'],
        aggfunc=np.sum
    ).reset_index()
    
    partnership_info= df.groupby('match_id')[['partnership_runs','partnership_balls']].last()

    # Merge the two pivot tables on 'match_id'
    info_df = info_df.merge(partnership_info, on='match_id', how='left')
    
    info_df.columns = ['match_id','innings','inn2_bowl_wkts','inn2_bowl_dots',
                       'inn2_4s','inn2_6s','inn2_stros','inn2_balls',
                       'inn2_nos','inn2_wides',
                      'inn2_runs_conceeded',
                  'inn2_runs_total','inn2_partnership_runs','inn2_partnership_balls']

    
    return info_df


# In[14]:


def transform_calc(x):
    if (x>=0):
        return (1 + np.log(1+ np.log(1 + np.log1p(x))))
    else:
        return 1/(1 + np.log(1+ np.log(1 + np.log1p(0-x))))
    
    
def geometric_mean(column):
    
    # Ensure the column is converted to a numpy array and replace non-positive values
    data = column.to_numpy()
    data = data[data > 0]  # Geometric mean is only defined for positive numbers
    
    if len(data) == 0:
        return np.nan  # Return NaN if there are no positive numbers in the column
    
    return np.exp(np.mean(np.log(data)))

def score_bonus(x):
    if x>0:
        return (-1+ x**(1/20))
    else:
        return 0
    
def partnership_bonus(x):
    if x>0:
        return x**(0.05*x/75)
    else:
        return 1


# In[15]:


info_df = info_calc(df)



bowl_stats_df = bowl_stats(df)
bowl_stats_df_inn1 = bowl_stats_df[bowl_stats_df.innings==1]


info_df_inn1 = info_df[info_df.columns[~(info_df.columns.str.contains('2'))]]
info_df_inn1.drop(['team_1_bowl','winner','win_fl_inn1', 'win_margin_runs', 'win_margin_wkts'],
                  axis=1,inplace=True)

bowl_stats_df_inn1 = bowl_stats_df_inn1.merge(info_df_inn1, on='match_id', how='left')

# runs conceeded & balls proportion
# dot_%, BpB, Bp_StRo, BpE : for both
# then, proportion of each

# Calculating run and ball proportions
bowl_stats_df_inn1['run_prpn'] = np.where(
    bowl_stats_df_inn1['inn1_runs_conceeded'] > 0,
    bowl_stats_df_inn1['runs'] / bowl_stats_df_inn1['inn1_runs_conceeded'],
    np.nan
)

bowl_stats_df_inn1['ball_prpn'] = np.where(
    bowl_stats_df_inn1['inn1_balls'] > 0,
    bowl_stats_df_inn1['balls'] / bowl_stats_df_inn1['inn1_balls'],
    np.nan
)

bowl_stats_df_inn1['wicket_prpn'] = np.where(
    bowl_stats_df_inn1['inn1_wkts'] > 0,
    bowl_stats_df_inn1['wickets'] / bowl_stats_df_inn1['inn1_wkts'],
    np.nan
)


# Calculating dot ball percentage
bowl_stats_df_inn1['dot_%'] = np.where(
    bowl_stats_df_inn1['balls'] > 0,
    100 * bowl_stats_df_inn1['dots'] / bowl_stats_df_inn1['balls'],
    np.nan
)

# Calculating Balls per Boundary (BpB)
bowl_stats_df_inn1['BpB'] = np.where(
    (bowl_stats_df_inn1['fours'] + bowl_stats_df_inn1['sixes']) > 0,
    bowl_stats_df_inn1['balls'] / (bowl_stats_df_inn1['fours'] + bowl_stats_df_inn1['sixes']),
    0
)

# Calculating Balls per StrikeRotation (Bp_StRo)
bowl_stats_df_inn1['Bp_StRo'] = np.where(
    bowl_stats_df_inn1['strike_rotations'] > 0,
    bowl_stats_df_inn1['balls'] / bowl_stats_df_inn1['strike_rotations'],
    0
)

# Calculating Balls per Extras (BpE)
bowl_stats_df_inn1['BpE'] = np.where(
    (bowl_stats_df_inn1['wides'] + bowl_stats_df_inn1['nos']) > 0,
    bowl_stats_df_inn1['balls'] / (bowl_stats_df_inn1['wides'] + bowl_stats_df_inn1['nos']),
    0
)


# Calculating total dot ball percentage
bowl_stats_df_inn1['total_dot_%'] = np.where(
    bowl_stats_df_inn1['inn1_balls'] > 0,
    100 * bowl_stats_df_inn1['inn1_dots'] / bowl_stats_df_inn1['inn1_balls'],
    np.nan
)

# Calculating total Balls per Boundary (BpB)
bowl_stats_df_inn1['total_BpB'] = np.where(
    (bowl_stats_df_inn1['inn1_4s'] + bowl_stats_df_inn1['inn1_6s']) != 0,
    bowl_stats_df_inn1['inn1_balls'] / (bowl_stats_df_inn1['inn1_4s'] + bowl_stats_df_inn1['inn1_6s']),
    0
)

# Calculating total Balls per StrikeRotation (Bp_StRo)
bowl_stats_df_inn1['total_Bp_StRo'] = np.where(
    bowl_stats_df_inn1['inn1_stros'] > 0,
    bowl_stats_df_inn1['inn1_balls'] / bowl_stats_df_inn1['inn1_stros'],
    0
)

# Calculating total Balls per Extras (BpE)
bowl_stats_df_inn1['total_BpE'] = np.where(
    (bowl_stats_df_inn1['inn1_wides'] + bowl_stats_df_inn1['inn1_nos']) > 0,
    bowl_stats_df_inn1['inn1_balls'] / (bowl_stats_df_inn1['inn1_wides'] + bowl_stats_df_inn1['inn1_nos']),
    0
)

# Calculating comparison proportions
bowl_stats_df_inn1['dot_compare_prpn'] = np.where(
    bowl_stats_df_inn1['total_dot_%'] > 0,
    bowl_stats_df_inn1['dot_%'] / bowl_stats_df_inn1['total_dot_%'],
    np.nan
)

bowl_stats_df_inn1['BpB_compare_prpn'] = np.where(
    bowl_stats_df_inn1['total_BpB'] > 0,
    bowl_stats_df_inn1['BpB'] / bowl_stats_df_inn1['total_BpB'],
    bowl_stats_df_inn1['balls']
)

bowl_stats_df_inn1['Bp_StRo_compare_prpn'] = np.where(
    bowl_stats_df_inn1['total_Bp_StRo'] > 0,
    bowl_stats_df_inn1['Bp_StRo'] / bowl_stats_df_inn1['total_Bp_StRo'],
    bowl_stats_df_inn1['balls']
)

bowl_stats_df_inn1['BpE_compare_prpn'] = np.where(
    bowl_stats_df_inn1['total_BpE'] > 0,
    bowl_stats_df_inn1['BpE'] / bowl_stats_df_inn1['total_BpE'],
    bowl_stats_df_inn1['balls']
)


bowl_stats_df_inn1['ER_points'] = 100/((6*bowl_stats_df_inn1['runs']/bowl_stats_df_inn1['balls'])**1.25)
bowl_stats_df_inn1['wkt_points'] = 25*bowl_stats_df_inn1['wickets']

bowl_stats_df_inn1['dot_points'] = (bowl_stats_df_inn1['dot_%']/10)**1.25
bowl_stats_df_inn1['bpb_points'] = np.where((bowl_stats_df_inn1['fours']+bowl_stats_df_inn1['sixes'])>0,
                                    bowl_stats_df_inn1['BpB'],
                                      np.where((((bowl_stats_df_inn1['fours']+bowl_stats_df_inn1['sixes'])==0) &
                                                bowl_stats_df_inn1['balls']>0),
                                              bowl_stats_df_inn1['balls'], 0))





df1 = df[df.innings==1]

pre_stats_df = pd.DataFrame()

for match in df1.match_id.unique():
    m1 = df1[df1.match_id==match]


    m_b4_df = pd.DataFrame()

    for bowler_name in m1.bowler.unique():

        b_1 = m1[m1.bowler==bowler_name]
        first_balls = np.array(b_1.groupby('over')['ball'].first())

        stats_b4_df = pd.DataFrame({
            'match_id': [match],
            'innings': 1,
            'bowler': [bowler_name]
            })

        i=-1

        #print(first_balls)
        for start_ball in first_balls:
            i =i+1
            #print(start_ball)
            if str(start_ball).startswith('1'):
                output = pd.DataFrame(columns=['inn1_bowl_wkts','inn1_bowl_dots',
                       'inn1_4s','inn1_6s','inn1_stros','inn1_balls',
                       'inn1_nos','inn1_wides',
                      'inn1_runs_conceeded',
                  'inn1_runs_total','inn1_partnership_runs','inn1_partnership_balls'])
                output['inn1_run_rate'] = 0
                output.columns = [col+str('_')+str(i) for col in output.columns]
                output.loc[0] = 0 #np.nan
                stats_b4_df = pd.concat([stats_b4_df, output], axis=1)

            else:

                output = info_calc_conditional(m1[m1.ball < start_ball])
                output.drop('match_id', axis=1, inplace=True)
                output['inn1_run_rate'] = 6*output['inn1_runs_conceeded']/output['inn1_balls']
                output.columns = [col + '_' + str(i) for col in output.columns]

                # Append columns to stats_b4_df
                stats_b4_df = pd.concat([stats_b4_df, output], axis=1)

        m_b4_df = m_b4_df.append(stats_b4_df)
    pre_stats_df = pre_stats_df.append(m_b4_df)
    
    
pre_stats_df = pre_stats_df.drop(['innings_0','innings_1','innings_2','innings_3'], axis=1).reset_index(drop=True)



over_stats_df = pd.DataFrame()

df1 = df[df.innings==1]

for match in df1.match_id.unique():
    m1 = df1[df1.match_id==match]


    m_df = pd.DataFrame()

    for bowler_name in m1.bowler.unique():

        b_1 = m1[m1.bowler==bowler_name]
        stats_df = pd.DataFrame({
                'match_id': [match],
                'innings': 1,
                'bowler': [bowler_name]
                })
        overs = b_1.over.unique()
        i=-1
        for over in overs:
            i=i+1
            b1_o = b_1[b_1.over==over]
            
            stats_df['over'+str('_')+str(i)] = over
            stats_df['runs_in_over'+str('_')+str(i)] = b1_o.runs_conceded_by_bowler.sum()
            stats_df['balls_in_over'+str('_')+str(i)] = b1_o.islegal.sum()
            stats_df['wkts_in_over'+str('_')+str(i)] = b1_o.isBowlerWicket.sum()
            
        over_stats_df = over_stats_df.append(stats_df)
    
    
    
bowl_stats_df_inn1 = bowl_stats_df_inn1.merge(pre_stats_df, on=['match_id','innings','bowler'], how='left')
bowl_stats_df_inn1 = bowl_stats_df_inn1.merge(over_stats_df, on=['match_id','innings','bowler'], how='left')

# Step 1: Create bins for `run_rate`
bins = [-1, 6, 7.5, 8.75, 10, 12, 100]

def count_non_zero(values):
    return (values != 0).sum()

for i in range(4):
    # Create run rate bins
    bowl_stats_df_inn1['run_rate_bin_' + str(i)] = pd.cut(bowl_stats_df_inn1['inn1_run_rate_' + str(i)], bins=bins, right=True)
   


cols__ = ['over_0',
 'run_rate_bin_0',
                    'inn1_bowl_wkts_0',
 'over_1',
 'run_rate_bin_1',
                    'inn1_bowl_wkts_1',
 'over_2',
 'run_rate_bin_2',
                    'inn1_bowl_wkts_2',
 'over_3',
 'run_rate_bin_3',
                    'inn1_bowl_wkts_3'
 ]

## pick the probabilities from pre-computed excel

bowl_inn1_prob = pd.read_csv        ('/Users/roumyadas/Desktop/IPL_Simulation/Stats/impact_stats/bowl_stats_df_inn1_prob_bins.csv')

for col in bowl_inn1_prob:
    if str(col).startswith('prob_wicket')==False:
        bowl_inn1_prob[col] = bowl_inn1_prob[col].astype(str)
        bowl_stats_df_inn1[col] = bowl_stats_df_inn1[col].astype(str)

bowl_stats_df_inn1 = bowl_stats_df_inn1.merge(bowl_inn1_prob.drop_duplicates(), 
                                              on=cols__,
                                           how='left')
prob_cols = ['prob_wicket_0','prob_wicket_1','prob_wicket_2','prob_wicket_3']
bowl_stats_df_inn1[prob_cols] = bowl_stats_df_inn1[prob_cols].fillna(0).astype(float)






for i in range(4):
    
    bowl_stats_df_inn1['pre_ER_multiplier_'+str(i)] = np.where(bowl_stats_df_inn1['balls_in_over_'+str(i)]>0,
            bowl_stats_df_inn1['inn1_run_rate_'+str(i)]/\
                np.where(bowl_stats_df_inn1['runs_in_over_'+str(i)]>0,
                         6*bowl_stats_df_inn1['runs_in_over_'+str(i)]/bowl_stats_df_inn1['balls_in_over_'+str(i)],
                        0.5),np.nan)
    
    
    bowl_stats_df_inn1['pre_wkt_bonus_'+str(i)] = np.where(bowl_stats_df_inn1['wkts_in_over_'+str(i)]>0,
            np.where(bowl_stats_df_inn1['prob_wicket_'+str(i)]>0,
                     bowl_stats_df_inn1['wkts_in_over_'+str(i)]/bowl_stats_df_inn1['prob_wicket_'+str(i)],
                        5*bowl_stats_df_inn1['wkts_in_over_'+str(i)]),0)
    
    
    bowl_stats_df_inn1['pre_partnership_bonus_'+str(i)] = np.where((bowl_stats_df_inn1['balls_in_over_'+str(i)]>0) & 
                                                                   (bowl_stats_df_inn1['wkts_in_over_'+str(i)]>0),
            bowl_stats_df_inn1['inn1_partnership_runs_'+str(i)],0)
    
    
    
    

cols_ = bowl_stats_df_inn1.columns[bowl_stats_df_inn1.columns.str.contains('prpn|multiplier|bonus')]

for col in bowl_stats_df_inn1.columns:
    if '_bin_' not in str(col):
        bowl_stats_df_inn1[col] = bowl_stats_df_inn1[col].fillna(0)

def transform_calc(x):
    if (x>=0):
        return (1 + np.log(1+ np.log(1 + np.log1p(x))))
    else:
        return 1/(1 + np.log(1+ np.log(1 + np.log1p(0-x))))
    
    
def geometric_mean(column):
    
    # Ensure the column is converted to a numpy array and replace non-positive values
    data = column.to_numpy()
    data = data[data > 0]  # Geometric mean is only defined for positive numbers
    
    if len(data) == 0:
        return np.nan  # Return NaN if there are no positive numbers in the column
    
    return np.exp(np.mean(np.log(data)))

def score_bonus(x):
    if x>0:
        return (-1+ x**(1/20))
    else:
        return 0
    
def partnership_bonus(x):
    if x>0:
        return x**(0.05*x/75)
    else:
        return 1

bat_impact = bat_impact_df

bowl_wkts_df = df1[df1.isBowlerWicket==1][['bowler','match_id','striker','partnership_runs']].drop_duplicates()        .sort_values(by=['match_id','bowler']).reset_index(drop=True)

bowl_wkts_df = bowl_wkts_df.merge(bat_impact[['match_id','striker','runs','impact_runs']], 
                                  on=['match_id','striker'], how='left')


#bowl_wkts_df

median_imp_runs = bowl_wkts_df.groupby('match_id')['impact_runs'].median().reset_index()
median_imp_runs.rename(columns={'impact_runs':'median_impact_runs'}, inplace=True)
    
bowl_wkts_df = bowl_wkts_df.merge(median_imp_runs, on='match_id',how='left')

##
bowl_wkts_df['median_impact_runs'] = bowl_wkts_df['median_impact_runs'].replace(0, 1)

bowl_wkts_df['wkt_impact'] = bowl_wkts_df['impact_runs']/bowl_wkts_df['median_impact_runs']-1
bowl_wkts_df['runs_bonus'] = bowl_wkts_df['runs'].apply(score_bonus)
bowl_wkts_df['partnership_bonus'] = bowl_wkts_df['partnership_runs'].apply(partnership_bonus)

bowl_wkts_df['wkt_multiplier'] = (bowl_wkts_df['wkt_impact'].apply(transform_calc)+bowl_wkts_df['runs_bonus'])*                                    bowl_wkts_df['partnership_bonus']


wkt_value_df = bowl_wkts_df.groupby(['match_id','bowler'])['wkt_multiplier'].apply(geometric_mean).reset_index()

bowl_stats_df_inn1 = bowl_stats_df_inn1.merge(wkt_value_df, on=['match_id','bowler'], how='left')
bowl_stats_df_inn1['wkt_multiplier'].fillna(0, inplace=True)


bowl_stats_df_inn1['bowl_impact'] = None

for index,row in bowl_stats_df_inn1.iterrows():
    
    ER_multiplier = (row['ball_prpn']/row['run_prpn'])**(1/2.5)
    SR_multiplier = (row['wicket_prpn']/row['ball_prpn'])**(1/10)
    
    wt_total = (row['ball_prpn']) #**0.5
    
    prpn_points = (row['Bp_StRo_compare_prpn']+row['BpE_compare_prpn'])*wt_total*(1-wt_total)
    
    wkt_points = row['wkt_points']*row['wkt_multiplier']*SR_multiplier*(1-wt_total)
    ER_points = row['ER_points']*ER_multiplier*wt_total#*(1-wt_total)
    dot_points = row['dot_points']*row['dot_compare_prpn']*wt_total#*(1-wt_total)
    bpb_points = row['bpb_points']*row['BpB_compare_prpn']*wt_total#*(1-wt_total)
    
    
    addition_points = []
    
    for i in range(4):
        if (row['balls_in_over_'+str(i)]>0):
            wt_pre = row['inn1_balls_'+str(i)]/row['inn1_balls']
            #wt_p = row['inn1_partnership_balls_'+str(i)]/row['inn1_balls']
            
            ER_m = row['pre_ER_multiplier_'+str(i)]
            #P_m = row['pre_partnership_bonus_'+str(i)]
            W_m = row['pre_wkt_bonus_'+str(i)]
            
            
            pre_ER_mutiplier = -1+wt_pre*ER_m**(np.where(ER_m>1,0.5,2))
            #pre_P_multiplier = -1+wt_p*P_m**0.25
            pre_W_multiplier = -1+wt_pre*W_m**0.25
            
            total_addition = pre_ER_mutiplier+pre_W_multiplier#+pre_P_multiplier
            addition_points.append(total_addition)
            
    final_addition_points = wkt_points+prpn_points+ER_points+dot_points+bpb_points+sum(addition_points)
    
    final_impact = final_addition_points
    
    
    bowl_stats_df_inn1.at[index, 'bowl_impact'] = final_impact #[final_impact,ER_points]
                              
        
cols_view = ['match_id', 'innings', 'bowler', 'team', 'opposition', 'runs', 'balls',
       'wickets','wkt_multiplier','bowl_impact']

bowl_impact = bowl_stats_df_inn1[cols_view]
bowl_impact['impact_wkts'] = bowl_impact['wickets']*bowl_impact['wkt_multiplier']

bowl_impact.drop('wkt_multiplier', axis=1, inplace=True)

impact_sum_match = bat_impact[(bat_impact.innings==1)].groupby('match_id')['impact_runs'].sum().reset_index()
impact_sum_match = impact_sum_match.merge(bowl_stats_df_inn1.groupby('match_id')['bowl_impact'].sum()                                          .reset_index(), on='match_id')







info_df = info_calc(df)
bowl_stats_df_inn2 = bowl_stats_df[bowl_stats_df.innings==2]

info_df_inn2 = info_df
#[info_df.columns[~(info_df.columns.str.contains('1'))]]
info_df_inn2.drop(['team_2_bowl','winner', 'win_margin_runs', 'win_margin_wkts'],
                  axis=1,inplace=True)

bowl_stats_df_inn2 = bowl_stats_df_inn2.merge(info_df_inn2, on='match_id', how='left')
bowl_stats_df_inn2['target'] = bowl_stats_df_inn2['inn1_runs_total']+1

bowl_stats_df_inn2 = bowl_stats_df_inn2[bowl_stats_df_inn2.columns[~(bowl_stats_df_inn2.columns.str.contains('1'))]]

# runs conceeded & balls proportion
# dot_%, BpB, Bp_StRo, BpE : for both
# then, proportion of each

# Calculating run and ball proportions
bowl_stats_df_inn2['run_prpn'] = np.where(
    bowl_stats_df_inn2['inn2_runs_conceeded'] > 0,
    bowl_stats_df_inn2['runs'] / bowl_stats_df_inn2['inn2_runs_conceeded'],
    np.nan
)

bowl_stats_df_inn2['ball_prpn'] = np.where(
    bowl_stats_df_inn2['inn2_balls'] > 0,
    bowl_stats_df_inn2['balls'] / bowl_stats_df_inn2['inn2_balls'],
    np.nan
)

bowl_stats_df_inn2['wicket_prpn'] = np.where(
    bowl_stats_df_inn2['inn2_wkts'] > 0,
    bowl_stats_df_inn2['wickets'] / bowl_stats_df_inn2['inn2_wkts'],
    np.nan
)


# Calculating dot ball percentage
bowl_stats_df_inn2['dot_%'] = np.where(
    bowl_stats_df_inn2['balls'] > 0,
    100 * bowl_stats_df_inn2['dots'] / bowl_stats_df_inn2['balls'],
    np.nan
)

# Calculating Balls per Boundary (BpB)
bowl_stats_df_inn2['BpB'] = np.where(
    (bowl_stats_df_inn2['fours'] + bowl_stats_df_inn2['sixes']) > 0,
    bowl_stats_df_inn2['balls'] / (bowl_stats_df_inn2['fours'] + bowl_stats_df_inn2['sixes']),
    0
)

# Calculating Balls per StrikeRotation (Bp_StRo)
bowl_stats_df_inn2['Bp_StRo'] = np.where(
    bowl_stats_df_inn2['strike_rotations'] > 0,
    bowl_stats_df_inn2['balls'] / bowl_stats_df_inn2['strike_rotations'],
    0
)

# Calculating Balls per Extras (BpE)
bowl_stats_df_inn2['BpE'] = np.where(
    (bowl_stats_df_inn2['wides'] + bowl_stats_df_inn2['nos']) > 0,
    bowl_stats_df_inn2['balls'] / (bowl_stats_df_inn2['wides'] + bowl_stats_df_inn2['nos']),
    0
)


# Calculating total dot ball percentage
bowl_stats_df_inn2['total_dot_%'] = np.where(
    bowl_stats_df_inn2['inn2_balls'] > 0,
    100 * bowl_stats_df_inn2['inn2_dots'] / bowl_stats_df_inn2['inn2_balls'],
    np.nan
)

# Calculating total Balls per Boundary (BpB)
bowl_stats_df_inn2['total_BpB'] = np.where(
    (bowl_stats_df_inn2['inn2_4s'] + bowl_stats_df_inn2['inn2_6s']) != 0,
    bowl_stats_df_inn2['inn2_balls'] / (bowl_stats_df_inn2['inn2_4s'] + bowl_stats_df_inn2['inn2_6s']),
    0
)

# Calculating total Balls per StrikeRotation (Bp_StRo)
bowl_stats_df_inn2['total_Bp_StRo'] = np.where(
    bowl_stats_df_inn2['inn2_stros'] > 0,
    bowl_stats_df_inn2['inn2_balls'] / bowl_stats_df_inn2['inn2_stros'],
    0
)

# Calculating total Balls per Extras (BpE)
bowl_stats_df_inn2['total_BpE'] = np.where(
    (bowl_stats_df_inn2['inn2_wides'] + bowl_stats_df_inn2['inn2_nos']) > 0,
    bowl_stats_df_inn2['inn2_balls'] / (bowl_stats_df_inn2['inn2_wides'] + bowl_stats_df_inn2['inn2_nos']),
    0
)

# Calculating comparison proportions
bowl_stats_df_inn2['dot_compare_prpn'] = np.where(
    bowl_stats_df_inn2['total_dot_%'] > 0,
    bowl_stats_df_inn2['dot_%'] / bowl_stats_df_inn2['total_dot_%'],
    np.nan
)

bowl_stats_df_inn2['BpB_compare_prpn'] = np.where(
    bowl_stats_df_inn2['total_BpB'] > 0,
    bowl_stats_df_inn2['BpB'] / bowl_stats_df_inn2['total_BpB'],
    bowl_stats_df_inn2['balls']
)

bowl_stats_df_inn2['Bp_StRo_compare_prpn'] = np.where(
    bowl_stats_df_inn2['total_Bp_StRo'] > 0,
    bowl_stats_df_inn2['Bp_StRo'] / bowl_stats_df_inn2['total_Bp_StRo'],
    bowl_stats_df_inn2['balls']
)

bowl_stats_df_inn2['BpE_compare_prpn'] = np.where(
    bowl_stats_df_inn2['total_BpE'] > 0,
    bowl_stats_df_inn2['BpE'] / bowl_stats_df_inn2['total_BpE'],
    bowl_stats_df_inn2['balls']
)


bowl_stats_df_inn2['ER_points'] = 100/((6*bowl_stats_df_inn2['runs']/bowl_stats_df_inn2['balls'])**1.25)

#bowl_stats_df_inn2['RR_points'] = 100/((6*bowl_stats_df_inn2['runs']/bowl_stats_df_inn2['balls'])**1.25)

bowl_stats_df_inn2['wkt_points'] = 25*bowl_stats_df_inn2['wickets']

bowl_stats_df_inn2['dot_points'] = (bowl_stats_df_inn2['dot_%']/10)**1.25
bowl_stats_df_inn2['bpb_points'] = np.where((bowl_stats_df_inn2['fours']+bowl_stats_df_inn2['sixes'])>0,
                                    bowl_stats_df_inn2['BpB'],
                                      np.where((((bowl_stats_df_inn2['fours']+bowl_stats_df_inn2['sixes'])==0) &
                                                bowl_stats_df_inn2['balls']>0),
                                              bowl_stats_df_inn2['balls'], 0))



df2 = df[df.innings==2]


df2['runs_remain_before'] = df2['runs_remaining']+df2['total_runs']
df2['balls_remain_before'] = df2['legal_balls_remaining']+df2['islegal']

df2['reqd_rr_before'] = np.where((df2['runs_remain_before']>0)&(df2['balls_remain_before']>0),
                                 6*df2['runs_remain_before']/df2['balls_remain_before'],0)

#df2.groupby(['match_id','bowler','over'])['reqd_rr_before'].first().reset_index()
rr_stats = pd.pivot_table(df2, index=['match_id','bowler'], columns='over',values='reqd_rr_before', 
              aggfunc='first').reset_index()



# Function to retain the first 4 non-NaN values, filling the rest with NaNs if 
# fewer than 4 non-NaN values are present
def retain_first_nonnan(row, n=4):
    non_nan_values = row.dropna().tolist()
    if len(non_nan_values) < n:
        non_nan_values.extend([np.nan] * (n - len(non_nan_values)))
    else:
        non_nan_values = non_nan_values[:n]
    return non_nan_values

# Create a new DataFrame to hold the result
rr_result_df = pd.DataFrame(columns=['match_id', 'bowler'] + [f'over_RR_{i}' for i in range(4)])

# Iterate over each row in the DataFrame
for idx, row in rr_stats.iterrows():
    # Extract match_id and bowler
    match_id = row['match_id']
    bowler = row['bowler']
    # Extract first 4 non-NaN values from columns 1 to 20
    first_4_values = retain_first_nonnan(row[2:], n=4)
    #print(first_4_values)
    # Create a new row for the result DataFrame
    new_row = [match_id, bowler] + first_4_values
    #print(new_row)
    # Append the new row to the result DataFrame
    rr_result_df.loc[idx] = new_row


#rr_result_df

pre_stats_df = pd.DataFrame()

for match in df2.match_id.unique():
    m2 = df2[df2.match_id==match]


    m_b4_df = pd.DataFrame()

    for bowler_name in m2.bowler.unique():

        b_2 = m2[m2.bowler==bowler_name]
        first_balls = np.array(b_2.groupby('over')['ball'].first())

        stats_b4_df = pd.DataFrame({
            'match_id': [match],
            'innings': 2,
            'bowler': [bowler_name]
            })

        i=-1

        for start_ball in first_balls:
            i =i+1

            if str(start_ball).startswith('1'):
                output = pd.DataFrame(columns=['inn2_bowl_wkts','inn2_bowl_dots',
                       'inn2_4s','inn2_6s','inn2_stros','inn2_balls',
                       'inn2_nos','inn2_wides',
                      'inn2_runs_conceeded',
                  'inn2_runs_total','inn2_partnership_runs','inn2_partnership_balls'])
                output['inn2_run_rate'] = 0
                output.columns = [col+str('_')+str(i) for col in output.columns]
                output.loc[0] = 0 #np.nan
                stats_b4_df = pd.concat([stats_b4_df, output], axis=1)

            else:

                output = info_calc_conditional_2(m2[m2.ball < start_ball])
                output.drop('match_id', axis=1, inplace=True)
                output['inn2_run_rate'] = 6*output['inn2_runs_conceeded']/output['inn2_balls']
                output.columns = [col + '_' + str(i) for col in output.columns]

                # Append columns to stats_b4_df
                stats_b4_df = pd.concat([stats_b4_df, output], axis=1)

        m_b4_df = m_b4_df.append(stats_b4_df)
    pre_stats_df = pre_stats_df.append(m_b4_df)
    

pre_stats_df = pre_stats_df.drop(['innings_0','innings_2','innings_2','innings_3'], axis=1).reset_index(drop=True)

pre_stats_df = pre_stats_df.merge(rr_result_df, on=['match_id','bowler'], how='left')

over_stats_df = pd.DataFrame()

#df2 = df[df.innings==2]
for match in df2.match_id.unique():
    m2 = df2[df2.match_id==match]


    m_df = pd.DataFrame()

    for bowler_name in m2.bowler.unique():

        b_2 = m2[m2.bowler==bowler_name]
        stats_df = pd.DataFrame({
                'match_id': [match],
                'innings': 2,
                'bowler': [bowler_name]
                })
        overs = b_2.over.unique()
        i=-1
        for over in overs:
            i=i+1
            b2_o = b_2[b_2.over==over]
            
            stats_df['over'+str('_')+str(i)] = over
            stats_df['runs_in_over'+str('_')+str(i)] = b2_o.runs_conceded_by_bowler.sum()
            stats_df['balls_in_over'+str('_')+str(i)] = b2_o.islegal.sum()
            stats_df['wkts_in_over'+str('_')+str(i)] = b2_o.isBowlerWicket.sum()
            
        over_stats_df = over_stats_df.append(stats_df)
    
    
    
bowl_stats_df_inn2 = bowl_stats_df_inn2.merge(pre_stats_df, on=['match_id','innings','bowler'], how='left')
bowl_stats_df_inn2 = bowl_stats_df_inn2.merge(over_stats_df, on=['match_id','innings','bowler'], how='left')

# Step 1: Create bins for `run_rate`
bins = [-1, 6, 7.5, 8.75, 10, 12, 200]

def count_non_zero(values):
    return (values != 0).sum()

for i in range(4):
    # Create run rate bins
    bowl_stats_df_inn2['run_rate_bin_' + str(i)] = pd.cut(bowl_stats_df_inn2['inn2_run_rate_' + str(i)], bins=bins, right=True)
    bowl_stats_df_inn2['reqd_run_rate_bin_' + str(i)] = pd.cut(bowl_stats_df_inn2['over_RR_' + str(i)], bins=bins, right=True)
    
    


cols__ = ['over_0',
 'run_rate_bin_0',
          'reqd_run_rate_bin_0',
                    'inn2_bowl_wkts_0',
 'over_1',
 'run_rate_bin_1',
          'reqd_run_rate_bin_1',
                    'inn2_bowl_wkts_1',
 'over_2',
 'run_rate_bin_2',
          'reqd_run_rate_bin_2',
                    'inn2_bowl_wkts_2',
 'over_3',
 'run_rate_bin_3',
          'reqd_run_rate_bin_3',
                    'inn2_bowl_wkts_3'
 ]

## pick the probabilities from pre-computed excel

bowl_inn2_prob = pd.read_csv        ('/Users/roumyadas/Desktop/IPL_Simulation/Stats/impact_stats/bowl_stats_df_inn2_prob_bins.csv')


for col in bowl_inn2_prob:
    if str(col).startswith('prob_wicket')==False:
        bowl_inn2_prob[col] = bowl_inn2_prob[col].astype(str)
        bowl_stats_df_inn2[col] = bowl_stats_df_inn2[col].astype(str)

bowl_stats_df_inn2 = bowl_stats_df_inn2.merge(bowl_inn2_prob.drop_duplicates(), 
                                              on=cols__,
                                           how='left')
prob_cols = ['prob_wicket_0','prob_wicket_1','prob_wicket_2','prob_wicket_3']
bowl_stats_df_inn2[prob_cols] = bowl_stats_df_inn2[prob_cols].fillna(0).astype(float)

for i in range(4):
    
    bowl_stats_df_inn2['pre_ER_multiplier_'+str(i)] = np.where(bowl_stats_df_inn2['balls_in_over_'+str(i)]>0,
            bowl_stats_df_inn2['inn2_run_rate_'+str(i)]/\
                np.where(bowl_stats_df_inn2['runs_in_over_'+str(i)]>0,
                         6*bowl_stats_df_inn2['runs_in_over_'+str(i)]/bowl_stats_df_inn2['balls_in_over_'+str(i)],
                        0.5),np.nan)
    
    bowl_stats_df_inn2['pre_RR_multiplier_'+str(i)] = np.where(bowl_stats_df_inn2['balls_in_over_'+str(i)]>0,
            bowl_stats_df_inn2['over_RR_'+str(i)]/\
                np.where(bowl_stats_df_inn2['runs_in_over_'+str(i)]>0,
                         6*bowl_stats_df_inn2['runs_in_over_'+str(i)]/bowl_stats_df_inn2['balls_in_over_'+str(i)],
                        0.5),np.nan)    
    
    bowl_stats_df_inn2['pre_wkt_bonus_'+str(i)] = np.where(bowl_stats_df_inn2['wkts_in_over_'+str(i)]>0,
            np.where(bowl_stats_df_inn2['prob_wicket_'+str(i)]>0,
                     bowl_stats_df_inn2['wkts_in_over_'+str(i)]/bowl_stats_df_inn2['prob_wicket_'+str(i)],
                        5*bowl_stats_df_inn2['wkts_in_over_'+str(i)]),0)
    
    
    bowl_stats_df_inn2['pre_partnership_bonus_'+str(i)] = np.where((bowl_stats_df_inn2['balls_in_over_'+str(i)]>0) & 
                                                                   (bowl_stats_df_inn2['wkts_in_over_'+str(i)]>0),
            bowl_stats_df_inn2['inn2_partnership_runs_'+str(i)],0)
    
    
    
    

cols_ = bowl_stats_df_inn2.columns[bowl_stats_df_inn2.columns.str.contains('prpn|multiplier|bonus')]


bowl_stats_df_inn2.iloc[0]#isna().sum()

for col in bowl_stats_df_inn2.columns:
    if '_bin_' not in str(col):
        bowl_stats_df_inn2[col] = bowl_stats_df_inn2[col].fillna(0)

bowl_wkts_df = df2[df2.isBowlerWicket==1][['bowler','match_id','striker','partnership_runs']].drop_duplicates()        .sort_values(by=['match_id','bowler']).reset_index(drop=True)

bowl_wkts_df = bowl_wkts_df.merge(bat_impact[['match_id','striker','runs','impact_runs']], 
                                  on=['match_id','striker'], how='left')


#bowl_wkts_df

median_imp_runs = bowl_wkts_df.groupby('match_id')['impact_runs'].median().reset_index()
median_imp_runs.rename(columns={'impact_runs':'median_impact_runs'}, inplace=True)
    
bowl_wkts_df = bowl_wkts_df.merge(median_imp_runs, on='match_id',how='left')

##
bowl_wkts_df['median_impact_runs'] = bowl_wkts_df['median_impact_runs'].replace(0, 1)

bowl_wkts_df['wkt_impact'] = bowl_wkts_df['impact_runs']/bowl_wkts_df['median_impact_runs']-1
bowl_wkts_df['runs_bonus'] = bowl_wkts_df['runs'].apply(score_bonus)
bowl_wkts_df['partnership_bonus'] = bowl_wkts_df['partnership_runs'].apply(partnership_bonus)

bowl_wkts_df['wkt_multiplier'] = (bowl_wkts_df['wkt_impact'].apply(transform_calc)+bowl_wkts_df['runs_bonus'])*                                    bowl_wkts_df['partnership_bonus']


wkt_value_df = bowl_wkts_df.groupby(['match_id','bowler'])['wkt_multiplier'].apply(geometric_mean).reset_index()

bowl_stats_df_inn2 = bowl_stats_df_inn2.merge(wkt_value_df, on=['match_id','bowler'], how='left')
bowl_stats_df_inn2['wkt_multiplier'].fillna(0, inplace=True)

bowl_stats_df_inn2['bowl_impact'] = None

for index,row in bowl_stats_df_inn2.iterrows():
    
    ER_multiplier = (row['ball_prpn']/row['run_prpn'])**(1/2.5)
    RR_compare_prpn = ((row['target']/20)/(6*row['runs']/row['balls']))
    SR_multiplier = (row['wicket_prpn']/row['ball_prpn'])**(1/10)
    
    wt_total = (row['ball_prpn']) #**0.5
    
    prpn_points = RR_compare_prpn+(row['Bp_StRo_compare_prpn']+row['BpE_compare_prpn'])*wt_total*(1-wt_total)
    
    
    wkt_points = row['wkt_points']*row['wkt_multiplier']*SR_multiplier*(1-wt_total)
    ER_points = row['ER_points']*ER_multiplier*wt_total#*(1-wt_total)
    dot_points = row['dot_points']*row['dot_compare_prpn']*wt_total#*(1-wt_total)
    bpb_points = row['bpb_points']*row['BpB_compare_prpn']*wt_total#*(1-wt_total)
    
    
    addition_points = []
    
    for i in range(4):
        if (row['balls_in_over_'+str(i)]>0):
            wt_pre = row['inn2_balls_'+str(i)]/row['inn2_balls']
            #wt_p = row['inn2_partnership_balls_'+str(i)]/row['inn2_balls']
            wt_remain = (120-row['inn2_balls_'+str(i)])/row['inn2_balls']
            
            
            ER_m = row['pre_ER_multiplier_'+str(i)]
            #P_m = row['pre_partnership_bonus_'+str(i)]
            W_m = row['pre_wkt_bonus_'+str(i)]
            RR_m = row['pre_RR_multiplier_'+str(i)]
            
            
            pre_ER_mutiplier = -1+wt_pre*ER_m**(np.where(ER_m>1,0.5,2))
            #pre_P_multiplier = -1+wt_p*P_m**0.25
            pre_W_multiplier = -1+wt_pre*W_m**0.25
            pre_RR_multiplier = -1+wt_remain*RR_m**0.25
            
            total_addition = pre_ER_mutiplier+pre_W_multiplier+pre_RR_multiplier#+pre_P_multiplier
            addition_points.append(total_addition)
            
    final_addition_points = wkt_points+prpn_points+ER_points+dot_points+bpb_points+sum(addition_points)
    
    final_impact = final_addition_points
    
    
    bowl_stats_df_inn2.at[index, 'bowl_impact'] = final_impact #[final_impact,ER_points]
                              

cols_view = ['match_id', 'innings', 'bowler', 'team', 'opposition', 'runs', 'balls',
       'wickets','wkt_multiplier','bowl_impact']

bowl_impact2 = bowl_stats_df_inn2[cols_view]
bowl_impact2['impact_wkts'] = bowl_impact2['wickets']*bowl_impact2['wkt_multiplier']



bowl_impact = pd.concat([bowl_impact,bowl_impact2], axis=0, ignore_index=True).reset_index(drop=True)

bowl_impact = bowl_impact.sort_values(by=['match_id','innings']).reset_index(drop=True)


# In[ ]:





# ##### total impact

# In[16]:


cols_view = ['match_id', 'innings', 'striker', 'team', 'opposition',
       'batting_position', 'runs', 'balls','SR', 'mode_of_dismissal', 'win_fl_inn1',
       'win_fl_inn2', 'impact_runs','adjusted_runs']

total_impact = bat_impact[cols_view].merge(bowl_impact, left_on=['match_id','striker'], right_on=['match_id','bowler'], how='outer')
total_impact = total_impact.rename(columns={'striker':'batter','team_x':'bat_team','team_y':'bowl_team','opposition_x':'bat_opposition','opposition_y':'bowl_opposition','innings_x':'inning_bat','innings_y':'inning_bowl',
                                            'runs_y':'runs_conceeded','balls_y':'balls_bowled','runs_x':'bat_runs','balls_x':'balls_faced',
                                            'impact_runs':'bat_impact'})
#total_impact.drop(['opposition_y'],axis=1,inplace=True)

total_impact['win_fl_inn1'] = total_impact.groupby('match_id')['win_fl_inn1'].ffill()
total_impact['win_fl_inn2'] = total_impact.groupby('match_id')['win_fl_inn2'].ffill()

total_impact['win_fl_inn1'] = total_impact.groupby('match_id')['win_fl_inn1'].bfill()
total_impact['win_fl_inn2'] = total_impact.groupby('match_id')['win_fl_inn2'].bfill()


total_impact['winner'] = None
total_impact['team'] = None
total_impact['opposition'] = None

for index,row in total_impact.iterrows():

    team = [row['bat_team'] if pd.isna(row['bat_team'])==False else row['bowl_team']]
    opposition = [row['bat_opposition'] if pd.isna(row['bat_opposition'])==False else row['bowl_opposition']]

    total_impact.at[index, 'team'] = team[0]
    total_impact.at[index, 'opposition'] = opposition[0]

    if pd.isna(row['inning_bat'])==True:
        total_impact.at[index,'inning_bat'] = np.where(row['inning_bowl']==2,1,2)
    if pd.isna(row['inning_bowl'])==True:
        total_impact.at[index,'inning_bowl'] =  np.where(row['inning_bat']==2,1,2)

    total_impact.at[index,'bat_team'] = team[0]
    total_impact.at[index,'bowl_team'] = team[0]

    total_impact.at[index,'bat_opposition'] = opposition[0]
    total_impact.at[index,'bowl_opposition'] = opposition[0]

    if pd.isna(row['bowler'])==True:
        total_impact.at[index,'bowler'] = row['batter']
    elif pd.isna(row['batter'])==True:
        total_impact.at[index,'batter'] = row['bowler']



    if row['win_fl_inn1'] == 1:
        if row['inning_bat']==1:
            total_impact.at[index,'winner'] = row['bat_team']
        else:
            total_impact.at[index,'winner'] = row['bowl_opposition']

    elif row['win_fl_inn2'] == 1:
        if row['inning_bat']==1:
            total_impact.at[index,'winner'] = row['bat_opposition']
        else:
            total_impact.at[index,'winner'] = row['bat_team']

total_impact['winner'] = total_impact.groupby('match_id')['winner'].ffill()
total_impact['winner'] = total_impact.groupby('match_id')['winner'].bfill()

total_impact = total_impact.sort_values(by=['match_id','inning_bat'])#.head(22)#[22:44]

total_impact = total_impact.rename(columns={'batter':'player'})

cols_to_drop = ['bat_team', 'bat_opposition','win_fl_inn1', 'win_fl_inn2','bowler','bowl_team',
       'bowl_opposition']

total_impact.drop(cols_to_drop,axis=1,inplace=True)

columns = ['bowl_impact','bat_impact']

for column in columns:
    total_impact[column].fillna(0, inplace=True)

total_impact['total_impact'] = total_impact['bowl_impact'] + total_impact['bat_impact']
total_impact = total_impact.round(2)
total_impact.fillna('', inplace=True)

team_impact = pd.pivot_table(data=total_impact, index=['match_id','team'], values='total_impact',
              aggfunc='sum').reset_index()
team_impact.columns = ['match_id','team','team_impact']


# In[ ]:





# ##### presentable summary of impact points

# Player	Team	
# TI
# Runs
# I. Runs
# B. Impact
# Bowl
# I. Wkts
# Bo. Impact

# In[17]:


total_impact_final = pd.DataFrame()

total_impact_final['Player'] = total_impact['player']
total_impact_final['TI'] = total_impact['total_impact']
total_impact_final['Team'] = total_impact['team']
total_impact_final['Runs'] = total_impact[['bat_runs','balls_faced']].apply(lambda x: 
                                                                f"{int(x[0])}({int(x[1])})" if x[0]!=''
                                                                            else '', axis=1)

total_impact_final['I.Runs'] = total_impact['adjusted_runs']
total_impact_final['B.Impact'] = total_impact['bat_impact']

total_impact_final['Bowl'] = total_impact[['wickets','runs_conceeded']].apply(lambda x: 
                                                                f"{int(x[0])}-{int(x[1])}" if x[0]!=''
                                                                            else '', axis=1)

total_impact_final['I.Wkts'] = total_impact['impact_wkts']
total_impact_final['Bo.Impact'] = total_impact['bowl_impact']

total_impact_final = total_impact_final.sort_values('TI', ascending=False).reset_index(drop=True)


# total_impact_final

# In[18]:


total_impact_final['Rank'] = total_impact_final.index+1

total_impact_final['desc'] = total_impact_final[['Player', 'TI', 'Team', 'Runs', 'I.Runs',
                        'B.Impact', 
                        'Bowl', 'I.Wkts', 'Bo.Impact','Rank']].apply(lambda x:
            f"{x[-1]}> {x[0]}({x[2]}) - TI: {x[1]} - Runs: {x[3]} [I.Runs= {x[4]}, B.I.= {x[5]}] \n Bowl: {x[6]} [I.Wkts= {x[7]}, Bo.I= {x[8]}]",
                                                                    axis=1)


# In[22]:


output_file = f"/Users/roumyadas/Desktop/IPL_Simulation/Season_03/total_impact/{match_id}_impact.txt"
    #output_file = "/Users/roumyadas/Desktop/IPL_Simulation/experimentation/matchcard_" + str(match_id) + ".txt"

# Redirect the output
with open(output_file, "w") as f:
    with redirect_stdout(f):

        #line = " | ".join(total_impact_final.columns)
        print('``` Impact Points list ```')

        # Print rows one by one
        for _, row in total_impact_final.iterrows():
            desc = row['desc']
            print('```',desc,'```')  
            print('---' * 10)
            


# In[26]:


path__ = '/Users/roumyadas/Desktop/IPL_Simulation/Season_03/Stats/Impact_indi_S03.xlsx'

existing_impact_file = pd.read_excel(path__)

total_impact_final['Match'] = match_id

new_impact_file = pd.concat([existing_impact_file,total_impact_final.drop('desc', axis=1)], 
                            axis=0, ignore_index=True)

new_impact_file.to_excel(path__, index=None)


# In[ ]:




