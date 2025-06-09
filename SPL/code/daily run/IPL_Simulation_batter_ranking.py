#!/usr/bin/env python
# coding: utf-8

# In[137]:


import pandas as pd
import glob
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import random
import warnings
warnings.filterwarnings('ignore')


# In[138]:


df_sim_1 = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_01/Stats/df_all_round_sim.csv')
df_sim_2 = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/df_all_round_sim.csv')

#df_sim_1 = pd.read_csv('D:/Downloads/df_all_round_sim_01.csv')
#df_sim_2 = pd.read_csv('D:/Downloads/df_all_round_sim_02.csv')

df_all = pd.concat([df_sim_1,df_sim_2[df_sim_1.columns]],axis=0).reset_index(drop=True)
#df_all = df_sim_1


# In[139]:


df_exp = df_all.copy()

df_exp['over'] = df_exp['legal_balls_bowled'].apply(lambda x: x//6 if x%6==0 else 1+x//6)
df_exp.loc[df_exp['islegal']==0,'over'] = np.nan

df_exp['over'].fillna(method='bfill', inplace=True)
df_exp['over'] = df_exp['over'].astype(int)

df_exp['phase'] = df_exp['over'].apply(lambda x: 'pp' if x<=6 else 'death' if x>=16 else 'middle')


# In[140]:


def weighted_mean(df, value_col, weight_col, group_col):
    """
    Calculate weighted mean for a groupby.

    Args:
        df (pd.DataFrame): Input dataframe
        value_col (str): Column with values to average
        weight_col (str): Column with weights
        group_col (str or list): Column(s) to group by

    Returns:
        pd.DataFrame: group_col + weighted mean
    """
    weighted_sum = (df[value_col] * df[weight_col]).groupby(df[group_col]).sum()
    total_weight = df[weight_col].groupby(df[group_col]).sum()
    wtd_mean = weighted_sum / total_weight
    return wtd_mean.reset_index(name=f'{value_col}')


# In[141]:


@pd.api.extensions.register_dataframe_accessor("wtd")
class WeightedMeanAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def mean(self):
        val_col, weight_col = self._obj.columns
        weighted_sum = (self._obj[val_col] * self._obj[weight_col]).sum()
        total_weight = self._obj[weight_col].sum()
        return weighted_sum / total_weight


# ## batting

# #ideas ::

# In[142]:


def batter_ranking(df_exp):

#     <!-- **team played for**

#     team played for in the latest season -->

    df_exp_new = df_exp[df_exp['season']==int(df_exp['season'].unique()[-1])]
    team = df_exp_new.groupby('striker')['batting_team'].unique().reset_index()
    team['team'] = team['batting_team'].apply(lambda x: x[0])

    team.drop('batting_team',axis=1, inplace=True)

    perf = df_exp.groupby('striker')[['runs_off_bat','is_faced_by_batter']].sum().reset_index()
    team_df = team.merge(perf, on='striker',how='left')
    inn = df_exp.groupby('striker')['match_id'].nunique().reset_index()
    team_df = team_df.merge(inn, on='striker',how='left')
    team_df.columns = ['striker','team','runs','balls','num_innings']
    
    



#     <!-- **1. PPI (PowerPlay Index) :**
#      how a batter's SR compares to others' (median) SR in PP -->

    df_pp = df_exp[df_exp['phase']=='pp']

    pp_sr = df_pp.groupby('striker').agg(  
        num_innings = ('match_id','nunique'),
        runs = ('runs_off_bat','sum'),
        balls = ('is_faced_by_batter' ,'sum')
    ).reset_index()

    pp_sr['strike_rate'] = 100*pp_sr['runs']/pp_sr['balls']

    #pp_sr = pp_sr[(pp_sr.balls>=25)&(pp_sr.num_innings>=2)]

    #pp_sr['PPI'] = pp_sr['strike_rate']/pp_sr['strike_rate'].mean() - 1
    pp_sr['PPI'] = pp_sr['strike_rate']/pp_sr[['strike_rate','balls']].wtd.mean() - 1 #df[[col1, col2]].wtd.mean()
    PPI_df = pp_sr[['striker','PPI']]

    #PPI_df.sort_values('PPI',ascending=False).head(5)

#     <!-- **2. MDI (Middle Dot Index) :**
#      how a batter's Dot% compares to others' (median) Dot% in Middle overs -->

    df_mid = df_exp[df_exp['phase']=='middle']

    mid_dot = df_mid.groupby('striker').agg(  
        num_innings = ('match_id','nunique'),
        runs = ('runs_off_bat','sum'),
        balls = ('is_faced_by_batter' ,'sum'),
        dots = ('isDotforBatter','sum')
    ).reset_index()

    mid_dot['dot_'] = mid_dot['dots']/mid_dot['balls']

    mid_dot = mid_dot[(mid_dot.balls>=4)&(mid_dot.num_innings>=1)]

    mid_dot['MDI'] = mid_dot[['dot_','balls']].wtd.mean()/mid_dot['dot_'] - 1
    MDI_df = mid_dot[['striker','MDI']]

    #MDI_df.sort_values('MDI',ascending=False).head(5)

#     <!-- **3. DFI (Death Finishing Index) :**
#      how a batter's SR compares to others' (median) SR in Death -->

    df_de = df_exp[df_exp['phase']=='death']

    de_sr = df_de.groupby('striker').agg(  
        num_innings = ('match_id','nunique'),
        runs = ('runs_off_bat','sum'),
        balls = ('is_faced_by_batter' ,'sum')
    ).reset_index()

    de_sr['strike_rate'] = 100*de_sr['runs']/de_sr['balls']

    #de_sr = de_sr[(de_sr.balls>=25)&(de_sr.num_innings>=2)]

    de_sr['DFI'] = de_sr['strike_rate']/de_sr[['strike_rate','balls']].wtd.mean() - 1
    DFI_df = de_sr[['striker','DFI']]

    #DFI_df.sort_values('DFI',ascending=False).head(5)

#     <!-- **4. High-Impact Over Index (HOI)**  
#     Measures performance in high-impact overs:

#     Powerplay: bonus if >=10 runs scored
#     Middle: bonus if >=9 runs scored
#     Death: bonus if >=12 runs scored

#     COI = Sum of (bonus_overs) / overs_batted
#          -->

    phase_bat = df_exp.groupby(['match_id','striker','phase','over'])[['runs_off_bat','is_faced_by_batter']].sum().reset_index()
    phase_bat['bonus_pt'] = phase_bat[['phase','runs_off_bat']].apply(
                                                        lambda x: 1 if (x[0]=='pp' and x[1]>=10)
                                                             else 1 if (x[0]=='middle' and x[1]>=9)
                                                             else 1 if (x[0]=='death' and x[1]>=12)
                                                             else 0,
                                                        axis=1
    )

    phase_bat = phase_bat.groupby('striker')[['bonus_pt','is_faced_by_batter']].sum().reset_index()
    phase_bat['HOI'] = 6*phase_bat['bonus_pt']/phase_bat['is_faced_by_batter']

    HOI_df = phase_bat[['striker','HOI']]

    #HOI_df.sort_values('HOI', ascending=False).head(5)



#     <!-- **5. Chase-Capability index (CCI)**  
#     Measures performance in high-reqd rr period:

#     SR under Reqd Rr>=10 vs how others fare -->

    df_rr = df_exp[df_exp['reqd_run_rate']>=10]

    rr_sr = df_rr.groupby('striker').agg(  
        num_innings = ('match_id','nunique'),
        runs = ('runs_off_bat','sum'),
        balls = ('is_faced_by_batter' ,'sum')
    ).reset_index()

    rr_sr['strike_rate'] = 100*rr_sr['runs']/rr_sr['balls']

    rr_sr = rr_sr[(rr_sr.balls>=25)&(rr_sr.num_innings>=2)]

    rr_sr['CCI'] = rr_sr['strike_rate']/rr_sr[['strike_rate','balls']].wtd.mean() - 1
    CCI_df = rr_sr[['striker','CCI']]

    #CCI_df.sort_values('CCI',ascending=False).head(5)



#     <!-- **6. Expected Runs Increased (ERI)**

#     Estimate what an average batter would have scored in same #balls (e.g., by match avg SR)
#     ERS = (Actual Runs Scored-Expected )
#      -->

    inn_sr = df_exp.groupby(['match_id','innings'])[['runs_off_bat','is_faced_by_batter']].sum().reset_index()
    inn_sr['inn_SR'] = 100*inn_sr['runs_off_bat']/inn_sr['is_faced_by_batter']

    bat_sr = df_exp.groupby(['match_id','innings','striker'])[['runs_off_bat','is_faced_by_batter']].sum().reset_index()
    bat_sr['SR'] = 100*bat_sr['runs_off_bat']/bat_sr['is_faced_by_batter']

    #bat_sr = bat_sr[bat_sr['is_faced_by_batter']>=2]

    bat_sr = bat_sr.merge(inn_sr[['match_id','innings','inn_SR']], on=['match_id','innings'], how='inner')
    bat_sr['ERI'] = bat_sr['runs_off_bat'] - bat_sr['inn_SR']*bat_sr['is_faced_by_batter']/100

    #bat_sr = bat_sr.groupby('striker')['ERI'].mean().reset_index() #################
    bat_sr = weighted_mean(bat_sr, value_col='ERI', weight_col='is_faced_by_batter', group_col='striker')

    ERI_df = bat_sr[['striker','ERI']]
    ERI_df['ERI'] = ERI_df['ERI']*0.5

    #ERI_df.sort_values('ERI',ascending=False).head(5)



#     <!-- **7. Tail-batting index (TBI)**  
#     Measures performance in batting-with-tail period:

#     SR under non striker batting position>=8 vs how others fare -->

    df_tb = df_exp[df_exp['non_striker_batting_position']>=8]

    tb_sr = df_tb.groupby('striker').agg(  
        num_innings = ('match_id','nunique'),
        runs = ('runs_off_bat','sum'),
        balls = ('is_faced_by_batter' ,'sum')
    ).reset_index()

    tb_sr['strike_rate'] = 100*tb_sr['runs']/tb_sr['balls']

    tb_sr = tb_sr[(tb_sr.balls>=25)&(tb_sr.num_innings>=2)]

    tb_sr['TBI'] = tb_sr['strike_rate']/tb_sr[['strike_rate','balls']].wtd.mean() - 1
    TBI_df = tb_sr[['striker','TBI']]

    #TBI_df.sort_values('TBI',ascending=False).head(5)





#     <!-- **8. Partnership Value Added (PVA)**

#     recognizing batters who play key roles in building substantial partnerships, not just quick cameos.
#          -->

    df_exp.loc[df_exp.isWicket==1, 'partnership_runs'] = np.nan

    df_exp['partnership_runs'] = df_exp['partnership_runs'].fillna(method='ffill')
    df_exp.loc[df_exp.isWicket==1, 'partnership_runs'] = df_exp.loc[df_exp.isWicket==1, 'partnership_runs']+                                                df_exp.loc[df_exp.isWicket==1, 'total_runs']

    p_count = df_exp[df_exp['partnership_runs']>=30].groupby('striker')['match_id'].nunique().reset_index()
    s_count = df_exp.groupby('striker')['match_id'].nunique().reset_index()
    p_count.columns = ['striker','p_matches']
    s_count.columns = ['striker','matches']

    PVA_df = p_count.merge(s_count, on='striker', how='outer').fillna(0)
    PVA_df['PVA'] = PVA_df['p_matches']/PVA_df['matches']

    PVA_df = PVA_df[['striker','PVA']]
    PVA_df['PVA'] = PVA_df['PVA']*2.5
    #

    #PVA_df.sort_values('PVA',ascending=False).head()



#     <!-- **9. Over-reliance index (ORI)**

#     recognizing batters who elevate the team Eco while batting vs when not -->

    from collections import defaultdict

    grouped = df_exp.groupby(['match_id', 'batting_team'])

    batter_list = []
    with_rr_list = []
    without_rr_list = []

    for batter in df_exp['striker'].unique():
        with_runs = with_balls = wo_runs = wo_balls = 0

        match_teams = df_exp[df_exp['striker'] == batter][['match_id', 'batting_team']].drop_duplicates().values.tolist()

        for match_id, team in match_teams:
            group = grouped.get_group((match_id, team))

            mask_with = (group['striker'] == batter) | (group['non_striker'] == batter)
            subset_with = group[mask_with]
            with_runs += subset_with['total_runs'].sum()
            with_balls += subset_with['islegal'].sum()

            subset_wo = group[~mask_with]
            wo_runs += subset_wo['total_runs'].sum()
            wo_balls += subset_wo['islegal'].sum()

        with_rr = 6 * with_runs / with_balls if with_balls else 0
        without_rr = 6 * wo_runs / wo_balls if wo_balls else 0

        batter_list.append(batter)
        with_rr_list.append(with_rr)
        without_rr_list.append(without_rr)


    bat_dep = pd.DataFrame([batter_list,with_rr_list,without_rr_list]).T
    bat_dep.columns = ['striker','With_Run_Rate','Without_Run_Rate']
    bat_dep['ORI'] = bat_dep['With_Run_Rate']-bat_dep['Without_Run_Rate']

    ORI_df = bat_dep[['striker','ORI']]

    #ORI_df.sort_values('ORI',ascending=False).head(4)





#     <!-- **10. Stabilization-Ability index (SAI)**  
#     Measures performance in pressure-entry point:

#     SR, Avg after entry point being <=45 for >=3 -->

    entry_pt = df_exp.groupby(['striker','match_id'])[['last_fow','wickets_down']].first().reset_index()
    entry_pt = entry_pt[(entry_pt.last_fow<=45)&(entry_pt.wickets_down>=3)][['striker','match_id']]

    entry_ = {}
    batters = entry_pt['striker'].unique().tolist()
    for batter in batters:
        m = entry_pt[entry_pt['striker']==batter]['match_id'].unique().tolist()
        entry_[batter] = m

    batter_list = []
    sr_list = []
    avg_list = []

    for batter in entry_.keys():
        runs = 0
        balls = 0
        outs = 0
        for m in entry_[batter]:
            runs+= df_exp[(df_exp['striker']==batter)&(df_exp['match_id']==m)]['runs_off_bat'].sum()
            balls+= df_exp[(df_exp['striker']==batter)&(df_exp['match_id']==m)]['is_faced_by_batter'].sum()
            outs+= df_exp[(df_exp['match_id']==m)&(df_exp['player_dismissed']==batter)]['isWicket'].sum()
        sr = 100*runs/balls
        avg = (runs/outs) if outs>0 else runs

        batter_list.append(batter)
        sr_list.append(sr)
        avg_list.append(avg)

    SAI_df = pd.DataFrame()
    SAI_df['striker'] = batter_list
    SAI_df['SR'] = sr_list
    SAI_df['avg'] = avg_list
    SAI_df['SR_med'] = SAI_df['SR']/SAI_df['SR'].mean()
    SAI_df['avg_med'] = SAI_df['avg']/SAI_df['avg'].mean()
    SAI_df['SAI'] = SAI_df['SR_med']*SAI_df['avg_med'] - 1

    SAI_df = SAI_df[['striker','SAI']]
    #SAI_df.sort_values('SAI', ascending=False)



#     <!-- **11. Recent Form**

#     (avg+sr)/median(avg+sr) in last 3outings
#          -->

    players_list = df_exp['striker'].unique().tolist()
    bat_pl = df_exp[df_exp.striker.isin(players_list)]
    batter_match_id = {}

    # Collect last 3 match IDs for each batter
    for batter in bat_pl.striker.unique():
        matches = bat_pl[bat_pl.striker == batter].match_id.unique()[-3:].tolist()
        batter_match_id[batter] = matches

    df_bat = pd.DataFrame()

    # Extract relevant rows for last 3 matches
    for batter_name in players_list:
        last_3_matches = batter_match_id.get(batter_name, [])
        df_sub = bat_pl[(bat_pl.striker == batter_name) & (bat_pl.match_id.isin(last_3_matches))]
        if df_sub.shape[0] > 0:
            df_sub.reset_index(drop=True, inplace=True)
            df_bat = df_bat.append(df_sub)
        else:
            continue

    # Compute runs and balls
    df_bat['runs_scored'] = df_bat['runs_off_bat']
    batter_stats_form = df_bat.groupby('striker').agg(
        num_innings=('match_id', 'nunique'),
        runs=('runs_scored', 'sum'),
        balls=('is_faced_by_batter', 'sum'),
        #outs=('player_dismissed', lambda x: x.notna().sum())
    ).reset_index()

    batter_stats_form['outs'] = 0
    for batter in batter_stats_form.striker.unique():
        batter_outs = df_bat[df_bat['player_dismissed']==batter]['isWicket'].sum()
        batter_stats_form.loc[batter_stats_form.striker==batter, 'outs'] = batter_outs 


    # Handle avg and SR
    batter_stats_form['sr'] = 100 * batter_stats_form['runs'] / batter_stats_form['balls']
    batter_stats_form['avg'] = batter_stats_form.apply(
        lambda row: row['runs'] / row['outs'] if row['outs'] > 0 else row['runs'], axis=1
    )

    # Fill missing or infinite values
    batter_stats_form['sr'] = batter_stats_form['sr'].fillna(0)
    batter_stats_form['avg'] = batter_stats_form['avg'].fillna(0)
    batter_stats_form['sr+avg'] = batter_stats_form['sr']+batter_stats_form['avg']
    #batter_stats_form = batter_stats_form[batter_stats_form['balls']>=20]

    med = batter_stats_form[['sr+avg','balls']].wtd.mean()

    batter_stats_form['recent_form'] = (batter_stats_form['sr+avg'] / med) - 1

    # Final output
    RF_df = batter_stats_form[['striker', 'recent_form']]

    RF_df['recent_form'] = RF_df['recent_form']*3  ##triple value

    #RF_df.sort_values('recent_form', ascending=False).head(3)




#     <!-- **12. Run_Contribution impact (RCI)**

#     Run contribution per match, then median -->

    team_runs = (
        df_exp.groupby(['match_id', 'batting_team'])['total_runs']
        .sum()
        .reset_index()
        .rename(columns={'total_runs': 'team_runs'})
    )

    batter_runs = (
        df_exp.groupby(['striker', 'match_id', 'batting_team'])['total_runs']
        .sum()
        .reset_index()
        .rename(columns={'total_runs': 'batter_runs'})
    )

    merged = pd.merge(batter_runs, team_runs, on=['match_id', 'batting_team'], how='left')

    merged['contribution'] = merged['batter_runs'] / merged['team_runs']


    RCI_df = (
        merged.groupby('striker')['contribution']
        .mean()
        .reset_index()
        .rename(columns={'contribution': 'RCI'})
        .sort_values('RCI', ascending=False)
    )

    RCI_df['RCI'] = RCI_df['RCI']*2 ##double value

    #RCI_df.head(5)



#     <!-- **13. Boundary-Hitting Index (BHI)**

#     relative position wrt BpB, with balls faced>=100 -->

    bdry_df = df_exp.groupby('striker').agg( 
        balls = ('is_faced_by_batter','sum'),
        fours = ('isFour','sum'),
        sixes = ('isSix' ,'sum')
    ).reset_index()

    bdry_df = bdry_df[bdry_df['balls']>=35]
    bdry_df['bdry_ct'] = bdry_df['fours'] + bdry_df['sixes']
    bdry_df['bpb'] = bdry_df['balls']/bdry_df['bdry_ct']

    BHI_df = bdry_df[['striker','bpb','balls']]
    BHI_df['BHI'] = BHI_df[['bpb','balls']].wtd.mean()/BHI_df['bpb'] - 1
    BHI_df.drop(['bpb','balls'], axis=1, inplace=True)
    #BHI_df.sort_values('BHI', ascending=False).head(5)




#     <!-- **14. Dot-Avoidance Index (DAI)**

#     relative position wrt Dot%, with balls faced>=100 -->

    dot_df = df_exp.groupby('striker').agg( 
        balls = ('is_faced_by_batter','sum'),
        dots = ('isDotforBatter','sum'),
    ).reset_index()

    dot_df = dot_df[dot_df['balls']>=5]
    dot_df['dot_p'] = dot_df['dots']/dot_df['balls']

    DAI_df = dot_df[['striker','dot_p','balls']]
    DAI_df['DAI'] = DAI_df[['dot_p','balls']].wtd.mean()/DAI_df['dot_p'] - 1
    DAI_df.drop(['dot_p','balls'], axis=1, inplace=True)
    #DAI_df.sort_values('DAI', ascending=False).head(5)



#     <!-- **15. Batting Efficiency Rating (BER)**
#     Composite of avg, SR, dot%, bpb
#     Normalize each metric and combine:
#     BER = 0.3*normalized_avg + 0.3*normalized_SR + 0.2*(1-normalized_dot%) + 0.2*(1 - normalized_bpb) -->

    batter_stats = df_exp.groupby('striker').agg( 
        runs = ('runs_off_bat','sum'),
        balls = ('is_faced_by_batter','sum'),
        dots = ('isDotforBatter','sum'),
        fours = ('isFour','sum'),
        sixes = ('isSix' ,'sum')
    ).reset_index()

    batter_stats['outs'] = 0
    for batter in batter_stats.striker.unique():
        batter_outs = df_exp[df_exp['player_dismissed']==batter]['isWicket'].sum()
        batter_stats.loc[batter_stats.striker==batter, 'outs'] = batter_outs 

    batter_stats['bdry'] = batter_stats['fours']+batter_stats['sixes']
    batter_stats = batter_stats[batter_stats.balls>=100]
    batter_stats['avg'] = batter_stats['runs']/batter_stats['outs']
    batter_stats['SR'] = batter_stats['runs']/batter_stats['balls']
    batter_stats['dot'] = batter_stats['dots']/batter_stats['balls']
    batter_stats['bpb'] = batter_stats['balls']/batter_stats['bdry']

    batter_stats['norm_avg'] = batter_stats['avg']/batter_stats['avg'].mean()
    batter_stats['norm_sr'] = batter_stats['SR']/batter_stats['SR'].mean()
    batter_stats['norm_dot'] = batter_stats['dot'].mean()/batter_stats['dot']
    batter_stats['norm_bpb'] = batter_stats['bpb'].mean()/batter_stats['bpb']

    batter_stats['BER'] = 0.3*batter_stats['norm_avg']+0.3*batter_stats['norm_sr']+0.2*batter_stats['norm_dot']+0.2*batter_stats['norm_bpb']
    batter_stats['BER'] = batter_stats['BER'] - 1
    batter_stats['BER'] = batter_stats['BER']*2  ##double value
    BER_df = batter_stats[['striker','BER']]

    #BER_df.sort_values('BER',ascending=False).head(5)


#     <!-- **16. Wt. of Runs**
#     Runs Scored*0.01 -->

    players_list = df_exp['striker'].unique().tolist()
    bat_pl = df_exp[df_exp.striker.isin(players_list)]
    batter_match_id = {}

    # Collect last 15 match IDs for each batter
    for batter in bat_pl.striker.unique():
        matches = bat_pl[bat_pl.striker == batter].match_id.unique()[-15:].tolist()
        batter_match_id[batter] = matches

    df_bat = pd.DataFrame()

    # Extract relevant rows for last 15 matches
    for batter_name in players_list:
        last_15_matches = batter_match_id.get(batter_name, [])
        df_sub = bat_pl[(bat_pl.striker == batter_name) & (bat_pl.match_id.isin(last_15_matches))]
        if df_sub.shape[0] > 0:
            df_sub.reset_index(drop=True, inplace=True)
            df_bat = df_bat.append(df_sub)
        else:
            continue

    batter_stats = df_bat.groupby('striker').agg( 
        runs = ('runs_off_bat','sum')
        ).reset_index()
    batter_stats['WR'] = batter_stats['runs']*0.01
    WR_df = batter_stats[['striker','WR']]

    #WR_df.sort_values('WR',ascending=False).head(5)



#     <!-- **17. Hold-the-Fort index (HFI)**
#     avg #partnerships involved in per match * 2.5 -->

    pw_df = df_exp.groupby(['striker','match_id']).agg( 
        partners = ('non_striker','nunique')
    ).reset_index()

    HFI_df = pw_df.groupby('striker')['partners'].mean().reset_index()

    HFI_df['partners'] = HFI_df['partners']-2
    HFI_df['partners'] = HFI_df['partners']*2.5
    #HFI_df.sort_values('partners', ascending=False).head(5)



#     <!-- **18. MIQ (Match Quality Index)**
#     MIQ = (Batter_SR / Innings_SR) × (Phase_Weight1) × (Runs_Scored / Team_Runs) × (Phase_Weight2) × (Not_Out_Bonus)

#     phase wt1 -->
#     Powerplay	1.1
#     Middle overs	1.3
#     Death	1.0

#     phase wt2 -->
#     Powerplay	1.0
#     Middle overs	1.2
#     Death	1.4 -->

    #phase_wise runs, SR, wts 1 & 2
    
    phase_runs = df_exp.groupby(['match_id','striker','phase'])[['runs_off_bat','is_faced_by_batter']]                                            .sum().reset_index()
    phase_runs['SR'] = phase_runs['runs_off_bat']/phase_runs['is_faced_by_batter']
    phase_runs['p_w_2'] = 1.4
    phase_runs.loc[phase_runs['phase']=='pp','p_w_2'] = 1.0
    phase_runs.loc[phase_runs['phase']=='middle','p_w_2'] = 1.2
    phase_runs.loc[phase_runs['phase']=='death','p_w_2'] = 1.4

    phase_runs['pw2_mult'] = phase_runs['p_w_2']*phase_runs['is_faced_by_batter']

    bat_wts = phase_runs.groupby(['match_id','striker'])[['runs_off_bat','is_faced_by_batter','pw2_mult']]                                .sum().reset_index()
    bat_wts['pw2'] = bat_wts['pw2_mult']/bat_wts['is_faced_by_batter']

    bat_wts = bat_wts[['match_id','striker','runs_off_bat','is_faced_by_batter','pw2']]


    #batter_sr / inn_sr
    inn_sr = df_exp.groupby(['match_id','innings'])[['runs_off_bat','is_faced_by_batter']].sum().reset_index()
    inn_sr['inn_SR'] = 100*inn_sr['runs_off_bat']/inn_sr['is_faced_by_batter']

    bat_sr = df_exp.groupby(['match_id','innings','striker'])[['runs_off_bat','is_faced_by_batter']].sum().reset_index()
    bat_sr['SR'] = 100*bat_sr['runs_off_bat']/bat_sr['is_faced_by_batter']
    bat_sr = bat_sr.merge(inn_sr[['match_id','innings','inn_SR']], on=['match_id','innings'], how='inner')

    bat_sr['comp_1'] = bat_sr['SR']/bat_sr['inn_SR']

    #print('bat_sr', bat_sr.columns)
    #Runs_Scored / Team_Runs
    entry_pt = df_exp.groupby(['striker','match_id','batting_team'])['last_fow'].first().reset_index()

    team_runs = (
        df_exp.groupby(['match_id', 'batting_team'])['total_runs']
        .sum()
        .reset_index()
        .rename(columns={'total_runs': 'team_runs'})
    )

    batter_runs = (
        df_exp.groupby(['striker', 'match_id', 'batting_team'])['total_runs']
        .sum()
        .reset_index()
        .rename(columns={'total_runs': 'batter_runs'})
    )
    batter_runs = batter_runs.merge(entry_pt, on=['striker', 'match_id', 'batting_team'], how='outer')

    merged = pd.merge(batter_runs, team_runs, on=['match_id','batting_team'], how='left')
    merged['team_runs_after'] = merged['team_runs']-merged['last_fow']
    merged['team_runs_b4_p'] = merged['last_fow'] / merged['team_runs']
    merged['pw1'] = (1-merged['team_runs_b4_p'])*5

    merged['comp_2'] = merged['batter_runs'] / merged['team_runs_after']

    #print('merged', merged.columns)

    #not out count & bonus
    no_df = df_exp.groupby(['match_id','player_dismissed'])['isWicket'].sum().reset_index()
    no_df = no_df.rename(columns={'player_dismissed':'striker'})
    no_df['no_bonus'] = 1
    no_df['comp_3'] = no_df['isWicket']*no_df['no_bonus']


    merge_on = ['match_id','striker']
    MIQ_df = bat_wts.merge(bat_sr.merge(merged.merge(no_df, on=merge_on, how='outer'), on=merge_on, how='outer'),
                           on=merge_on, how='outer')

    MIQ_df = MIQ_df[['match_id','striker','batter_runs','comp_1','pw1','comp_2','pw2','comp_3']]
    MIQ_df['comp_3'] = MIQ_df['comp_3'].fillna(1.1)
    MIQ_df = MIQ_df[MIQ_df.batter_runs>=10]
    MIQ_df['MIQ'] = MIQ_df['comp_1']*MIQ_df['pw1']*MIQ_df['comp_2']*MIQ_df['pw2']*MIQ_df['comp_3']
    #MIQ_df['MIQ'] = MIQ_df['MIQ']+1
    #MIQ_df['MIQ'] = MIQ_df['MIQ']

    MIQ_df = MIQ_df.groupby('striker')['MIQ'].median().reset_index()
    MIQ_df['MIQ'] = MIQ_df['MIQ']*5
    #MIQ_df.sort_values('MIQ', ascending=False).head(10)


    ################################################################




    df_list = [team_df,PPI_df,MDI_df,DFI_df,HOI_df,CCI_df,ERI_df,TBI_df,PVA_df,ORI_df,SAI_df,
              RF_df,RCI_df,BHI_df,DAI_df,BER_df,WR_df,HFI_df,MIQ_df] #WR_df,

    all_df = team_df
    for df in df_list[1:]:

        #df[df.columns[1]] = df[df.columns[1]]/(df[df.columns[1]].max()-df[df.columns[1]].min())
        all_df = all_df.merge(df, on='striker', how='outer')
    all_df = all_df.fillna(0)
    all_df['score'] = all_df[all_df.columns[5:].values].sum(axis=1)
    all_df = all_df[(all_df['runs']>=100)&(all_df['num_innings']>=5)].dropna(subset=['team'])                                .sort_values('score', ascending=False).reset_index(drop=True)

    all_df['rank'] = all_df.index+1
    all_df = all_df.rename(columns={'striker':'batter'})

    return all_df


# ## comparison function

# In[143]:


def compare_batter_ranks(old_df, new_df):
    old_df = old_df.copy()
    new_df = new_df.copy()
    
    old_df['rank'] = old_df['rank'].astype(int)
    new_df['rank'] = new_df['rank'].astype(int)

    # 1. New entries
    old_batters = set(old_df['batter'])
    new_batters = set(new_df['batter'])
    new_entries = new_batters - old_batters
    if new_entries:
        print("🔹 New Entries:")
        print(new_df[new_df['batter'].isin(new_entries)].sort_values(by='rank')[['batter', 'rank']])
    else:
        print("🔹 No new entries.")
    print()
    print('---'*10)
    print()

    # Merge for comparison
    merged = pd.merge(old_df, new_df, on='batter', how='inner', suffixes=('_old', '_new'))

    # 2. Major rank changes (±5 or more)
    merged['rank_change'] = merged['rank_old'] - merged['rank_new']
    major_changes = merged[(merged['rank_change'].abs() >= 5) & (merged['rank_new'] <= 20)]

    if not major_changes.empty:
        print("🔹 Major Rank Changes (±5 or more):")
        print(major_changes[['batter', 'rank_old', 'rank_new', 'rank_change']].sort_values(by='rank_change', key=abs))
    else:
        print("🔹 No major rank changes.")
    print()
    print('---'*10)
    print()

    # 3. Moved out of Top 10
    top10_old = old_df.nsmallest(10, 'rank')['batter']
    top10_new = new_df.nsmallest(10, 'rank')['batter']
    
    moved_out = set(top10_old) - set(top10_new)
    if moved_out:
        print("🔹 Moved out of Top 10:")
        moved_out_df = pd.merge(
            old_df[old_df['batter'].isin(moved_out)],
            new_df[['batter', 'rank']].rename(columns={'rank': 'rank_new'}),
            on='batter',
            how='left'
        )
        print(moved_out_df[['batter', 'rank', 'rank_new']].rename(columns={'rank': 'rank_old'}).sort_values(by='rank_old'))
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
            new_df[new_df['batter'].isin(moved_in)],
            old_df[['batter', 'rank']].rename(columns={'rank': 'rank_old'}),
            on='batter',
            how='left'
        )
        print(moved_in_df[['batter', 'rank', 'rank_old']].rename(columns={'rank': 'rank_new'}).sort_values(by='rank_new'))
    else:
        print("🔹 No new entries into Top 10.")
    print()
    print('---'*10)
    print()


# In[ ]:





# ## applying

# In[145]:


#all_df = batter_ranking(df_exp)
df_old = df_exp[~(df_exp['match_id'].isin(df_exp['match_id'].unique()[-2:].tolist()))]

all_df = batter_ranking(df_exp)
all_df_old = batter_ranking(df_old)
all_df['score'] = all_df['score'].apply(lambda x: min(x,30+random.random()))
all_df = all_df.sort_values('score', ascending=False).reset_index(drop=True)
all_df.to_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/Stats/batter_ranking.csv', index=None)


# In[146]:


all_df = all_df[['batter','team','rank','score']]
all_df_old = all_df_old[['batter','team','rank','score']]


# In[147]:


compare_batter_ranks(all_df_old, all_df)


# In[ ]:




