#!/usr/bin/env python
# coding: utf-8

# In[5]:


import pandas as pd
import glob
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# In[20]:


df_all = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/df_all_round_sim.csv')


# In[21]:


bowl_rank = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/Stats/bowler_ranking.csv')
bat_rank = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/Stats/batter_ranking.csv')


# df_all.match_id.unique()

# In[22]:


##reading all STATS from one excel##
excel_filename = "/Users/roumyadas/Desktop/IPL_Simulation/Season_02/STATS_S02.xlsx"

batter_stats = pd.read_excel(excel_filename, sheet_name='BAT')
bowler_stats = pd.read_excel(excel_filename, sheet_name='BOWL')
pts_table = pd.read_excel(excel_filename, sheet_name='POINTS_TABLE')
player_stats = pd.read_excel(excel_filename, sheet_name='MVP_points')
#---------#
dots_stats = pd.read_excel(excel_filename, sheet_name='Most_Dots')
fours_stats = pd.read_excel(excel_filename, sheet_name='Most_Fours')
sixes_stats = pd.read_excel(excel_filename, sheet_name='Most_Sixes')
run_contribution = pd.read_excel(excel_filename, sheet_name='Most_Run_Contribution')
wkt_contribution = pd.read_excel(excel_filename, sheet_name='Most_Wkt_Contribution')
#---------#
w3_stats = pd.read_excel(excel_filename, sheet_name='Most_3wkt_hauls')
r50_stats = pd.read_excel(excel_filename, sheet_name='Most_50+_scores')
eco_stats = pd.read_excel(excel_filename, sheet_name='Lowest_Economy')
sr_stats = pd.read_excel(excel_filename, sheet_name='Best_Strike_Rate')
    
    
print(f"Excel file '{excel_filename}' read successfully with 13 sheets!")


# In[23]:


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

# Get the index of the highest score for each striker (resolving ties using fewer balls)
idx = mbm.groupby('player')['runs_off_bat'].idxmax()

# Filter the rows
highest_scores = mbm.loc[idx]

highest_scores['high_score'] = highest_scores['runs_off_bat'].astype(str)+ highest_scores['out_str']+ str(' (')+                                    highest_scores['is_faced_by_batter'].astype(str)+str(')')
        

highest_scores = highest_scores.rename(columns={'player':'striker'})

batter_stats_2 = batter_stats.merge(highest_scores[['striker','high_score']], on='striker',how='left')
batter_stats_2 = batter_stats_2.round(2)
#########ADDING HIGHEST SCORES##############


# batter_stats_2

# In[24]:


#########ADDING BEST PERFORMANCE##############
mbm_ball_bat = df_all.groupby(['bowler','match_id'])[['runs_conceeded','islegal','isBowlerWicket']]                     .sum().reset_index()

mbm_ball_bat = mbm_ball_bat.rename(columns={'bowler': 'player'})
mbm_ball_bat['isBowlerWicket'] = mbm_ball_bat['isBowlerWicket'].fillna(0).astype(int)

# Sort with priority: max wickets → min balls → min runs
mbm_ball_bat = mbm_ball_bat.sort_values(by=['player', 'isBowlerWicket', 'islegal', 'runs_conceeded'],
                                        ascending=[True, False, True, True])

# Get index of best performance per bowler
idx = mbm_ball_bat.groupby('player').head(1).index

most_wkts = mbm_ball_bat.loc[idx].copy()

most_wkts['best_performance'] = (
    most_wkts['isBowlerWicket'].astype(str) + '-' +
    most_wkts['runs_conceeded'].astype(str) + ' (' +
    most_wkts['islegal'].astype(str) + ')'
)

most_wkts = most_wkts.rename(columns={'player': 'bowler'})

# Merge with main stats
bowler_stats_2 = bowler_stats.merge(most_wkts[['bowler', 'best_performance']], on='bowler', how='left')
bowler_stats_2 = bowler_stats_2.round(2)
#########ADDING BEST PERFORMANCE##############


# In[25]:


#########ADDING Best batting performance##############
mbm_team_bat_ball = df_all.groupby(['batting_team','match_id','bowling_team'])[['total_runs','islegal','isWicket']]                                    .sum().reset_index().sort_values(by='batting_team')

mbm_team_bat_ball = mbm_team_bat_ball.rename(columns={'batting_team':'team','total_runs':'runs',
                                'islegal':'balls','isWicket':'wickets','bowling_team':'opposition'})

mbm_team_bat_ball['wickets'] = mbm_team_bat_ball['wickets'].fillna(0).astype(int)

mbm_team_bat_ball = mbm_team_bat_ball.sort_values(by=['runs', 'wickets'], ascending=[False, True])

# Get the best bowling performance index (highest wickets, then lowest runs)
idx = mbm_team_bat_ball.groupby('team').head(1).index


# Filter the rows
highest_scores = mbm_team_bat_ball.loc[idx]

highest_scores['highest_batting_total'] = highest_scores['runs'].astype(str)+ '-'+ highest_scores['wickets'].astype(str)+            ' (' + highest_scores['balls'].astype(str)+ ')' + ' vs '+ highest_scores['opposition'].astype(str) +            ' in ' + highest_scores['match_id'].astype(str)

#########ADDING Best bowling performance##############
mbm_team_ball_bat = df_all.groupby(['bowling_team','match_id','batting_team'])[['total_runs','islegal','isWicket']]                                    .sum().reset_index().sort_values(by='bowling_team')

mbm_team_ball_bat = mbm_team_ball_bat.rename(columns={'bowling_team':'team','total_runs':'runs',
                                'islegal':'balls','isWicket':'wickets','batting_team':'opposition'})

mbm_team_ball_bat['wickets'] = mbm_team_ball_bat['wickets'].fillna(0).astype(int)

mbm_team_ball_bat = mbm_team_ball_bat.sort_values(by=['wickets', 'runs'], ascending=[False, True])

# Get the best bowling performance index (highest wickets, then lowest runs)
idx = mbm_team_ball_bat.groupby('team').head(1).index

# Filter the rows
lowest_scores = mbm_team_ball_bat.loc[idx]

lowest_scores['best_bowling_performance'] = lowest_scores['runs'].astype(str)+ '-'+                 lowest_scores['wickets'].astype(str)+                 ' (' + lowest_scores['balls'].astype(str)+ ')'+ ' vs '+ lowest_scores['opposition'].astype(str)+            ' in ' + lowest_scores['match_id'].astype(str)
        
#lowest_scores[['team','best_bowling_performance']]
######################
        
best_performance = highest_scores[['team','highest_batting_total']]        .merge(lowest_scores[['team','best_bowling_performance']], on='team')

best_performance = best_performance.sort_values(by='team')


# In[ ]:





# In[ ]:





# 1. Print the schedule (MatchID, Date, Team one, Team two)
# 2. Use the .py mechanism for winner, POTM
# 3. Print the totals of both teams, along with wickets
# 4. Calculate the runs scored and wickets taken for each match, and print the top scorer and bowler
# 5. Figure out what the POTM did, and write it
# 6. Write a match summary of fixed format

# In[26]:


matches_info = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Fixtures/IPL_2024_schedule.xlsx',
                            sheet_name='Season_02')

matches_info = matches_info[['Date','num','Team One', 'Team Two']]
matches_info = matches_info.rename(columns={'num':'Match_Num','Team One':'Home','Team Two':'Away'})


matches_info['match_id'] = matches_info['Match_Num'].apply(lambda x: 'S02M00' + str(x) if x<=9 else 'S02M0' + str(x))

matches_info['POTM'] = ''
for idx,row in matches_info.iterrows():
    match = row['match_id']
    top_point = ''
    if match in df_all['match_id'].unique():
        #print(match)
        df_mod = df_all[df_all['match_id']==match].reset_index(drop=True)
        df_mod_1 = df_mod[df_mod['innings']==1]
        df_mod_2 = df_mod[df_mod['innings']==2]

        bowler_stats = df_mod_1.groupby(['bowler','bowling_team']).agg(   ##,'innings'
                        runs = ('runs_conceeded','sum'),
                        balls = ('islegal' ,'sum'),
                        wkts = ('isBowlerWicket','sum'),
                        dots = ('isDotforbowler','sum')

                    ).reset_index()

        bowler_stats['economy'] = 6*bowler_stats['runs']/bowler_stats['balls']

        bowler_stats = bowler_stats.sort_values(['wkts','economy'], ascending=[False, True]).reset_index(drop=True)
        #batting stats

        batter_stats = df_mod_1.groupby(['striker','batting_team']).agg(  ##,'innings'
            runs = ('runs_off_bat','sum'),
            balls = ('is_faced_by_batter' ,'sum'),
            fours = ('isFour','sum'),
            sixes = ('isSix','sum'),
            out = ('is_striker_Out','sum'),
            dots = ('isDotforBatter','sum')

        ).reset_index()

        batter_stats['strike_rate'] = 100*batter_stats['runs']/batter_stats['balls']
        for index,row in batter_stats.iterrows():
            batter = row['striker']
            if (batter in df_mod_1.player_dismissed.unique())==True:

                new_out_value = 1
                batter_stats.at[index, 'out'] = new_out_value

        batter_stats['out'] = batter_stats['out'].replace(0,'N/O')
        batter_stats['out'] = batter_stats['out'].replace(1,'out')

        batter_stats = batter_stats.sort_values(['runs','strike_rate'], ascending=[False,False]).reset_index(drop=True)

        batter_stats = batter_stats.round(2)
        bowler_stats = bowler_stats.round(2)

        batter_stats['points'] = 0
        bowler_stats['points'] = 0

        for index, row in batter_stats.iterrows():
            #batting
            run_pt = row['runs']*1
            bdry_pt = row['fours']*1+row['sixes']*2
            dot_pt = row['dots']*(-0.25)

            sr_pt = 6 if row['strike_rate']>=170 else 4 if row['strike_rate']>150 else 2 if row['strike_rate']>130 else                     0 if row['strike_rate']>70 else -2 if row['strike_rate']>=60 else -4 if row['strike_rate']>=50 else -6

            milestone_pt = 16 if row['runs']>=100 else 8 if row['runs']>=50 else 4 if row['runs']>=30 else 0

            total_pt = run_pt+bdry_pt+dot_pt+sr_pt+milestone_pt

            batter_stats.at[index, 'points'] = total_pt

        for index, row in bowler_stats.iterrows():
            #bowling
            wkt_pt = row['wkts']*25
            wkt_bonus_pt = (16 if row['wkts']>=5 else 8 if row['wkts']>=4 else 4 if row['wkts']>=3 else 0)
            dot_pt = row['dots']*0.25

            eco_pt = -6 if row['economy']>12 else -4 if row['economy']>11 else -2 if row['economy']>=10 else                       0 if row['economy']>7 else 2 if row['economy']>=6 else 4 if row['economy']>=5 else 6 

            total_pt = wkt_pt+wkt_bonus_pt+dot_pt+eco_pt

            bowler_stats.at[index, 'points'] = total_pt


        ######## points dictionary
        bat_pt = batter_stats[['striker','points']].rename(columns={'striker':'player','points':'points1'})
        bowl_pt = bowler_stats[['bowler','points']].rename(columns={'bowler':'player','points':'points1'})
        pt1 = pd.concat([bat_pt,bowl_pt],axis=0)


        #####-------------------------------------------------------------------------------------------#####

        bowler_stats = df_mod_2.groupby(['bowler','bowling_team']).agg(   ##,'innings'
                        runs = ('runs_conceeded','sum'),
                        balls = ('islegal' ,'sum'),
                        wkts = ('isBowlerWicket','sum'),
                        dots = ('isDotforbowler','sum')

                    ).reset_index()

        bowler_stats['economy'] = 6*bowler_stats['runs']/bowler_stats['balls']

        bowler_stats = bowler_stats.sort_values(['wkts','economy'], ascending=[False, True]).reset_index(drop=True)

        #batting stats

        batter_stats = df_mod_2.groupby(['striker','batting_team']).agg(  ##,'innings'
            runs = ('runs_off_bat','sum'),
            balls = ('is_faced_by_batter' ,'sum'),
            fours = ('isFour','sum'),
            sixes = ('isSix','sum'),
            outs = ('is_striker_Out','sum'),
            dots = ('isDotforBatter','sum')

        ).reset_index()

        batter_stats['strike_rate'] = 100*batter_stats['runs']/batter_stats['balls']
        for index,row in batter_stats.iterrows():
            batter = row['striker']
            if batter in df_mod_2.player_dismissed.unique():
                new_out_value = 1
                batter_stats.at[index, 'outs'] = new_out_value

        batter_stats['outs'] = batter_stats['outs'].replace(0,'N/O')
        batter_stats['outs'] = batter_stats['outs'].replace(1,'out')

        batter_stats = batter_stats.sort_values(['runs','strike_rate'], ascending=[False,False]).reset_index(drop=True)

        batter_stats = batter_stats.round(2)
        bowler_stats = bowler_stats.round(2)


        batter_stats['points'] = 0
        bowler_stats['points'] = 0

        for index, row in batter_stats.iterrows():
            #batting
            run_pt = row['runs']*1
            bdry_pt = row['fours']*1+row['sixes']*2
            dot_pt = row['dots']*(-0.25)

            sr_pt = 6 if row['strike_rate']>=170 else 4 if row['strike_rate']>150 else 2 if row['strike_rate']>130 else                     0 if row['strike_rate']>70 else -2 if row['strike_rate']>=60 else -4 if row['strike_rate']>=50 else -6

            milestone_pt = 16 if row['runs']>=100 else 8 if row['runs']>=50 else 4 if row['runs']>=30 else 0

            total_pt = run_pt+bdry_pt+dot_pt+sr_pt+milestone_pt

            batter_stats.at[index, 'points'] = total_pt

        for index, row in bowler_stats.iterrows():
            #bowling
            wkt_pt = row['wkts']*25
            wkt_bonus_pt = (16 if row['wkts']>=5 else 8 if row['wkts']>=4 else 4 if row['wkts']>=3 else 0)
            dot_pt = row['dots']*0.25

            eco_pt = -6 if row['economy']>12 else -4 if row['economy']>11 else -2 if row['economy']>=10 else                       0 if row['economy']>7 else 2 if row['economy']>=6 else 4 if row['economy']>=5 else 6 

            total_pt = wkt_pt+wkt_bonus_pt+dot_pt+eco_pt

            bowler_stats.at[index, 'points'] = total_pt


        ######## points dictionary
        bat_pt = batter_stats[['striker','points']].rename(columns={'striker':'player','points':'points2'})
        bowl_pt = bowler_stats[['bowler','points']].rename(columns={'bowler':'player','points':'points2'})
        pt2 = pd.concat([bat_pt,bowl_pt],axis=0)


        pts = pt1.merge(pt2, on='player', how='outer')
        pts.fillna(0, inplace=True)
        pts['points'] = pts['points1']+pts['points2']
        pts.sort_values(by='points', ascending=False, inplace=True)

        top_point = pts.head(1).player.unique()[0]


    matches_info.at[idx,'POTM'] = top_point
    #print(top_point)
        

matches_info['Winner'] = ''
matches_info['POTM_performance'] = ''
matches_info['Top_Scorer'] = ''
matches_info['Top_Bowler'] = ''
matches_info['Match_Report'] = ''



for index,row in matches_info.iterrows():
    match = row['match_id']
    potm = row['POTM']
    if match in df_all['match_id'].unique():
        df_mod = df_all[df_all['match_id']==match].reset_index(drop=True)
        inn1_score = df_mod[df_mod.innings==1].runs_scored.max()
        inn2_score = df_mod[df_mod.innings==2].runs_scored.max()
        inn1_team = df_mod[df_mod.innings==1]['batting_team'].unique()[0]
        inn2_team = df_mod[df_mod.innings==2]['batting_team'].unique()[0]
        
        
        bat_1st = df_mod['batting_team'].unique()[0]
        bat_2nd = df_mod['batting_team'].unique()[1]

        if inn1_score>inn2_score:
            winner = inn1_team
        elif inn1_score<inn2_score:
            winner = inn2_team
         
        home = row['Home']
        away = row['Away']
        home_total = df_mod[df_mod['batting_team']==home].runs_scored.max()
        away_total = df_mod[df_mod['batting_team']==away].runs_scored.max()
        home_wkts = df_mod[df_mod['batting_team']==home].wickets_down.max()
        away_wkts = df_mod[df_mod['batting_team']==away].wickets_down.max()
        home_balls = df_mod[df_mod['batting_team']==home].legal_balls_bowled.max()
        away_balls = df_mod[df_mod['batting_team']==away].legal_balls_bowled.max()
        
        home_overs = str(home_balls//6)+'.'+str(home_balls%6)
        away_overs = str(away_balls//6)+'.'+str(away_balls%6)
        
        home_score = str(home_total)+'-'+str(home_wkts)+' ('+str(home_overs)+')'
        away_score = str(away_total)+'-'+str(away_wkts)+' ('+str(away_overs)+')'
        
        
        #top_score
        top_scores = df_mod.groupby(['striker','batting_team'])['runs_off_bat','is_faced_by_batter'].sum().reset_index()                            .sort_values(by=['runs_off_bat','is_faced_by_batter'], ascending=[False,True])
        
        top_scorer = top_scores.head(1) 
        ts_arr = top_scorer.values[0]
        top_batter = ts_arr[0]
        n_o_i = ''
        if top_batter not in df_mod['player_dismissed'].unique():
            n_o_i = '*'
        
        top_scorer = ts_arr[0] + ' ('+ts_arr[1]+')'+' -> '+str(ts_arr[2])+n_o_i+' off '+str(ts_arr[-1])
        
        

        #top_bowler
        top_bowlers = df_mod.groupby(['bowler','bowling_team'])['isBowlerWicket','runs_conceeded','islegal'].sum().reset_index()                    .sort_values(by=['isBowlerWicket','runs_conceeded','islegal'], ascending=[False,True,False])
        
        top_bowler = top_bowlers.head(1)

        tb_arr = top_bowler.values[0]
        ov = str(tb_arr[-1]//6)+'.'+str(tb_arr[-1]%6)
        top_bowler = tb_arr[0] + ' ('+tb_arr[1]+')'+' -> '+str(tb_arr[2])+'-'+str(tb_arr[-2])+' ('+str(ov)+')'

        #potm performance
        n_o_i = ''
        if potm not in df_mod['player_dismissed'].unique():
            n_o_i = '*'
        potm_bat_score = ''
        potm_ball_score = ''
        bat_ind = 0
        ball_ind = 0
        if potm in top_scores['striker'].unique():
            bat_ind = 1
            potm_bat = top_scores[top_scores['striker']==potm].values[0]
            potm_team = potm_bat[0] + ' ('+potm_bat[1]+')'+' -> '
            potm_bat_score = str(potm_bat[2])+n_o_i+' off '+str(potm_bat[-1])
        
        if potm in top_bowlers['bowler'].unique():
            ball_ind = 1
            potm_ball = top_bowlers[top_bowlers['bowler']==potm].values[0]
            ov = str(potm_ball[-1]//6)+'.'+str(potm_ball[-1]%6)
            potm_team = potm_ball[0] + ' ('+potm_ball[1]+')'+' -> '
            potm_ball_score = str(potm_ball[2])+'-'+str(potm_ball[-2])+' ('+str(ov)+')'
            
        if (bat_ind==1) & (ball_ind==1):
            potm_perf = potm_team + potm_bat_score+' ; '+potm_ball_score
        elif ball_ind==0:
            potm_perf = potm_team + potm_bat_score
        else:
            potm_perf = potm_team + potm_ball_score
        
        #match summary
        home_perf = home +' '+str(home_score)
        away_perf = away +' '+str(away_score)
        report = ''
        #win_diff = 
        if winner==home:
            if winner==bat_1st:
                win_diff = int(home_total)-int(away_total)
                report = home_perf+' beat '+away_perf+' by '+str(win_diff)+' run'+('s' if win_diff>1 else '')+'!'
            else:
                wkt_diff = 10-home_wkts
                report = home_perf+' beat '+away_perf+' by '+str(wkt_diff)+' wicket'+('s' if wkt_diff>1 else '')+'!'
        else: #winner==away
            if winner==bat_1st:
                win_diff = int(away_total)-int(home_total)
                report = away_perf+' beat '+home_perf+' by '+str(win_diff)+' run'+('s' if win_diff>1 else '')+'!'
            else:
                wkt_diff = 10-away_wkts
                report = away_perf+' beat '+home_perf+' by '+str(wkt_diff)+' wicket'+('s' if wkt_diff>1 else '')+'!'
        
        
        
        
        #value setting
        matches_info.at[index,'Winner'] = winner
        matches_info.at[index,'POTM_performance'] = potm_perf
        matches_info.at[index,'Top_Scorer'] = top_scorer
        matches_info.at[index,'Top_Bowler'] = top_bowler
        matches_info.at[index,'Match_Report'] = report
        
    
        
    


# In[27]:


rating_list = []
for m in matches_info['Match_Num']:
    if len(str(m))==1:
        m = '0'+str(m)
    path = f'/Users/roumyadas/Desktop/IPL_Simulation/Season_02/Match_Rating/Match_{m}.txt'
    try:
        txts = pd.read_fwf(path)
        rating_list.append(str(txts.iloc[0]).split('    ')[0].split('Match Rating: ')[1])
    except:
        rating_list.append('')


# In[28]:


matches_info = matches_info[['Date','Match_Num','Home','Away','Winner','POTM_performance',
             'Top_Scorer','Top_Bowler','Match_Report']]

matches_info['Date'] = matches_info['Date'].dt.strftime("%Y-%m-%d")
matches_info['Match_Rating'] = pd.Series(rating_list)


# In[ ]:





# In[29]:


matches_info_mod = matches_info.copy()
matches_info_mod['POTM'] = ''
for index,row in matches_info_mod.iterrows():
    potm = row['POTM_performance'].split('(')[0].strip()
    matches_info_mod.at[index, 'POTM'] = potm

matches_info_mod = matches_info_mod[matches_info_mod['POTM']!='']    
potm_count = matches_info_mod.groupby('POTM')['POTM_performance'].count().reset_index()
potm_count.columns = ['player','num_POTM_awards']


# In[30]:


player_stats = player_stats.merge(potm_count, on='player', how='left')
player_stats['num_POTM_awards'] = player_stats['num_POTM_awards'].fillna(0)
player_stats['num_POTM_awards'] = player_stats['num_POTM_awards'].astype(int)


# In[31]:


## catches

catches_df = df_all[df_all['wicket_event']=='Caught'].groupby(['fielder','bowling_team'])['wicket_event'].count().reset_index()

#catches_df
catches_df.columns = ['player','team','#catches']
catches_df = catches_df.sort_values('#catches',ascending=False)

## runouts
runout_ = df_all[(df_all['wicket_event']=='Stumped/Runout by Keeper')|(df_all['wicket_type']=='runout')]

if runout_.shape[0]>0:
    runout_df = runout_.groupby(['fielder','bowling_team'])['player_dismissed'].count().reset_index()
    
    runout_df.columns = ['player','team','#runout/stumping']
    catches_df = catches_df.merge(runout_df,on=['player','team'],how='outer')
    catches_df = catches_df.fillna(0)


# In[ ]:





# ## fantasy points

# In[18]:


points_df = pd.DataFrame(columns=['player','points'])


for match in df_all.match_id.unique():
    df_sub = df_all[df_all['match_id']==match]
    #bowler
    bowler_stats = df_sub.groupby(['bowler','bowling_team']).agg(   ##,'innings'
                        runs = ('runs_conceeded','sum'),
                        balls = ('islegal' ,'sum'),
                        wkts = ('isBowlerWicket','sum'),
                        dots = ('isDotforbowler','sum')

                    ).reset_index()

    bowler_stats['economy'] = 6*bowler_stats['runs']/bowler_stats['balls']

    bowler_stats = bowler_stats.sort_values(['wkts','economy'], ascending=[False, True]).reset_index(drop=True)
    #batting stats

    batter_stats = df_sub.groupby(['striker','batting_team']).agg(  ##,'innings'
        runs = ('runs_off_bat','sum'),
        balls = ('is_faced_by_batter' ,'sum'),
        fours = ('isFour','sum'),
        sixes = ('isSix','sum'),
        out = ('is_striker_Out','sum'),
        dots = ('isDotforBatter','sum')

    ).reset_index()

    batter_stats['strike_rate'] = 100*batter_stats['runs']/batter_stats['balls']
    for index,row in batter_stats.iterrows():
        batter = row['striker']
        if (batter in df_sub.player_dismissed.unique())==True:

            new_out_value = 1
            batter_stats.at[index, 'out'] = new_out_value

    batter_stats['out'] = batter_stats['out'].replace(0,'N/O')
    batter_stats['out'] = batter_stats['out'].replace(1,'out')

    batter_stats = batter_stats.sort_values(['runs','strike_rate'], ascending=[False,False]).reset_index(drop=True)

    batter_stats = batter_stats.round(2)
    bowler_stats = bowler_stats.round(2)

    batter_stats['points'] = 0
    bowler_stats['points'] = 0

    for index, row in batter_stats.iterrows():
        #batting
        run_pt = row['runs']*1
        bdry_pt = row['fours']*1+row['sixes']*2
        dot_pt = row['dots']*(-0.25)

        sr_pt = 6 if row['strike_rate']>=170 else 4 if row['strike_rate']>150 else 2 if row['strike_rate']>130 else                 0 if row['strike_rate']>70 else -2 if row['strike_rate']>=60 else -4 if row['strike_rate']>=50 else -6

        milestone_pt = 16 if row['runs']>=100 else 8 if row['runs']>=50 else 4 if row['runs']>=30 else 0

        total_pt = run_pt+bdry_pt+dot_pt+sr_pt+milestone_pt

        batter_stats.at[index, 'points'] = total_pt

    for index, row in bowler_stats.iterrows():
        #bowling
        wkt_pt = row['wkts']*25
        wkt_bonus_pt = (16 if row['wkts']>=5 else 8 if row['wkts']>=4 else 4 if row['wkts']>=3 else 0)
        dot_pt = row['dots']*0.25

        eco_pt = -6 if row['economy']>12 else -4 if row['economy']>11 else -2 if row['economy']>=10 else                   0 if row['economy']>7 else 2 if row['economy']>=6 else 4 if row['economy']>=5 else 6 

        total_pt = wkt_pt+wkt_bonus_pt+dot_pt+eco_pt

        bowler_stats.at[index, 'points'] = total_pt
        
    bat_pt = batter_stats[['striker','batting_team','points']].rename(columns={'striker':'player',
                                                                               'batting_team':'team'})
    bowl_pt = bowler_stats[['bowler','bowling_team','points']].rename(columns={'bowler':'player',
                                                                              'bowling_team':'team'})
    points_df = points_df.append(pd.concat([bat_pt,bowl_pt],axis=0))

points_df = points_df.sort_values('points',ascending=False)

points_df = points_df.groupby(['player','team'])['points'].sum().reset_index()

points_df = points_df.sort_values('points',ascending=False)


# In[32]:


matches_info


# # saving the sheets

# In[33]:


##saving all STATS in one excel##
excel_filename = "/Users/roumyadas/Desktop/IPL_Simulation/Season_02/STATS_S02.xlsx"

# Use ExcelWriter to write multiple sheets
with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
    batter_stats_2.to_excel(writer, sheet_name='BAT', index=False)
    bowler_stats_2.to_excel(writer, sheet_name='BOWL', index=False)
    pts_table.to_excel(writer, sheet_name='POINTS_TABLE', index=False)
    player_stats.to_excel(writer, sheet_name='MVP_points', index=False)
    player_stats.to_excel(writer, sheet_name='Fantasy_points', index=False)
    catches_df.to_excel(writer, sheet_name='Fielding', index=False)
    #---------#
    dots_stats.to_excel(writer, sheet_name='Most_Dots', index=False)
    fours_stats.to_excel(writer, sheet_name='Most_Fours', index=False)
    sixes_stats.to_excel(writer, sheet_name='Most_Sixes', index=False)
    run_contribution.to_excel(writer, sheet_name='Most_Run_Contribution', index=False)
    wkt_contribution.to_excel(writer, sheet_name='Most_Wkt_Contribution', index=False)
    #---------#
    w3_stats.to_excel(writer, sheet_name='Most_3wkt_hauls', index=False)
    r50_stats.to_excel(writer, sheet_name='Most_50+_scores', index=False)
    eco_stats.to_excel(writer, sheet_name='Lowest_Economy', index=False)
    sr_stats.to_excel(writer, sheet_name='Best_Strike_Rate', index=False)
    #---------#
    best_performance.to_excel(writer, sheet_name='Team_best_Performance', index=False)
    matches_info.to_excel(writer, sheet_name='Match_Summary', index=False)
    
    
print(f"Excel file '{excel_filename}' created successfully with 15 sheets!")


# ## adding batter stats in phases, and exit_pt stats

# In[34]:


df_sim = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/df_all_round_sim.csv')
df_sim['over_1'] = df_sim['legal_balls_bowled']//6
df_sim['over_2'] = df_sim['legal_balls_bowled']%6
df_sim['over_1'] = df_sim['over_1'].astype(str)
df_sim['over_2'] = df_sim['over_2'].astype(str)

df_sim['over'] = df_sim['over_1'] + "." +  df_sim['over_2']
df_sim['over'] = df_sim['over'].astype(float)

df_sim.drop(['over_1','over_2'],axis=1,inplace=True)
df_sim['over_'] = np.ceil(df_sim['over'])
df_sim['over_'] = df_sim['over_'].astype(int)

df_sim['phase'] = np.where(df_sim['over']<=6, "PP", np.where(df_sim['over']<=15, "Middle", "Death"))


def exit_pt_stats(batter, team):
    import warnings
    warnings.filterwarnings('ignore')
    import numpy as np

    # --- phase-wise stats
    phase_wise = df_sim[df_sim.striker == batter]                    .groupby(['match_id', 'phase'])[['runs_off_bat', 'is_faced_by_batter']]                    .sum().reset_index()

    # Create the performance descriptions
    phase_wise['PP_perf'] = phase_wise.apply(
        lambda x: f"{x['runs_off_bat']} off {x['is_faced_by_batter']}" if x['phase'] == 'PP' else np.nan,
        axis=1
    )
    phase_wise['Middle_perf'] = phase_wise.apply(
        lambda x: f"{x['runs_off_bat']} off {x['is_faced_by_batter']}" if x['phase'] == 'Middle' else np.nan,
        axis=1
    )
    phase_wise['Death_perf'] = phase_wise.apply(
        lambda x: f"{x['runs_off_bat']} off {x['is_faced_by_batter']}" if x['phase'] == 'Death' else np.nan,
        axis=1
    )

    # Now pivot it properly: one row per match_id
    phase_wise = phase_wise.groupby('match_id')[['PP_perf', 'Middle_perf', 'Death_perf']].first().reset_index()

    # --- match-wise stats
    match_wise = df_sim[df_sim.striker == batter]                    .groupby(['match_id', 'innings'])[['runs_off_bat', 'is_faced_by_batter']]                    .sum().reset_index()
    match_wise.columns = ['match_id', 'innings', 'runs', 'balls']
    match_wise['SR'] = (100 * match_wise['runs'] / match_wise['balls']).round(2)

    # --- final match score
    final_score = df_sim.groupby(['match_id', 'innings'])[['total_runs', 'islegal', 'isWicket']]                    .sum().reset_index()
    final_score.columns = ['match_id', 'innings', 'final_score', 'total_balls', 'wkts']

    # --- exit points
    exit_pts = df_sim[df_sim.player_dismissed == batter].groupby('match_id').tail(1).reset_index(drop=True)
    exit_pts['exit_pt_score'] = exit_pts.apply(
        lambda x: f"{x['runs_scored']}-{x['wickets_down']}({x['legal_balls_bowled']//6}.{x['legal_balls_bowled']%6})",
        axis=1
    )
    exit_pts = exit_pts[['match_id', 'exit_pt_score']]

    # --- merge
    match_exit = match_wise.merge(final_score.merge(exit_pts, on='match_id', how='left'), 
                                  on=['match_id', 'innings'], how='inner')

    # --- win/loss
    win_ = []
    for m in match_exit['match_id'].unique():
        t_runs = df_sim[(df_sim['match_id'] == m) & (df_sim['batting_team'] == team)]['runs_scored'].max()
        other_runs = df_sim[(df_sim['match_id'] == m) & (df_sim['batting_team'] != team)]['runs_scored'].max()
        win = 1 if t_runs > other_runs else 0
        win_.append(win)
    match_exit['win'] = win_

    # --- final merge
    match_exit = match_exit.merge(phase_wise, on='match_id', how='left')
    match_exit['batter'] = batter
    match_exit['team'] = team

    #print(f"{batter}, from {team}")
    return match_exit


# In[35]:


batter_stats = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/batter_stats.csv')

batter_stats_mod = batter_stats[batter_stats.runs>=100]
exit_pt_df = pd.DataFrame()
for batter in batter_stats_mod['striker'].unique():
    batter = batter
    team = batter_stats_mod[batter_stats_mod.striker==batter]['batting_team'].unique()[0]
    exit_pt_df = exit_pt_df.append(exit_pt_stats(batter,team))


# In[ ]:





# ## bowler stats each phase wise

# In[36]:


def phase_bowl_stats(bowler, team):
    import warnings
    warnings.filterwarnings('ignore')
    import numpy as np

    # --- phase-wise stats
    phase_wise = df_sim[df_sim.bowler == bowler]                    .groupby(['match_id', 'phase'])[['runs_conceeded', 'islegal','isBowlerWicket']]                    .sum().reset_index()

    # Create the performance descriptions
    phase_wise['PP_perf'] = phase_wise.apply(
        lambda x: f"{x['isBowlerWicket']}-{x['runs_conceeded']}({x['islegal']})" if x['phase'] == 'PP' else np.nan,
        axis=1
    )
    phase_wise['Middle_perf'] = phase_wise.apply(
        lambda x: f"{x['isBowlerWicket']}-{x['runs_conceeded']}({x['islegal']})" if x['phase'] == 'Middle' \
        else np.nan,
        axis=1
    )
    phase_wise['Death_perf'] = phase_wise.apply(
        lambda x: f"{x['isBowlerWicket']}-{x['runs_conceeded']}({x['islegal']})" if x['phase'] == 'Death' \
        else np.nan,
        axis=1
    )

    # Now pivot it properly: one row per match_id
    phase_wise = phase_wise.groupby('match_id')[['PP_perf', 'Middle_perf', 'Death_perf']].first().reset_index()

    # --- match-wise stats
    match_wise = df_sim[df_sim.bowler == bowler]                    .groupby(['match_id', 'innings'])[['runs_conceeded', 'islegal','isBowlerWicket']]                    .sum().reset_index()
    match_wise.columns = ['match_id', 'innings', 'runs', 'balls','wkts']
    match_wise['Eco'] = (6 * match_wise['runs'] / match_wise['balls']).round(2)

    # --- final match score
    final_score = df_sim.groupby(['match_id', 'innings'])[['total_runs', 'islegal', 'isWicket']]                    .sum().reset_index()
    final_score.columns = ['match_id', 'innings', 'final_score', 'total_balls', 'wkts_lost']

    # --- merge
    match_exit = match_wise.merge(final_score, 
                                  on=['match_id', 'innings'], how='inner')

    # --- win/loss
    win_ = []
    for m in match_exit['match_id'].unique():
        t_runs = df_sim[(df_sim['match_id'] == m) & (df_sim['batting_team'] == team)]['runs_scored'].max()
        other_runs = df_sim[(df_sim['match_id'] == m) & (df_sim['batting_team'] != team)]['runs_scored'].max()
        win = 1 if t_runs > other_runs else 0
        win_.append(win)
    match_exit['win'] = win_

    # --- final merge
    match_exit = match_exit.merge(phase_wise, on='match_id', how='left')
    match_exit['bowler'] = bowler
    match_exit['team'] = team

    #print(f"{bowler}, from {team}")
    return match_exit


# In[37]:


bowler_stats = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/bowler_stats.csv')

bowler_stats_mod = bowler_stats[bowler_stats.balls>=24]
phase_bowl_stat = pd.DataFrame()
for bowler in bowler_stats_mod['bowler'].unique():
    bowler = bowler
    team = bowler_stats_mod[bowler_stats_mod.bowler==bowler]['bowling_team'].unique()[0]
    phase_bowl_stat = phase_bowl_stat.append(phase_bowl_stats(bowler,team))


# In[ ]:





# ##### phase-wise team stats, batting & bowling in two sheets

# In[38]:


phase_ball_tm = df_sim.groupby(['bowling_team','phase'])                        [['runs_conceeded','islegal','isWicket']].sum().reset_index()

phase_ball_tm['eco'] = 6*phase_ball_tm['runs_conceeded']/phase_ball_tm['islegal']
phase_ball_tm['SR'] = phase_ball_tm['islegal']/phase_ball_tm['isWicket']

phase_ball_tm = phase_ball_tm.rename(columns={'isWicket':'wkts'})

phase_ball_tm = phase_ball_tm[['bowling_team','phase','wkts','eco','SR']].round(2)
phase_ball_tm = phase_ball_tm.sort_values(by='bowling_team')


# In[39]:


phase_bat_tm = df_sim.groupby(['batting_team','phase'])                        [['total_runs','islegal','isWicket']].sum().reset_index()

phase_bat_tm['avg'] = phase_bat_tm['total_runs']/phase_bat_tm['isWicket']
phase_bat_tm['SR'] = 100*phase_bat_tm['total_runs']/phase_bat_tm['islegal']

phase_bat_tm = phase_bat_tm.rename(columns={'isWicket':'outs'})


phase_bat_tm = phase_bat_tm[['batting_team','phase','outs','avg','SR']].round(2)
phase_bat_tm = phase_bat_tm.sort_values(by='batting_team')


# In[ ]:





# # customizing the sheets

# In[40]:


import pandas as pd

#excel_filename = "/Users/roumyadas/Desktop/IPL_Simulation/Season_02/STATS_S02.xlsx"


# Dictionary mapping sheet names to DataFrames
sheets_data = {
    'BAT': batter_stats_2,
    'BOWL': bowler_stats_2,
    'POINTS_TABLE': pts_table,
    'MVP_points': player_stats,
    'Fantasy_points': points_df,
    'Bowler_Ranking': bowl_rank[['bowler','team','score','rank']],
    'Batter_Ranking': bat_rank[['batter','team','score','rank']],
    'Fielding': catches_df,
    'Most_Dots': dots_stats,
    'Most_Fours': fours_stats,
    'Most_Sixes': sixes_stats,
    'Most_Run_Contribution': run_contribution,
    'Most_Wkt_Contribution': wkt_contribution,
    'Most_3wkt_hauls': w3_stats,
    'Most_50+_scores': r50_stats,
    'Lowest_Economy': eco_stats,
    'Best_Strike_Rate': sr_stats,
    'Team_best_Performance': best_performance,
    'Match_Summary': matches_info,
    'exit_pt_stats': exit_pt_df,
    'phase_bowl_stats': phase_bowl_stat,
    'Phase_wise_team_bowling': phase_ball_tm,
    'Phase_wise_team_batting': phase_bat_tm
    
}

with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
    # Writing all sheets
    for sheet_name, df in sheets_data.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Get workbook
    workbook = writer.book  

    # Define formats
    bold_format = workbook.add_format({'bold': True})  # Bold text
    large_font_format = workbook.add_format({'font_size': 14})  # Increased font size
    red_text_format = workbook.add_format({'font_color': 'red'})  # Red text

    # Apply formatting to each sheet
    for sheet_name, df in sheets_data.items():
        worksheet = writer.sheets[sheet_name]
        
        # 1️⃣ Bold all column names (header row)
        for col_idx, col_name in enumerate(df.columns):
            worksheet.write(0, col_idx, col_name, bold_format)
        
        # 3️⃣ Bold entire column 1 (index 0) of every sheet
        worksheet.set_column(0, 0, None, bold_format)

        # 2️⃣ Increase font size of last column in 'POINTS_TABLE'
        if sheet_name == 'POINTS_TABLE':
            last_col_idx = len(df.columns) - 1  # Last column index
            worksheet.set_column(last_col_idx, last_col_idx, None, large_font_format)

        # 4️⃣ Conditional formatting for 'run_contribution_%' in 'Most_Run_Contribution'
        if sheet_name == 'Most_Run_Contribution' and 'run_contribution_%' in df.columns:
            col_idx = df.columns.get_loc('run_contribution_%')  # Get column index
            worksheet.conditional_format(1, col_idx, len(df), col_idx, 
                                {'type': 'cell', 'criteria': '>=', 'value': 30, 'format': red_text_format})

        # 5️⃣ Conditional formatting for 'wkt_contribution_%' in 'Most_Wkt_Contribution'
        if sheet_name == 'Most_Wkt_Contribution' and 'wkt_contribution_%' in df.columns:
            col_idx = df.columns.get_loc('wkt_contribution_%')  # Get column index
            worksheet.conditional_format(1, col_idx, len(df), col_idx, 
                                {'type': 'cell', 'criteria': '>=', 'value': 30, 'format': red_text_format})
            
        # 6️⃣ Adjust column widths dynamically
        for col_idx, col_name in enumerate(df.columns):
            max_length = max(df[col_name].astype(str).apply(len).max(), len(col_name))  # Max of column values & header
            worksheet.set_column(col_idx, col_idx, max_length + 2)  # Adding padding for readability
            
        # 7️⃣ Freeze the first row of every sheet
        worksheet.freeze_panes(1, 0)
        
        # 8️⃣ **Add Filter to all columns**
        worksheet.autofilter(0, 0, 0, len(df.columns) - 1)  # Apply filter to the first row across all columns


print(f"Excel file '{excel_filename}' created successfully with formatting!")


# In[ ]:





# try:
#     abc = batter_stats[batter_stats['striker']=='VR Iyer'][['runs','strike_rate']].values.tolist()[0]
# except:
#     abc = [0,'not played']
#     
# abc

# ## team stats
# 
# excel_filename = "/Users/roumyadas/Desktop/IPL_Simulation/STATS_S01.xlsx"
# destination = "/Users/roumyadas/Desktop/IPL_Simulation/Teams/team stats/"
# 
# 
# 
# batter_stats = pd.read_excel(excel_filename, sheet_name='BAT')
# bowler_stats = pd.read_excel(excel_filename, sheet_name='BOWL')
# pts_table = pd.read_excel(excel_filename, sheet_name='POINTS_TABLE')
# player_stats = pd.read_excel(excel_filename, sheet_name='MVP_points')
# #---------#
# dots_stats = pd.read_excel(excel_filename, sheet_name='Most_Dots')
# fours_stats = pd.read_excel(excel_filename, sheet_name='Most_Fours')
# sixes_stats = pd.read_excel(excel_filename, sheet_name='Most_Sixes')
# run_contribution = pd.read_excel(excel_filename, sheet_name='Most_Run_Contribution')
# wkt_contribution = pd.read_excel(excel_filename, sheet_name='Most_Wkt_Contribution')
# #---------#
# w3_stats = pd.read_excel(excel_filename, sheet_name='Most_3wkt_hauls')
# r50_stats = pd.read_excel(excel_filename, sheet_name='Most_50+_scores')
# eco_stats = pd.read_excel(excel_filename, sheet_name='Lowest_Economy')
# sr_stats = pd.read_excel(excel_filename, sheet_name='Best_Strike_Rate')
# #---------#
# best_perf = pd.read_excel(excel_filename, sheet_name='Team_best_Performance')
# summ = pd.read_excel(excel_filename, sheet_name='Match_Summary')
# 
# #---------#
# 
# 
# teams = ['CSK','DC','GT','KKR','LSG','MI','PBKS','RCB','RR','SRH']
# 
# ts_dfs = {}
# 
# dfs = [batter_stats,bowler_stats,pts_table,player_stats,
# dots_stats,fours_stats,sixes_stats,run_contribution,
# wkt_contribution,w3_stats,r50_stats,eco_stats,
# sr_stats,best_perf,summ]
# 
# cols_1 = ['batting_team','bowling_team','team','team',
# 'bowling_team','batting_team','batting_team','batting_team',
# 'bowling_team','bowling_team','batting_team','bowling_team',
# 'batting_team','team']
# cols_2 = ['Home','Away']
# 
# for t_ in teams:
#     for i in range(len(dfs)):
#         df_ = dfs[i]
#         col_ = cols_1[i]
#         df_sub = df_[df_[col_]==t_].reset_index(drop=True)
#         ts_dfs[t_] = df_sub
#         ts_dfs[t_].to_excel()

# import random
# 
# random.seed(7) 
# value = random.sample((0, 1), 1)[0]
# print(value)
# random.sample(('Bat','Bowl'),1)[0]
# 

# 1 --> Home, Bat
# 4 --> Home, Bowl
# 5 --> Away, Bowl
# 7 --> Away, Bat

# batter_stats.to_csv('/Users/roumyadas/Desktop/IPL_Simulation/batter_stats_upd.csv', index=None)
# bowler_stats.to_csv('/Users/roumyadas/Desktop/IPL_Simulation/bowler_stats_upd.csv', index=None)

# In[ ]:




