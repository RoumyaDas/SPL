#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import glob
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# In[2]:


bat_stat = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/updates_/separate_stats.xlsx', 
                         sheet_name='Bat')
bowl_stat = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/updates_/separate_stats.xlsx', 
                          sheet_name='Bowl')


# ## loading

# In[3]:


df_01 = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_01/Stats/df_all_round_sim.csv')
df_curr = pd.DataFrame(columns=df_01.columns.tolist())
try:
    df_curr = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/df_all_round_sim.csv')
except FileNotFoundError:
    print("df_curr file not found, proceeding with df_01 only.")

df_all = pd.concat([df_01,df_curr], axis=0)
df_all.reset_index(drop=True, inplace=True)


# ## bowling

# In[4]:


bowler_stats = df_all.groupby('bowler').agg(   ##,'innings'
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

bowler_stats['overs'] = bowler_stats['balls'].apply(lambda x: str(x//6)+'.'+str(x%6))
#########ADDING 3+,4+,5+ wkts#########
mbm_bowl = df_all.groupby(['bowler','match_id'])['isBowlerWicket'].sum().reset_index().sort_values(by='bowler')

_3plus = mbm_bowl[mbm_bowl.isBowlerWicket>=3].groupby('bowler')['match_id'].count().reset_index()
#_4plus = mbm_bowl[mbm_bowl.isBowlerWicket>=4].groupby('bowler')['match_id'].count().reset_index()
_5plus = mbm_bowl[mbm_bowl.isBowlerWicket>=5].groupby('bowler')['match_id'].count().reset_index()

_3plus.columns = ['bowler','3+_wkts']
#_4plus.columns = ['bowler','4+_wkts']
_5plus.columns = ['bowler','5+_wkts']


bowler_stats = bowler_stats.merge(_3plus, on='bowler', how='left')
#bowler_stats = bowler_stats.merge(_4plus, on='bowler', how='left')
bowler_stats = bowler_stats.merge(_5plus, on='bowler', how='left')

#bowler_stats[['3+_wkts','4+_wkts','5+_wkts']] = bowler_stats[['3+_wkts','4+_wkts','5+_wkts']].fillna(0).astype(int)
bowler_stats[['3+_wkts','5+_wkts']] =                     bowler_stats[['3+_wkts','5+_wkts']].fillna(0).astype(int)

mbm_ball_bat = df_all.groupby(['bowler','match_id'])[['runs_conceeded','islegal','isBowlerWicket']]                                    .sum().reset_index().sort_values(by='bowler')

mbm_ball_bat = mbm_ball_bat.rename(columns={'bowler':'player'})


mbm_ball_bat['isBowlerWicket'] = mbm_ball_bat['isBowlerWicket'].fillna(0).astype(int)

mbm_ball_bat = mbm_ball_bat.sort_values(by=['player', 'isBowlerWicket', 'runs_conceeded'], 
                                               ascending=[True, False, True])

# Get the index of the highest score for each striker (resolving ties using fewer balls)
idx = mbm_ball_bat.groupby('player')['isBowlerWicket'].idxmax()

# Filter the rows
most_wkts = mbm_ball_bat.loc[idx]

most_wkts['best_performance'] = most_wkts['isBowlerWicket'].astype(str)+ str('-')+            most_wkts['runs_conceeded'].astype(str)+str(' (')+most_wkts['islegal'].astype(str)+str(')')
        

most_wkts = most_wkts.rename(columns={'player':'bowler'})

bowler_stats = bowler_stats.merge(most_wkts[['bowler','best_performance']], on='bowler',how='left')
teams_played = df_all.groupby('bowler')['bowling_team'].unique().reset_index()

bowler_stats = bowler_stats.merge(teams_played, on='bowler',how='left')

bowler_stats = bowler_stats.round(2)

collist = ['bowler','num_innings','runs','overs', 'wkts','economy', 'strike_rate', 'bpb', 'dot_%', '3+_wkts',
       '5+_wkts','best_performance','bowling_team']

bowler_stats = bowler_stats[collist]
bowler_stats['3+_wkts'] = bowler_stats['3+_wkts'] - bowler_stats['5+_wkts']

bowler_stats = bowler_stats.rename(columns={'bowler':'player','num_innings':'innings','runs':'runs_conceded',
                                           '3+_wkts':'3w_hauls','5+_wkts':'5w_hauls',
                                            'best_performance':'best_figures','bowling_team':'teams_played_for'})
bowler_stats = bowler_stats.sort_values(['wkts','economy'], ascending=[False, True]).reset_index(drop=True)


# ## batting

# In[5]:


batter_stats = df_all.groupby('striker').agg(  ##,'innings'
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

#_30plus = mbm_bat[mbm_bat.runs_off_bat>=30].groupby('striker')['match_id'].count().reset_index()
_50plus = mbm_bat[mbm_bat.runs_off_bat>=50].groupby('striker')['match_id'].count().reset_index()
_100plus = mbm_bat[mbm_bat.runs_off_bat>=100].groupby('striker')['match_id'].count().reset_index()

#_30plus.columns = ['striker','30+_scores']
_50plus.columns = ['striker','50+_scores']
_100plus.columns = ['striker','100+_scores']

#batter_stats = batter_stats.merge(_30plus, on='striker', how='left')
batter_stats = batter_stats.merge(_50plus, on='striker', how='left')
batter_stats = batter_stats.merge(_100plus, on='striker', how='left')

#batter_stats[['30+_scores','50+_scores','100+_scores']] = \
#                    batter_stats[['30+_scores','50+_scores','100+_scores']].fillna(0).astype(int)
batter_stats[['50+_scores','100+_scores']] = batter_stats[['50+_scores','100+_scores']].fillna(0).astype(int)

#########ADDING HIGHEST SCORES##############
mbm_bat_ball = df_all.groupby(['striker','match_id'])[['runs_off_bat','is_faced_by_batter']]                                    .sum().reset_index().sort_values(by='striker')

mbm_bat_ball = mbm_bat_ball.rename(columns={'striker':'player'})

mbm_out = df_all.groupby(['player_dismissed','match_id'])['start_date']                                    .count().reset_index().sort_values(by='player_dismissed')

mbm_out = mbm_out.rename(columns={'player_dismissed':'player','start_date':'out'})
mbm_out['out'] = mbm_out['out'].fillna(0).astype(int)

mbm = mbm_bat_ball.merge(mbm_out, on=['player','match_id'], how='left')
mbm['out'] = mbm['out'].fillna(0).astype(int)

mbm['out_str'] = ''
mbm.loc[mbm['out']==0,'out_str'] = '*'

mbm = mbm.sort_values(by=['player', 'runs_off_bat', 'is_faced_by_batter'], 
                                               ascending=[True, False, True])

# Get the index of the highest score for each striker (resolving ties using fewer balls)
idx = mbm.groupby('player')['runs_off_bat'].idxmax()

# Filter the rows
highest_scores = mbm.loc[idx]

highest_scores['high_score'] = highest_scores['runs_off_bat'].astype(str)+ highest_scores['out_str']+ str(' (')+                                    highest_scores['is_faced_by_batter'].astype(str)+str(')')
        

highest_scores = highest_scores.rename(columns={'player':'striker'})

batter_stats = batter_stats.merge(highest_scores[['striker','high_score']], on='striker',how='left')
batter_stats = batter_stats.round(2)

teams_played = df_all.groupby('striker')['batting_team'].unique().reset_index()

batter_stats = batter_stats.merge(teams_played, on='striker',how='left')

collist = ['striker','num_innings','runs','balls','strike_rate', 'bat_avg','bpb', 'dot_%', '50+_scores',
       '100+_scores','high_score']

batter_stats = batter_stats[collist]

teams_played = df_all.groupby('striker')['batting_team'].unique().reset_index()

batter_stats = batter_stats.merge(teams_played, on='striker',how='left')
batter_stats['50+_scores'] = batter_stats['50+_scores'] - batter_stats['100+_scores']
batter_stats = batter_stats.round(2)

batter_stats = batter_stats.rename(columns={'striker':'player','num_innings':'innings','balls':'balls_played',
                                            '50+_scores':'50s','100+_scores':'100s',
                                           'high_score':'highest_score','batting_team':'teams_played_for'})
batter_stats = batter_stats.sort_values(['runs','strike_rate'], ascending=[False, False]).reset_index(drop=True)


# ## fielding

# In[6]:


## catches

catches_df = df_all[df_all['wicket_event']=='Caught'].groupby('fielder')['wicket_event'].count().reset_index()

#catches_df
catches_df.columns = ['player','#catches']
catches_df = catches_df.sort_values('#catches',ascending=False)

## runouts
runout_ = df_all[(df_all['wicket_event']=='Stumped/Runout by Keeper')|(df_all['wicket_type']=='runout')].dropna(subset=['fielder'])

if runout_.shape[0]>0:
    runout_df = runout_.groupby('fielder')['player_dismissed'].count().reset_index()
    
    runout_df.columns = ['player','#runout/stumping']
    catches_df = catches_df.merge(runout_df,on=['player'],how='outer')
    catches_df = catches_df.fillna(0)


# ## into ONE file (career)

# In[7]:


excel_filename = '/Users/roumyadas/Desktop/IPL_Simulation/Season_02/Stats/career.xlsx'

# Use ExcelWriter to write multiple sheets
with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
    batter_stats.to_excel(writer, sheet_name='Batting', index=False)
    bowler_stats.to_excel(writer, sheet_name='Bowling', index=False)
    catches_df.to_excel(writer, sheet_name='Fielding', index=False)


# In[9]:


excel_filename = '/Users/roumyadas/Desktop/IPL_Simulation/Season_02/Stats/career.xlsx'


# Dictionary mapping sheet names to DataFrames
sheets_data = {
    'Batting': batter_stats,
    'Bowling': bowler_stats, 
    'Fielding': catches_df
}

with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
    # Writing all sheets
    for sheet_name, df in sheets_data.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Get workbook
    workbook = writer.book  

    # Define formats
    bold_format = workbook.add_format({'bold': True})  # Bold text
    #large_font_format = workbook.add_format({'font_size': 14})  # Increased font size
    #red_text_format = workbook.add_format({'font_color': 'red'})  # Red text

    # Apply formatting to each sheet
    for sheet_name, df in sheets_data.items():
        worksheet = writer.sheets[sheet_name]
        
        # 1️⃣ Bold all column names (header row)
        for col_idx, col_name in enumerate(df.columns):
            worksheet.write(0, col_idx, col_name, bold_format)
        
        # Adjust column widths dynamically
        for col_idx, col_name in enumerate(df.columns):
            max_length = max(df[col_name].astype(str).apply(len).max(), len(col_name))  # Max of column values & header
            worksheet.set_column(col_idx, col_idx, max_length + 2)  # Adding padding for readability
            
        # 7️⃣ Freeze the first row of every sheet
        worksheet.freeze_panes(1, 0)
        
        # 8️⃣ **Add Filter to all columns**
        worksheet.autofilter(0, 0, 0, len(df.columns) - 1)  # Apply filter to the first row across all columns


print(f"Excel file '{excel_filename}' created successfully with formatting!")


# In[ ]:




