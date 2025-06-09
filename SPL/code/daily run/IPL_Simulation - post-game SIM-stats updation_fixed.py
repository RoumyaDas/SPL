#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import glob
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import warnings
warnings.filterwarnings('ignore')


# In[2]:


def try_float_2(value):
    try:
        val = np.round(value,2)
    except:
        val = value
    return val


# In[3]:


df_01 = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_01/Stats/df_all_round_sim.csv')
df_curr = pd.DataFrame(columns=df_01.columns.tolist())
try:
    df_curr = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/df_all_round_sim.csv')
    #df_curr = df_curr[df_01.columns.tolist()]
except FileNotFoundError:
    print("df_curr file not found, proceeding with df_01 only.")

df_all = pd.concat([df_01,df_curr], axis=0)
df_all.reset_index(drop=True, inplace=True)


df_all['phase'] = np.where(df_all['legal_balls_bowled']<=36, 'pp', 
                        np.where(df_all['legal_balls_bowled']>=90, 'death',
                            'middle'))


# In[4]:


player_list = pd.read_excel('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/player_list.xlsx',
                           sheet_name='season_02')

players_list = player_list['Func_Name'].dropna().tolist()


# ## form factor

# #Note : to run both on Sim stats & Entire stats

# In[5]:


#df_ = pd.read_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/t20_pl_g.csv')
df_all_ = df_all 
#df_all_ = pd.concat([df_,df_all],axis=0)
df_all_ = df_all_.drop_duplicates().reset_index(drop=True)


# In[6]:


bat_pl = df_all_[df_all_.striker.isin(players_list)]
bowl_pl = df_all_[df_all_.bowler.isin(players_list)]

bat_pl_1 = bat_pl[bat_pl.innings==1]
bat_pl_2 = bat_pl[bat_pl.innings==2]

bowl_pl_1 = bowl_pl[bowl_pl.innings==1]
bowl_pl_2 = bowl_pl[bowl_pl.innings==2]


# Initialize dictionaries to store match IDs
batter_match_id_1 = {}
batter_match_id_2 = {}
bowler_match_id_1 = {}
bowler_match_id_2 = {}

# Collect last 5 match IDs for each batter in bat_pl_1
for batter in bat_pl_1.striker.unique():
    matches = bat_pl_1[bat_pl_1.striker == batter].match_id.unique()[-5:].tolist()
    batter_match_id_1[batter] = matches

# Collect last 5 match IDs for each batter in bat_pl_2
for batter in bat_pl_2.striker.unique():
    matches = bat_pl_2[bat_pl_2.striker == batter].match_id.unique()[-5:].tolist()
    batter_match_id_2[batter] = matches

# Collect last 5 match IDs for each bowler in bowl_pl_1
for bowler in bowl_pl_1.bowler.unique():
    matches = bowl_pl_1[bowl_pl_1.bowler == bowler].match_id.unique()[-5:].tolist()
    bowler_match_id_1[bowler] = matches

# Collect last 5 match IDs for each bowler in bowl_pl_2
for bowler in bowl_pl_2.bowler.unique():
    matches = bowl_pl_2[bowl_pl_2.bowler == bowler].match_id.unique()[-5:].tolist()
    bowler_match_id_2[bowler] = matches

df_bat_1 = pd.DataFrame()

for batter_name in players_list:
    last_5_matches = batter_match_id_1.get(batter_name, [1])
    df_sub = bat_pl_1[(bat_pl_1.striker==batter_name)&(bat_pl_1.match_id.isin(last_5_matches))]
    if df_sub.shape[0]>0:
        df_sub.reset_index(drop=True, inplace=True)
        df_bat_1 = df_bat_1.append(df_sub)
    else:
        continue
        
df_bat_2 = pd.DataFrame()

for batter_name in players_list:
    last_5_matches = batter_match_id_2.get(batter_name, [2])
    df_sub = bat_pl_2[(bat_pl_2.striker==batter_name)&(bat_pl_2.match_id.isin(last_5_matches))]
    if df_sub.shape[0]>0:
        df_sub.reset_index(drop=True, inplace=True)
        df_bat_2 = df_bat_2.append(df_sub)
    else:
        continue
        
df_bowl_1 = pd.DataFrame()

for bowler_name in players_list:
    last_5_matches = bowler_match_id_1.get(bowler_name, [1])
    df_sub = bowl_pl_1[(bowl_pl_1.bowler==bowler_name)&(bowl_pl_1.match_id.isin(last_5_matches))]
    if df_sub.shape[0]>0:
        df_sub.reset_index(drop=True, inplace=True)
        df_bowl_1 = df_bowl_1.append(df_sub)
    else:
        continue
        
df_bowl_2 = pd.DataFrame()

for bowler_name in players_list:
    last_5_matches = bowler_match_id_2.get(bowler_name, [2])
    df_sub = bowl_pl_2[(bowl_pl_2.bowler==bowler_name)&(bowl_pl_2.match_id.isin(last_5_matches))]
    if df_sub.shape[0]>0:
        df_sub.reset_index(drop=True, inplace=True)
        df_bowl_2 = df_bowl_2.append(df_sub)
    else:
        continue
        
df_bowl_1['runs_conceeded'] = df_bowl_1['runs_off_bat']+df_bowl_1['wides']+df_bowl_1['noballs']
df_bowl_2['runs_conceeded'] = df_bowl_2['runs_off_bat']+df_bowl_2['wides']+df_bowl_2['noballs']

batter_stats_1_form = df_bat_1.groupby('striker').agg(

num_innings = ('match_id','nunique'),
    runs = ('runs_off_bat','sum'),
    balls = ('is_faced_by_batter' ,'sum'),
    outs = ('is_striker_Out','sum'),
    bat_order = ('striker_batting_position', lambda x: x.mode().iloc[0] if not x.mode().empty else None)
    
).reset_index()

batter_stats_2_form = df_bat_2.groupby('striker').agg(

num_innings = ('match_id','nunique'),
    runs = ('runs_off_bat','sum'),
    balls = ('is_faced_by_batter' ,'sum'),
    outs = ('is_striker_Out','sum'),
    bat_order = ('striker_batting_position', lambda x: x.mode().iloc[0] if not x.mode().empty else None)
    
).reset_index()

bowler_stats_1_form = df_bowl_1.groupby('bowler').agg(

num_innings = ('match_id','nunique'),
    runs = ('runs_conceeded','sum'),
    balls = ('islegal' ,'sum'),
    wkts = ('isBowlerWicket','sum'),
    bowl_phase = ('phase', lambda x: x.mode().iloc[0] if not x.mode().empty else None)
    
).reset_index()

bowler_stats_2_form = df_bowl_2.groupby('bowler').agg(

num_innings = ('match_id','nunique'),
    runs = ('runs_conceeded','sum'),
    balls = ('islegal' ,'sum'),
    wkts = ('isBowlerWicket','sum'),
    bowl_phase = ('phase', lambda x: x.mode().iloc[0] if not x.mode().empty else None)
    
).reset_index()

batter_stats_1_form['bat_avg'] = batter_stats_1_form['runs']/batter_stats_1_form['outs']
batter_stats_2_form['bat_avg'] = batter_stats_2_form['runs']/batter_stats_2_form['outs']

batter_stats_1_form['bat_sr'] = 100*batter_stats_1_form['runs']/batter_stats_1_form['balls']
batter_stats_2_form['bat_sr'] = 100*batter_stats_2_form['runs']/batter_stats_2_form['balls']

bowler_stats_1_form['bowl_sr'] = bowler_stats_1_form['balls']/bowler_stats_1_form['wkts']
bowler_stats_2_form['bowl_sr'] = bowler_stats_2_form['balls']/bowler_stats_2_form['wkts']

bowler_stats_1_form['bowl_eco'] = 6*bowler_stats_1_form['runs']/bowler_stats_1_form['balls']
bowler_stats_2_form['bowl_eco'] = 6*bowler_stats_2_form['runs']/bowler_stats_2_form['balls']

batter_stats_1_form['bat_avg'] = batter_stats_1_form.apply(
    lambda row: row['runs'] if np.isinf(row['bat_avg']) else row['bat_avg'], axis=1
)

batter_stats_1_form['bat_avg'] = batter_stats_1_form['bat_avg'].fillna(0)

batter_stats_2_form['bat_avg'] = batter_stats_2_form.apply(
    lambda row: row['runs'] if np.isinf(row['bat_avg']) else row['bat_avg'], axis=1
)

batter_stats_2_form['bat_avg'] = batter_stats_2_form['bat_avg'].fillna(0)

mult_1 = 0.2
mult_2 = 0.01
mult_3 = 0.3

batter_stats_1_form['a'] = ((0.5*batter_stats_1_form['bat_avg'])**mult_1)*((batter_stats_1_form['bat_order']**0.5)**-mult_1)
batter_stats_1_form['b'] = ((batter_stats_1_form['bat_sr']/100)**mult_3)*((batter_stats_1_form['bat_order']**0.5)**-mult_1)
batter_stats_1_form['c'] = (batter_stats_1_form['balls']*(batter_stats_1_form['bat_order']**0.5))**mult_2


batter_stats_1_form['form'] = 0.5*(batter_stats_1_form['a']+batter_stats_1_form['b'])*batter_stats_1_form['c']

batter_stats_1_form['form'] = batter_stats_1_form['form']/batter_stats_1_form['form'].mean()

batter_stats_1_form['form'] = batter_stats_1_form['form']**0.75

batter_stats_1_form['form'] = batter_stats_1_form['form']/batter_stats_1_form['form'].mean()


batter_stats_2_form['a'] = ((0.5*batter_stats_2_form['bat_avg'])**mult_1)*((batter_stats_2_form['bat_order']**0.5)**-mult_1)
batter_stats_2_form['b'] = ((batter_stats_2_form['bat_sr']/200)**mult_3)*((batter_stats_2_form['bat_order']**0.5)**-mult_1)
batter_stats_2_form['c'] = (batter_stats_2_form['balls']*(batter_stats_2_form['bat_order']**0.5))**mult_2


batter_stats_2_form['form'] = 0.5*(batter_stats_2_form['a']+batter_stats_2_form['b'])*batter_stats_2_form['c']

batter_stats_2_form['form'] = batter_stats_2_form['form']/batter_stats_2_form['form'].mean()

batter_stats_2_form['form'] = batter_stats_2_form['form']**0.75

batter_stats_2_form['form'] = batter_stats_2_form['form']/batter_stats_2_form['form'].mean()



batter_stats_1_form['form'] = np.where(batter_stats_1_form.balls<5, 0, batter_stats_1_form['form'])
batter_stats_2_form['form'] = np.where(batter_stats_2_form.balls<5, 0, batter_stats_2_form['form'])

##bowler

bowler_stats_1_form['bowl_eco'] = bowler_stats_1_form.apply(
    lambda row: row['runs'] if np.isinf(row['bowl_eco']) else row['bowl_eco'], axis=1
)

bowler_stats_1_form['bowl_eco'] = bowler_stats_1_form['bowl_eco'].fillna(0)

bowler_stats_2_form['bowl_eco'] = bowler_stats_2_form.apply(
    lambda row: row['runs'] if np.isinf(row['bowl_eco']) else row['bowl_eco'], axis=1
)

bowler_stats_2_form['bowl_eco'] = bowler_stats_2_form['bowl_eco'].fillna(0)

bowler_stats_1_form['bowl_sr'] = bowler_stats_1_form.apply(
    lambda row: row['runs'] if np.isinf(row['bowl_sr']) else row['bowl_sr'], axis=1
)

#bowler_stats_1_form['bowl_sr'] = bowler_stats_1_form['bowl_eco'].fillna(0)

bowler_stats_2_form['bowl_sr'] = bowler_stats_2_form.apply(
    lambda row: row['runs'] if np.isinf(row['bowl_sr']) else row['bowl_sr'], axis=1
)


bowler_stats_1_form['a'] = np.where(bowler_stats_1_form['bowl_phase']=='middle', bowler_stats_1_form['bowl_eco']*1.05,
                                (np.where(bowler_stats_1_form['bowl_phase']=='death', bowler_stats_1_form['bowl_eco']*0.95,
                                        bowler_stats_1_form['bowl_eco']*0.99)))

bowler_stats_1_form['b'] = np.where(bowler_stats_1_form['bowl_phase']=='middle', bowler_stats_1_form['bowl_sr'],
                                (np.where(bowler_stats_1_form['bowl_phase']=='death', bowler_stats_1_form['bowl_sr']*0.95,
                                        bowler_stats_1_form['bowl_sr']*0.95)))

bowler_stats_1_form['c'] = np.where(bowler_stats_1_form['wkts']>0,bowler_stats_1_form['wkts']/15,1/15)

bowler_stats_1_form['d'] = (1/(bowler_stats_1_form['a']))*(1/(bowler_stats_1_form['b']))*                                                    (bowler_stats_1_form['c'])


bowler_stats_1_form['form'] = bowler_stats_1_form['d']**0.1
#**bowler_stats_1_form['d']

bowler_stats_1_form['form'] = bowler_stats_1_form['form']/bowler_stats_1_form['form'].mean()
bowler_stats_1_form['form'] = np.where(bowler_stats_1_form.balls<12, 0, bowler_stats_1_form['form'])



bowler_stats_2_form['a'] = np.where(bowler_stats_2_form['bowl_phase']=='middle', bowler_stats_2_form['bowl_eco']*1.05,
                                (np.where(bowler_stats_2_form['bowl_phase']=='death', bowler_stats_2_form['bowl_eco']*0.95,
                                        bowler_stats_2_form['bowl_eco']*0.99)))

bowler_stats_2_form['b'] = np.where(bowler_stats_2_form['bowl_phase']=='middle', bowler_stats_2_form['bowl_sr'],
                                (np.where(bowler_stats_2_form['bowl_phase']=='death', bowler_stats_2_form['bowl_sr']*0.95,
                                        bowler_stats_2_form['bowl_sr']*0.95)))

bowler_stats_2_form['c'] = np.where(bowler_stats_2_form['wkts']>0,bowler_stats_2_form['wkts']/15,1/15)

bowler_stats_2_form['d'] = (1/(bowler_stats_2_form['a']))*(1/(bowler_stats_2_form['b']))*                                                    (bowler_stats_2_form['c'])


bowler_stats_2_form['form'] = bowler_stats_2_form['d']**0.1
#**bowler_stats_2_form['d']

bowler_stats_2_form['form'] = bowler_stats_2_form['form']/bowler_stats_2_form['form'].mean()
bowler_stats_2_form['form'] = np.where(bowler_stats_2_form.balls<12, 0, bowler_stats_2_form['form'])


bowler_stats_1_form['form'] = np.where(bowler_stats_1_form.balls<12, 0, bowler_stats_1_form['form'])
bowler_stats_2_form['form'] = np.where(bowler_stats_2_form.balls<12, 0, bowler_stats_2_form['form'])


batter_stats_1_form_trimmed = batter_stats_1_form[batter_stats_1_form.balls>=5].drop(['a','b','c'],axis=1)
batter_stats_2_form_trimmed = batter_stats_2_form[batter_stats_2_form.balls>=5].drop(['a','b','c'],axis=1)

bowler_stats_1_form_trimmed = bowler_stats_1_form[bowler_stats_1_form.balls>=12].drop(['a','b','c','d'],axis=1)
bowler_stats_2_form_trimmed = bowler_stats_2_form[bowler_stats_2_form.balls>=12].drop(['a','b','c','d'],axis=1)


# #### match-specific form

# In[7]:


bat_pl = df_all_[df_all_.striker.isin(players_list)]
bowl_pl = df_all_[df_all_.bowler.isin(players_list)]

batter_match_id = {}
bowler_match_id = {}

# Collect last 5 match IDs for each batter in bat_pl
for batter in bat_pl.striker.unique():
    matches = bat_pl[bat_pl.striker == batter].match_id.unique()[-5:].tolist()
    batter_match_id[batter] = matches

# Collect last 5 match IDs for each bowler in bowl_pl
for bowler in bowl_pl.bowler.unique():
    matches = bowl_pl[bowl_pl.bowler == bowler].match_id.unique()[-5:].tolist()
    bowler_match_id[bowler] = matches
    
######
df_bat = pd.DataFrame()

for batter_name in players_list:
    last_5_matches = batter_match_id.get(batter_name, [1])
    df_sub = bat_pl[(bat_pl.striker==batter_name)&(bat_pl.match_id.isin(last_5_matches))]
    if df_sub.shape[0]>0:
        df_sub.reset_index(drop=True, inplace=True)
        df_bat = df_bat.append(df_sub)
    else:
        continue
        
df_bowl = pd.DataFrame()

for bowler_name in players_list:
    last_5_matches = bowler_match_id.get(bowler_name, [1])
    df_sub = bowl_pl[(bowl_pl.bowler==bowler_name)&(bowl_pl.match_id.isin(last_5_matches))]
    if df_sub.shape[0]>0:
        df_sub.reset_index(drop=True, inplace=True)
        df_bowl = df_bowl.append(df_sub)
    else:
        continue
        
        
df_bowl['runs_conceeded'] = df_bowl['runs_off_bat']+df_bowl['wides']+df_bowl['noballs']

batter_stats_form = df_bat.groupby('striker').agg(

num_innings = ('match_id','nunique'),
    runs = ('runs_off_bat','sum'),
    balls = ('is_faced_by_batter' ,'sum'),
    outs = ('is_striker_Out','sum'),
    bat_order = ('striker_batting_position', lambda x: x.mode().iloc[0] if not x.mode().empty else None)
    
).reset_index()


bowler_stats_form = df_bowl.groupby('bowler').agg(

num_innings = ('match_id','nunique'),
    runs = ('runs_conceeded','sum'),
    balls = ('islegal' ,'sum'),
    wkts = ('isBowlerWicket','sum'),
    bowl_phase = ('phase', lambda x: x.mode().iloc[0] if not x.mode().empty else None)
    
).reset_index()

###########
batter_stats_form['bat_avg'] = batter_stats_form['runs']/batter_stats_form['outs']
batter_stats_form['bat_sr'] = 100*batter_stats_form['runs']/batter_stats_form['balls']

bowler_stats_form['bowl_sr'] = bowler_stats_form['balls']/bowler_stats_form['wkts']
bowler_stats_form['bowl_eco'] = 6*bowler_stats_form['runs']/bowler_stats_form['balls']


batter_stats_form['bat_avg'] = batter_stats_form.apply(
    lambda row: -1 if np.isinf(row['bat_avg']) else row['bat_avg'], axis=1
)
batter_stats_form['bat_avg'] = batter_stats_form['bat_avg'].fillna(0)

batter_stats_form['bat_sr'] = batter_stats_form.apply(
    lambda row: -1 if np.isinf(row['bat_sr']) else row['bat_sr'], axis=1
)
batter_stats_form['bat_sr'] = batter_stats_form['bat_sr'].fillna(0)

##bowler

bowler_stats_form['bowl_eco'] = bowler_stats_form.apply(
    lambda row: -1 if np.isinf(row['bowl_eco']) else row['bowl_eco'], axis=1
)

bowler_stats_form['bowl_eco'] = bowler_stats_form['bowl_eco'].fillna(0)


bowler_stats_form['bowl_sr'] = bowler_stats_form.apply(
    lambda row: 0 if np.isinf(row['bowl_sr']) else row['bowl_sr'], axis=1
)


# ## now read the big file

# In[8]:


df_ = pd.read_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/t20_pl_g.csv')
#df_all_ = df_all 

df_['runs_conceeded'] = df_['runs_off_bat'] + df_['wides'] + df_['noballs']
df_['isDotforbowler'] = ((df_['runs_off_bat'] == 0) & (df_['wides'] == 0) & (df_['noballs'] == 0)).astype(int)
df_['phase'] = np.where(df_['legal_balls_bowled'] <= 36, 'pp', 
                        np.where(df_['legal_balls_bowled'] >= 90, 'death', 'middle'))

df_ = df_.reindex(columns=df_all.columns)

df_all_ = pd.concat([df_,df_all],axis=0)
df_all_ = df_all_.drop_duplicates().reset_index(drop=True)


# In[9]:


'Gurjapneet Singh' in players_list


# ## batter, bowler stats

# #Note : to run both on Sim stats & Entire stats

# df_all_[df_all_.bowler=='Gurjapneet Singh']

# In[10]:


df_1 = df_all_[df_all_.innings==1]
df_2 = df_all_[df_all_.innings==2]

df_1_b = df_1[df_1.striker.isin(players_list)]
df_2_b = df_2[df_2.striker.isin(players_list)]

df_1_bo = df_1[df_1.bowler.isin(players_list)]
df_2_bo = df_2[df_2.bowler.isin(players_list)]



batter_stats = df_1_b.groupby(['striker','phase','innings']).agg(
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

##
batter_stats = batter_stats[batter_stats['balls']>0]
denominator = batter_stats['balls']
denominator = denominator.replace(0, np.nan)  # Replace zeros with NaN to avoid division by zero

batter_stats['strike_rate'] = np.where(
    denominator.notna(),  # Only perform division where denominator is not NaN
    100*batter_stats['runs'] / denominator,
    100  # Assign default value where denominator is zero or NaN
)
denominator = batter_stats['outs']
denominator = denominator.replace(0, np.nan)  # Replace zeros with NaN to avoid division by zero

batter_stats['balls_per_dismissal'] = np.where(
    denominator.notna(),  # Only perform division where denominator is not NaN
    batter_stats['balls'] / denominator,
    30  # Assign default value where denominator is zero or NaN
)

denominator = batter_stats['fours']+batter_stats['sixes']
denominator = denominator.replace(0, np.nan)  # Replace zeros with NaN to avoid division by zero

batter_stats['bpb'] = np.where(
    denominator.notna(),  # Only perform division where denominator is not NaN
    batter_stats['balls'] / denominator,
    10  # Assign default value where denominator is zero or NaN
)
batter_stats['dot_%'] = np.where(
    denominator.notna(),  # Only perform division where denominator is not NaN
    100*batter_stats['dots'] / denominator,
    0  # Assign default value where denominator is zero or NaN
)
#batter_stats['dot_%'] = 100*batter_stats['dots']/batter_stats['balls']

batter_stats['out_pb'] = 1/batter_stats['balls_per_dismissal']

batter_stats['one_pb'] = batter_stats['ones']/batter_stats['balls']
batter_stats['two_pb'] = batter_stats['twos']/batter_stats['balls']
batter_stats['three_pb'] = batter_stats['threes']/batter_stats['balls']
batter_stats['four_pb'] = batter_stats['fours']/batter_stats['balls']
batter_stats['six_pb'] = batter_stats['sixes']/batter_stats['balls']
batter_stats['dot_pb'] = batter_stats['dots']/batter_stats['balls']


pb_cols = [column for column in batter_stats.columns if '_pb' in str(column)]
pb_cols_div = [column for column in batter_stats.columns if '_pb' in str(column) and column!='out_pb']

batter_stats['pb_sum'] = batter_stats[pb_cols].apply(lambda x: x.sum(), axis=1)

batter_stats['out_prob'] = batter_stats['out_pb']/1

for col in pb_cols_div:
    rem_sum = (batter_stats['pb_sum']-batter_stats['out_pb'])
    multiplier = (1-batter_stats['out_prob'])/rem_sum
    batter_stats[str(col).replace('_pb','_prob')] = batter_stats[col]*multiplier
    
prob_cols = [column for column in batter_stats.columns if '_prob' in str(column)]

for col in batter_stats.columns[[0,1,2,3,4,5,6,13]]:
    prob_cols.append(col)

batter_stats_trimmed = batter_stats[prob_cols]

df_2_b['nrr_phase'] = np.where(df_2_b['reqd_run_rate']>=10, 'crucial', 
                        np.where(df_2_b['reqd_run_rate']<=8, 'easy',
                            'moderate'))

df_2_b['wkt_phase'] = np.where(df_2_b['wickets_down']>=7, 'tough', 
                        np.where(df_2_b['wickets_down']<=3, 'easy',
                            'medium'))

df_2_b['nrr_phase'].value_counts(), df_2_b['wkt_phase'].value_counts()

batter_stats = df_2_b.groupby(['striker','innings','phase','nrr_phase','wkt_phase']).agg(
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

batter_stats = batter_stats[batter_stats['balls']>0]
denominator = batter_stats['balls']
denominator = denominator.replace(0, np.nan)  # Replace zeros with NaN to avoid division by zero

batter_stats['strike_rate'] = np.where(
    denominator.notna(),  # Only perform division where denominator is not NaN
    100*batter_stats['runs'] / denominator,
    100  # Assign default value where denominator is zero or NaN
)
#batter_stats['strike_rate'] = np.where(batter_stats['balls']>0,100*batter_stats['runs']/batter_stats['balls'],100)
denominator = batter_stats['outs']
denominator = denominator.replace(0, np.nan)  # Replace zeros with NaN to avoid division by zero

batter_stats['balls_per_dismissal'] = np.where(
    denominator.notna(),  # Only perform division where denominator is not NaN
    batter_stats['balls'] / denominator,
    30  # Assign default value where denominator is zero or NaN
)

denominator = batter_stats['fours']+batter_stats['sixes']
denominator = denominator.replace(0, np.nan)  # Replace zeros with NaN to avoid division by zero

batter_stats['bpb'] = np.where(
    denominator.notna(),  # Only perform division where denominator is not NaN
    batter_stats['balls'] / denominator,
    10  # Assign default value where denominator is zero or NaN
)
denominator = batter_stats['balls']
denominator = denominator.replace(0, np.nan)  # Replace zeros with NaN to avoid division by zero

batter_stats['dot_%'] = np.where(
    denominator.notna(),  # Only perform division where denominator is not NaN
    100*batter_stats['dots'] / denominator,
    0  # Assign default value where denominator is zero or NaN
)
#batter_stats['dot_%'] = 100*batter_stats['dots']/batter_stats['balls']

batter_stats['out_pb'] = 1/batter_stats['balls_per_dismissal']

batter_stats['one_pb'] = batter_stats['ones']/batter_stats['balls']
batter_stats['two_pb'] = batter_stats['twos']/batter_stats['balls']
batter_stats['three_pb'] = batter_stats['threes']/batter_stats['balls']
batter_stats['four_pb'] = batter_stats['fours']/batter_stats['balls']
batter_stats['six_pb'] = batter_stats['sixes']/batter_stats['balls']
batter_stats['dot_pb'] = batter_stats['dots']/batter_stats['balls']


pb_cols = [column for column in batter_stats.columns if '_pb' in str(column)]
pb_cols_div = [column for column in batter_stats.columns if '_pb' in str(column) and column!='out_pb']

batter_stats['pb_sum'] = batter_stats[pb_cols].apply(lambda x: x.sum(), axis=1)

batter_stats['out_prob'] = batter_stats['out_pb']/1

for col in pb_cols_div:
    rem_sum = (batter_stats['pb_sum']-batter_stats['out_pb'])
    multiplier = (1-batter_stats['out_prob'])/rem_sum
    batter_stats[str(col).replace('_pb','_prob')] = batter_stats[col]*multiplier
    
prob_cols = [column for column in batter_stats.columns if '_prob' in str(column)]

for col in batter_stats.columns[[0,1,2,3,4,5,6,7,8,15]]:
    prob_cols.append(col)

batter_stats_trimmed_2 = batter_stats[prob_cols]


##################################################################################################


df_1_bo['runs_conceeded'] = df_1_bo['runs_off_bat']+df_1_bo['wides']+df_1_bo['noballs']
df_1_bo['isDotforbowler'] = np.where((df_1_bo['runs_conceeded']==0)&(df_1_bo['islegal']==1), 1, 0)
bowler_stats = df_1_bo.groupby(['bowler','phase','innings']).agg(
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

bowler_stats = bowler_stats[bowler_stats['balls']>0]
bowler_stats['economy'] = 6*bowler_stats['runs']/bowler_stats['balls']
bowler_stats['strike_rate'] = np.where(bowler_stats['wkts']>0,
                                       bowler_stats['balls']/bowler_stats['wkts'],bowler_stats['balls'])
bowler_stats['bpb'] = np.where(((bowler_stats['fours']+bowler_stats['sixes'])>0),
                               bowler_stats['balls']/(bowler_stats['fours']+bowler_stats['sixes']),
                               bowler_stats['balls'])
bowler_stats['dot_%'] = 100*bowler_stats['dots']/bowler_stats['balls']

bowler_stats['wkt_pb'] = 1/bowler_stats['strike_rate']



bowler_stats['one_pb'] = bowler_stats['ones']/bowler_stats['balls']
bowler_stats['two_pb'] = bowler_stats['twos']/bowler_stats['balls']
bowler_stats['three_pb'] = bowler_stats['threes']/bowler_stats['balls']
bowler_stats['four_pb'] = bowler_stats['fours']/bowler_stats['balls']
bowler_stats['six_pb'] = bowler_stats['sixes']/bowler_stats['balls']
bowler_stats['dot_pb'] = bowler_stats['dots']/bowler_stats['balls']

bowler_stats['wide_pb'] = bowler_stats['wides']/bowler_stats['balls']
bowler_stats['no_pb'] = bowler_stats['noballs']/bowler_stats['balls']


pb_cols = [column for column in bowler_stats.columns if '_pb' in str(column)]
pb_cols_div = [column for column in bowler_stats.columns if '_pb' in str(column) and column!='wkt_pb']
bowler_stats['pb_sum'] = bowler_stats[pb_cols].apply(lambda x: x.sum(), axis=1)

bowler_stats['wkt_prob'] = bowler_stats['wkt_pb']/1

for col in pb_cols_div:
    rem_sum = (bowler_stats['pb_sum']-bowler_stats['wkt_pb'])
    multiplier = (1-bowler_stats['wkt_prob'])/rem_sum
    bowler_stats[str(col).replace('_pb','_prob')] = bowler_stats[col]*multiplier
    prob_cols = [column for column in bowler_stats.columns if '_prob' in str(column)]

for col in bowler_stats.columns[[0,1,2,3,4,5,6,15,16]]:
    prob_cols.append(col)

bowler_stats_trimmed = bowler_stats[prob_cols]


df_2_bo['runs_conceeded'] = df_2_bo['runs_off_bat']+df_2_bo['wides']+df_2_bo['noballs']
df_2_bo['isDotforbowler'] = np.where((df_2_bo['runs_conceeded']==0)&(df_2_bo['islegal']==1), 1, 0)
df_2_bo['nrr_phase'] = np.where(df_2_bo['reqd_run_rate']>=10, 'easy', 
                        np.where(df_2_bo['reqd_run_rate']<=8, 'crucial',
                            'moderate'))

df_2_bo['wkt_phase'] = np.where(df_2_bo['wickets_down']>=7, 'easy', 
                        np.where(df_2_bo['wickets_down']<=3, 'crucial',
                            'medium'))

df_2_bo['nrr_phase'].value_counts(), df_2_bo['wkt_phase'].value_counts()
bowler_stats = df_2_bo.groupby(['bowler','innings','phase','nrr_phase','wkt_phase']).agg(
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

bowler_stats = bowler_stats[bowler_stats['balls']>0]
bowler_stats['economy'] = 6*bowler_stats['runs']/bowler_stats['balls']
bowler_stats['strike_rate'] = np.where(bowler_stats['wkts']>0,
                                       bowler_stats['balls']/bowler_stats['wkts'],bowler_stats['balls'])
bowler_stats['bpb'] = np.where(((bowler_stats['fours']+bowler_stats['sixes'])>0),
                               bowler_stats['balls']/(bowler_stats['fours']+bowler_stats['sixes']),
                               bowler_stats['balls'])
bowler_stats['dot_%'] = 100*bowler_stats['dots']/bowler_stats['balls']

bowler_stats['wkt_pb'] = 1/bowler_stats['strike_rate']

bowler_stats['one_pb'] = bowler_stats['ones']/bowler_stats['balls']
bowler_stats['two_pb'] = bowler_stats['twos']/bowler_stats['balls']
bowler_stats['three_pb'] = bowler_stats['threes']/bowler_stats['balls']
bowler_stats['four_pb'] = bowler_stats['fours']/bowler_stats['balls']
bowler_stats['six_pb'] = bowler_stats['sixes']/bowler_stats['balls']
bowler_stats['dot_pb'] = bowler_stats['dots']/bowler_stats['balls']

bowler_stats['wide_pb'] = bowler_stats['wides']/bowler_stats['balls']
bowler_stats['no_pb'] = bowler_stats['noballs']/bowler_stats['balls']


pb_cols = [column for column in bowler_stats.columns if '_pb' in str(column)]
pb_cols_div = [column for column in bowler_stats.columns if '_pb' in str(column) and column!='wkt_pb']
bowler_stats['pb_sum'] = bowler_stats[pb_cols].apply(lambda x: x.sum(), axis=1)

bowler_stats['wkt_prob'] = bowler_stats['wkt_pb']/1

for col in pb_cols_div:
    rem_sum = (bowler_stats['pb_sum']-bowler_stats['wkt_pb'])
    multiplier = (1-bowler_stats['wkt_prob'])/rem_sum
    bowler_stats[str(col).replace('_pb','_prob')] = bowler_stats[col]*multiplier

prob_cols = [column for column in bowler_stats.columns if '_prob' in str(column)]#Note : to run both on Sim stats & Entire stats
for col in bowler_stats.columns[[0,1,2,3,4,5,6,7,8,17,18]]:
    prob_cols.append(col)

bowler_stats_trimmed2 = bowler_stats[prob_cols]


# ## spin-pace factor

# #Note : to run both on Sim stats & Entire stats

# In[11]:


df_pl = df_all_.sort_values(by=['start_date','match_id','innings','ball']).reset_index(drop=True)

batter_list = pd.read_excel('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/player_list.xlsx',
                           sheet_name='season_02')
batters = batter_list['Func_Name'].unique().tolist()

df_pl = df_pl[df_pl['striker'].isin(batters)].reset_index(drop=True)

player_list = df_pl.bowler.unique()

players = player_list.tolist()


play_style_df = pd.read_csv("/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/play_style.csv")


# In[12]:


df_pl_mod = df_pl.merge(play_style_df, on='bowler',
                       how='left')


spin_bat = df_pl_mod[df_pl_mod['bowl_style_parent']=='Spin'].groupby('striker').agg(
    runs = ('runs_off_bat','sum'),
    balls = ('is_faced_by_batter','sum'),
    outs = ('isBowlerWicket','sum'),
    fours = ('isFour','sum'),
    sixes = ('isSix','sum'),
    dots = ('isDotforBatter','sum')
).reset_index()

spin_bat['SR'] = np.where(spin_bat['balls']>0,100*spin_bat['runs']/spin_bat['balls'],100)
spin_bat['Bat_avg'] = np.where(spin_bat['outs']>0,spin_bat['runs']/spin_bat['outs'],spin_bat['runs'])
denominator = spin_bat['fours'] + spin_bat['sixes']
denominator = denominator.replace(0, np.nan)  # Replace zeros with NaN to avoid division by zero

spin_bat['bpb'] = np.where(
    denominator.notna(),  # Only perform division where denominator is not NaN
    spin_bat['balls'] / denominator,
    10  # Assign default value where denominator is zero or NaN
)
spin_bat['dot_%'] = np.where(spin_bat['balls']>0,100*spin_bat['dots']/spin_bat['balls'],0)

pace_bat = df_pl_mod[df_pl_mod['bowl_style_parent']=='Pace'].groupby('striker').agg(
    runs = ('runs_off_bat','sum'),
    balls = ('is_faced_by_batter','sum'),
    outs = ('isBowlerWicket','sum'),
    fours = ('isFour','sum'),
    sixes = ('isSix','sum'),
    dots = ('isDotforBatter','sum')
).reset_index()

pace_bat['SR'] = np.where(pace_bat['balls']>0,100*pace_bat['runs']/pace_bat['balls'],100)
pace_bat['Bat_avg'] = np.where(pace_bat['outs']>0,pace_bat['runs']/pace_bat['outs'],pace_bat['runs'])
denominator = pace_bat['fours'] + pace_bat['sixes']
denominator = denominator.replace(0, np.nan)  # Replace zeros with NaN to avoid division by zero

pace_bat['bpb'] = np.where(
    denominator.notna(),  # Only perform division where denominator is not NaN
    pace_bat['balls'] / denominator,
    10  # Assign default value where denominator is zero or NaN
)
pace_bat['dot_%'] = np.where(pace_bat['balls']>0,100*pace_bat['dots']/pace_bat['balls'],0)

pace_bat['pace_index_int'] = pace_bat['SR']+np.where(pace_bat['Bat_avg']<1000, pace_bat['Bat_avg'],                                 pace_bat['runs'])- 10*np.where(pace_bat['bpb']<1000, pace_bat['bpb'],                                         pace_bat['balls'])-pace_bat['dot_%']

pace_bat['pace_idx'] = np.where(
    ((pace_bat['balls'] < 300) & (pace_bat['balls'] >= 50)), 
    pace_bat['pace_index_int'] * ((pace_bat['balls'] / 300) ** 0.5),\
    np.where(pace_bat['balls'] >= 300, 
    pace_bat['pace_index_int'], \
            np.nan)
)


##
spin_bat['spin_index_int'] = spin_bat['SR']+np.where(spin_bat['Bat_avg']<1000, spin_bat['Bat_avg'],                                 spin_bat['runs'])- 10*np.where(spin_bat['bpb']<1000, spin_bat['bpb'],                                         spin_bat['balls'])-spin_bat['dot_%']

spin_bat['spin_idx'] = np.where(
    ((spin_bat['balls'] < 300) & (spin_bat['balls'] >= 50)), 
    spin_bat['spin_index_int'] * ((spin_bat['balls'] / 300) ** 0.5),\
    np.where(spin_bat['balls'] >= 300, 
    spin_bat['spin_index_int'], \
            np.nan)
)

##

k1 = 0.02
k2 = 0.1
c1 = 70
c2 = 97

def sigmoid(x):
    if x<=70:
        value = 0.5 + 1 / (1 + np.exp(-k1 * (x-c1)))
    else:
        value = 1 + 1/ (1 + np.exp(-k2 * (x-c2 )))
        
    return value

pace_bat['pace_index'] = pace_bat['pace_idx'].apply(sigmoid)
spin_bat['spin_index'] = spin_bat['spin_idx'].apply(sigmoid)

##
pace_bat.drop(['pace_index_int','pace_idx'], axis=1, inplace=True)
spin_bat.drop(['spin_index_int','spin_idx'], axis=1, inplace=True)


pace_bat_trimmed = pace_bat[~pace_bat.pace_index.isna()].reset_index(drop=True)
spin_bat_trimmed = spin_bat[~spin_bat.spin_index.isna()].reset_index(drop=True)


# In[ ]:





# ## phase wise batting SR, bowling Eco

# #Note : to run only on Sim stats

# In[13]:


bat_phase = df_all.groupby(['striker','phase']).agg(
    num_innings = ('match_id','nunique'),
    runs = ('total_runs','sum'),
    balls = ('is_faced_by_batter' ,'sum')
    
).reset_index()

bat_phase['strike_rate'] = 100*bat_phase['runs']/bat_phase['balls']
bat_phase = bat_phase.round(2)


# In[14]:


bowl_phase = df_all.groupby(['bowler','phase']).agg(
    num_innings = ('match_id','nunique'),
    runs = ('runs_conceeded','sum'),
    balls = ('islegal' ,'sum')
    
).reset_index()

bowl_phase['economy'] = 6*bowl_phase['runs']/bowl_phase['balls']
bowl_phase = bowl_phase.round(2)


# ## h2h stats

# #Note : to run both on Sim stats & Entire stats

# In[15]:


h2h_stats = df_all_.groupby(['striker','bowler']).agg(
    
    runs_scored = ('runs_off_bat','sum'),
    runs_conceeded = ('runs_conceeded','sum'),
     
    balls_faced = ('is_faced_by_batter' ,'sum'),
    balls_bowled = ('islegal','sum'),
    
    outs = ('isBowlerWicket','sum')
    
).reset_index()

h2h_stats = h2h_stats[h2h_stats['balls_faced']>0]
h2h_stats['bat_sr'] = 100*h2h_stats['runs_scored']/h2h_stats['balls_faced']

h2h_stats['bat_avg'] = h2h_stats['runs_scored']/h2h_stats['outs']
h2h_stats['bowl_sr'] = h2h_stats['balls_bowled']/h2h_stats['outs']
h2h_stats['bat_sr'] = 100*h2h_stats['runs_scored']/h2h_stats['balls_faced']
h2h_stats['bowl_eco'] = 6*h2h_stats['runs_conceeded']/h2h_stats['balls_bowled']

h2h_stats['bat_avg'] = h2h_stats.apply(
    lambda row: row['balls_faced']*2 if np.isinf(row['bat_avg']) else row['bat_avg'], axis=1
)

h2h_stats['bowl_sr'] = h2h_stats.apply(
    lambda row: row['balls_bowled']*2 if np.isinf(row['bowl_sr']) else row['bowl_sr'], axis=1
)

h2h_stats['bowl_eco'] = h2h_stats.apply(
    lambda row: 36 if np.isinf(row['bowl_eco']) else row['bowl_eco'], axis=1
)

bat_fig = 2*135+0.5*35
bowl_fig = 27

h2h_stats['bat'] = (2*h2h_stats['bat_sr']+0.5*h2h_stats['bat_avg'])/bat_fig
h2h_stats['bowl'] = bowl_fig/(h2h_stats['bowl_sr']+h2h_stats['bowl_eco'])

h2h_stats['bat'] = np.where(h2h_stats['balls_faced']<20, 0, h2h_stats['bat'])
h2h_stats['bowl'] = np.where(h2h_stats['balls_bowled']<20, 0, h2h_stats['bowl'])

h2h_stats['bat'] = np.where(h2h_stats['bowl']==0, 2, h2h_stats['bat'])
h2h_stats['bowl'] = np.where(h2h_stats['bat']==0, 2, h2h_stats['bowl'])

h2h_stats['a'] = 2/(h2h_stats['bat']+h2h_stats['bowl'])

h2h_stats['bat_a'] = h2h_stats['bat']*h2h_stats['a']
h2h_stats['bowl_a'] = h2h_stats['bowl']*h2h_stats['a']

h2h_stats['h2h_factor_bat'] = np.where(h2h_stats['balls_faced']<20, 0, h2h_stats['bat_a'])
h2h_stats['h2h_factor_bowl'] = np.where(h2h_stats['balls_bowled']<20, 0, h2h_stats['bowl_a'])

h2h_stats_trimmed = h2h_stats[(h2h_stats.balls_bowled>=20)&(h2h_stats.balls_faced>=20)]                        [['striker','bowler','runs_scored','balls_bowled',
                          'outs','h2h_factor_bat','h2h_factor_bowl']]

#h2h_stats


# ## ground stats

# #Note : to run only on Sim stats

# In[16]:


df_g = df_all

ground_stats = df_g.groupby(['venue','phase','innings']).agg(
    num_innings = ('match_id','nunique'),
    runs = ('total_runs','sum'),
    balls = ('islegal' ,'sum'),
    wickets = ('isWicket','sum'),
    fours = ('isFour', 'sum'),
    sixes = ('isSix','sum'),
    dots = ('isDotforBatter','sum'),
    extras = ('extras','sum'),
    ones = ('isOne','sum'),
    twos = ('isTwo','sum'),
    threes = ('isThree','sum'),
    wides = ('wides','sum'),
    noballs = ('noballs','sum'),
    byes = ('byes','sum'),
    legbyes = ('legbyes','sum')
    
    
).reset_index()

ground_stats['run_rate'] = 6*ground_stats['runs']/ground_stats['balls']
ground_stats['strike_rate'] = 100*ground_stats['runs']/ground_stats['balls']
ground_stats['bowl_strike_rate'] = ground_stats['balls']/ground_stats['wickets']
ground_stats['bpb'] = ground_stats['balls']/(ground_stats['fours']+ground_stats['sixes'])
ground_stats['dot_%'] = 100*ground_stats['dots']/ground_stats['balls']
ground_stats['extra_per_over'] = 6*ground_stats['extras']/ground_stats['balls']

ground_stats['wkt_pb'] = 1/ground_stats['bowl_strike_rate']

ground_stats['one_pb'] = ground_stats['ones']/ground_stats['balls']
ground_stats['two_pb'] = ground_stats['twos']/ground_stats['balls']
ground_stats['three_pb'] = ground_stats['threes']/ground_stats['balls']
ground_stats['four_pb'] = ground_stats['fours']/ground_stats['balls']
ground_stats['six_pb'] = ground_stats['sixes']/ground_stats['balls']
ground_stats['dot_pb'] = ground_stats['dots']/ground_stats['balls']

ground_stats['wide_pb'] = ground_stats['wides']/ground_stats['balls']
ground_stats['no_pb'] = ground_stats['noballs']/ground_stats['balls']
ground_stats['bye_pb'] = ground_stats['byes']/ground_stats['balls']
ground_stats['legbye_pb'] = ground_stats['legbyes']/ground_stats['balls']

pb_cols = [column for column in ground_stats.columns if '_pb' in str(column)]
pb_cols_div = [column for column in ground_stats.columns if '_pb' in str(column) and column!='wkt_pb']
#print(len(pb_cols))

ground_stats['pb_sum'] = ground_stats[pb_cols].apply(lambda x: x.sum(), axis=1)

ground_stats['wkt_prob'] = ground_stats['wkt_pb']/1

for col in pb_cols_div:
    rem_sum = (ground_stats['pb_sum']-ground_stats['wkt_pb'])
    multiplier = (1-ground_stats['wkt_prob'])/rem_sum
    ground_stats[str(col).replace('_pb','_prob')] = ground_stats[col]*multiplier

prob_cols = [column for column in ground_stats.columns if '_prob' in str(column)]

for col in ground_stats.columns[[0,1,2,18,19,20,21,22]]:
    prob_cols.append(col)

ground_stats_trimmed = ground_stats[prob_cols]


# In[ ]:





# ## SIM CAREER batter, bowler stats

# #Note : to run only on Sim stats

# In[17]:


df_ = df_all


batter_stats = df_.groupby('striker').agg(  ##,'innings'
    num_innings = ('match_id','nunique'),
    runs = ('runs_off_bat','sum'),
    balls = ('is_faced_by_batter' ,'sum'),
    outs = ('is_striker_Out','sum')
    
).reset_index()

##addition of runouts
runout_count = df_[df_.wicket_type=='runout'].groupby('player_dismissed')['isWicket'].count().reset_index()

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
own_runout_count = df_[df_.wicket_type=='runout'].groupby('player_dismissed')['is_striker_Out'].sum().reset_index()

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
    
batter_stats['SR'] = 100*batter_stats['runs']/batter_stats['balls']
batter_stats['balls_per_dismissal'] = np.where(batter_stats['outs']>0,
                                               batter_stats['balls']/batter_stats['outs'], 'inf')
batter_stats['Bat_avg'] = np.where(batter_stats['outs']>0,
                                   batter_stats['runs']/batter_stats['outs'], 'inf')

##################################################################################################


## bowler stats

bowler_stats = df_.groupby('bowler').agg(   ##,'innings'
    num_innings = ('match_id','nunique'),
    runs = ('runs_conceeded','sum'),
    balls = ('islegal' ,'sum'),
    wkts = ('isBowlerWicket','sum')
).reset_index()

bowler_stats['economy'] = 6*bowler_stats['runs']/bowler_stats['balls']
bowler_stats['strike_rate'] = np.where(bowler_stats['wkts']>0,
                                       bowler_stats['balls']/bowler_stats['wkts'], 'inf')


# In[18]:


for col in bowler_stats:
    bowler_stats[col] = bowler_stats[col].apply(try_float_2)
    
for col in batter_stats:
    batter_stats[col] = batter_stats[col].apply(try_float_2)
    
for col in pace_bat:
    pace_bat[col] = pace_bat[col].apply(try_float_2)
    
for col in spin_bat:
    spin_bat[col] = spin_bat[col].apply(try_float_2)


# 

# # SAVING

# In[19]:


bowler_stats_2_form_trimmed.sort_values('form', ascending=False
                                       )


# In[20]:


batter_stats_1_form_trimmed.to_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/batter_stats_form_inn1.csv',
                           index=None)
batter_stats_2_form_trimmed.to_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/batter_stats_form_inn2.csv',
                           index=None)

bowler_stats_1_form_trimmed.to_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/bowler_stats_form_inn1.csv',
                           index=None)
bowler_stats_2_form_trimmed.to_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/bowler_stats_form_inn2.csv',
                           index=None)

batter_stats_trimmed.to_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/batter_stats_inn1.csv',
                           index=None)
batter_stats_trimmed_2.to_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/batter_stats_inn2.csv',
                           index=None)
bowler_stats_trimmed.to_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/bowler_stats_inn1.csv',
                           index=None)
bowler_stats_trimmed2.to_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/bowler_stats_inn2.csv',
                           index=None)

h2h_stats_trimmed.to_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/h2h_stats.csv',
                           index=None)

pace_bat_trimmed.to_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/pace_bat.csv',
                           index=None)
spin_bat_trimmed.to_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/spin_bat.csv',
                           index=None)


ground_stats_trimmed.to_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/ground_stats.csv',
                           index=None)


# batter_stats_1_form_trimmed.to_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/batter_stats_form_inn1.csv',
#                            index=None)
# batter_stats_2_form_trimmed.to_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/batter_stats_form_inn2.csv',
#                            index=None)
# 
# bowler_stats_1_form_trimmed.to_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/bowler_stats_form_inn1.csv',
#                            index=None)
# bowler_stats_2_form_trimmed.to_csv('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/bowler_stats_form_inn2.csv',
#                            index=None)

# ground_stats_trimmed.columns

# In[21]:


player_list = pd.read_excel('/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/player_list.xlsx',
                           sheet_name='season_02')

player_list = player_list[['Func_Name','Team_S02']].dropna()

player_list_bat = player_list.copy()
player_list_bat.columns=['striker','team']

player_list_bowl = player_list.copy()
player_list_bowl.columns=['bowler','team']

excel_filename = '/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/data to send/stats_players.xlsx'

# Use ExcelWriter to write multiple sheets
with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
    spin_bat_trimmed.drop('spin_index',axis=1).merge(player_list_bat,on='striker',how='left').sort_values('runs',ascending=False).to_excel(writer, sheet_name='spin_bat', index=False)
    pace_bat_trimmed.drop('pace_index',axis=1).merge(player_list_bat,on='striker',how='left').sort_values('runs',ascending=False).to_excel(writer, sheet_name='pace_bat', index=False)
    batter_stats_trimmed.drop(['out_prob', 'one_prob', 'two_prob', 'three_prob', 'four_prob',       'six_prob', 'dot_prob'],axis=1).merge(player_list_bat,on='striker',how='left').sort_values('runs',ascending=False).to_excel(writer, sheet_name='inning_1_bat', index=False)
    batter_stats_trimmed_2.drop(['out_prob', 'one_prob', 'two_prob', 'three_prob', 'four_prob',       'six_prob', 'dot_prob'],axis=1).merge(player_list_bat,on='striker',how='left').sort_values('runs',ascending=False).to_excel(writer, sheet_name='inning_2_bat', index=False)
    ####
    bowler_stats_trimmed.drop(['wkt_prob', 'one_prob', 'two_prob', 'three_prob', 'four_prob',       'six_prob', 'dot_prob', 'wide_prob', 'no_prob'],axis=1).merge(player_list_bowl,on='bowler',how='left').sort_values('wkts',ascending=False).to_excel(writer, sheet_name='inning_1_bowl', index=False)
    bowler_stats_trimmed2.drop(['wkt_prob', 'one_prob', 'two_prob', 'three_prob', 'four_prob',       'six_prob', 'dot_prob', 'wide_prob', 'no_prob'],axis=1).merge(player_list_bowl,on='bowler',how='left').sort_values('wkts',ascending=False).to_excel(writer, sheet_name='inning_2_bowl', index=False)
########

########
excel_filename = '/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/data to send/form_stats.xlsx'

# Use ExcelWriter to write multiple sheets
with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
    batter_stats_1_form_trimmed.drop('form',axis=1).merge(player_list_bat,on='striker',how='left').sort_values('runs',ascending=False).to_excel(writer, sheet_name='Bat_inning_1', index=False)
    batter_stats_2_form_trimmed.drop('form',axis=1).merge(player_list_bat,on='striker',how='left').sort_values('runs',ascending=False).to_excel(writer, sheet_name='Bat_inning_2', index=False)
    bowler_stats_1_form_trimmed.drop('form',axis=1).merge(player_list_bowl,on='bowler',how='left').sort_values('wkts',ascending=False).to_excel(writer, sheet_name='Bowl_inning_1', index=False)
    bowler_stats_2_form_trimmed.drop('form',axis=1).merge(player_list_bowl,on='bowler',how='left').sort_values('wkts',ascending=False).to_excel(writer, sheet_name='Bowl_inning_2', index=False)

player_list_bat = player_list.copy()
player_list_bat.columns=['striker','bat_team']

player_list_bowl = player_list.copy()
player_list_bowl.columns=['bowler','bowl_team']  

h2h_stats_mod = h2h_stats_trimmed[(h2h_stats_trimmed['striker'].isin(player_list['Func_Name'].unique()))&                          (h2h_stats_trimmed['bowler'].isin(player_list['Func_Name'].unique()))]

h2h_stats_mod = h2h_stats_mod.merge(player_list_bat,on='striker',how='left')                        .merge(player_list_bowl,on='bowler',how='left')


excel_filename = '/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/data to send/h2h_stats.xlsx'

# Use ExcelWriter to write multiple sheets
with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
    h2h_stats_mod.to_excel(writer, sheet_name='h2h', index=False)
    
    
    
    
    


# In[22]:


excel_filename = '/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/data to send/stats_players.xlsx'


# Dictionary mapping sheet names to DataFrames
sheets_data = {
    'spin_bat': spin_bat_trimmed.drop('spin_index',axis=1).merge(player_list_bat,on='striker',how='left').round(2).sort_values('runs',ascending=False),
    'pace_bat': pace_bat_trimmed.drop('pace_index',axis=1).merge(player_list_bat,on='striker',how='left').round(2).sort_values('runs',ascending=False),
    
    'inning_1_bat': batter_stats_trimmed.drop(['out_prob', 'one_prob', 'two_prob', 'three_prob', 'four_prob',\
       'six_prob', 'dot_prob'],axis=1).merge(player_list_bat,on='striker',how='left').round(2).sort_values('runs',ascending=False),
    
    'inning_2_bat': batter_stats_trimmed_2.drop(['out_prob', 'one_prob', 'two_prob', 'three_prob', 'four_prob',\
       'six_prob', 'dot_prob'],axis=1).merge(player_list_bat,on='striker',how='left').round(2).sort_values('runs',ascending=False),
    
    'inning_1_bowl': bowler_stats_trimmed.drop(['wkt_prob', 'one_prob', 'two_prob', 'three_prob', 'four_prob',\
       'six_prob', 'dot_prob', 'wide_prob', 'no_prob'],axis=1).merge(player_list_bowl,on='bowler',how='left').round(2).sort_values('wkts',ascending=False),
    
    'inning_2_bowl': bowler_stats_trimmed2.drop(['wkt_prob', 'one_prob', 'two_prob', 'three_prob', 'four_prob',\
       'six_prob', 'dot_prob', 'wide_prob', 'no_prob'],axis=1).merge(player_list_bowl,on='bowler',how='left').round(2).sort_values('wkts',ascending=False),

    'h2h': h2h_stats_mod.drop(['h2h_factor_bat','h2h_factor_bowl'],axis=1).round(2),
    
    'ground': ground_stats_trimmed.drop(['wkt_prob', 'one_prob', 'two_prob', 'three_prob', 'four_prob',\
       'six_prob', 'dot_prob', 'wide_prob', 'no_prob', 'bye_prob',\
       'legbye_prob'],axis=1).round(2)
    
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
        
        # 3️⃣ Bold entire column 1 (index 0) of every sheet
        worksheet.set_column(0, 0, None, bold_format)
            
        # Adjust column widths dynamically
        for col_idx, col_name in enumerate(df.columns):
            max_length = max(df[col_name].astype(str).apply(len).max(), len(col_name))  # Max of column values & header
            worksheet.set_column(col_idx, col_idx, max_length + 2)  # Adding padding for readability
            
        # 7️⃣ Freeze the first row of every sheet
        worksheet.freeze_panes(1, 0)
        
        # 8️⃣ **Add Filter to all columns**
        worksheet.autofilter(0, 0, 0, len(df.columns) - 1)  # Apply filter to the first row across all columns


print(f"Excel file '{excel_filename}' created successfully with formatting!")


# In[23]:


excel_filename = '/Users/roumyadas/Desktop/IPL_Simulation/Season_02/updates_/separate_stats.xlsx'

# Use ExcelWriter to write multiple sheets
with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
    batter_stats.to_excel(writer, sheet_name='Bat', index=False)
    bowler_stats.to_excel(writer, sheet_name='Bowl', index=False)
    bat_phase.to_excel(writer, sheet_name='BAT_phase', index=False)
    bowl_phase.to_excel(writer, sheet_name='BOWL_phase', index=False)
    h2h_stats.to_excel(writer, sheet_name='h2h', index=False)
    #ground_stats_trimmed.to_excel(writer, sheet_name='ground', index=False)
    pace_bat.to_excel(writer, sheet_name='pace', index=False)
    spin_bat.to_excel(writer, sheet_name='spin', index=False)
    batter_stats_form.to_excel(writer, sheet_name='form_bat', index=False)
    bowler_stats_form.to_excel(writer, sheet_name='form_bowl', index=False)


# In[ ]:





# In[ ]:





# In[24]:


print("ALL DONE")


# In[ ]:





# In[ ]:




