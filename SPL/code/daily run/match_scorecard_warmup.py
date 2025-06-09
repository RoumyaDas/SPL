from contextlib import redirect_stdout
import discord
import random
import os
import asyncio

import pandas as pd
import requests

#########################

import pandas as pd
import glob
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

matches_list = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx',
                            sheet_name='Schedule')

matches_list = matches_list[['Date','Team One','Team Two']]

team_CSK = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='CSK')
team_CSK = team_CSK.sort_values(by='XI').head(11)
team_CSK_B = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='CSK (2)')
team_CSK_B = team_CSK_B.sort_values(by='XI').head(11)
####

team_DC = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='DC')
team_DC = team_DC.sort_values(by='XI').head(11)
team_DC_B = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='DC (2)')
team_DC_B = team_DC_B.sort_values(by='XI').head(11)
####

team_GT = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='GT')
team_GT = team_GT.sort_values(by='XI').head(11)
team_GT_B = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='GT (2)')
team_GT_B = team_GT_B.sort_values(by='XI').head(11)
####

team_KKR = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='KKR')
team_KKR = team_KKR.sort_values(by='XI').head(11)
team_KKR_B = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='KKR (2)')
team_KKR_B = team_KKR_B.sort_values(by='XI').head(11)

####

team_LSG = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='LSG')
team_LSG = team_LSG.sort_values(by='XI').head(11)
team_LSG_B = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='LSG (2)')
team_LSG_B = team_LSG_B.sort_values(by='XI').head(11)
####

team_MI = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='MI')
team_MI = team_MI.sort_values(by='XI').head(11)
team_MI_B = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='MI (2)')
team_MI_B = team_MI_B.sort_values(by='XI').head(11)
####

team_PBKS = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='PBKS')
team_PBKS = team_PBKS.sort_values(by='XI').head(11)
team_PBKS_B = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='PBKS (2)')
team_PBKS_B = team_PBKS_B.sort_values(by='XI').head(11)
####

team_RCB = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='RCB')
team_RCB = team_RCB.sort_values(by='XI').head(11)
team_RCB_B = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='RCB (2)')
team_RCB_B = team_RCB_B.sort_values(by='XI').head(11)
####

team_RR = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='RR')
team_RR = team_RR.sort_values(by='XI').head(11)
team_RR_B = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='RR (2)')
team_RR_B = team_RR_B.sort_values(by='XI').head(11)
####

team_SRH = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='SRH')
team_SRH = team_SRH.sort_values(by='XI').head(11)
team_SRH_B = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03 warmup.xlsx', 
                        sheet_name='SRH (2)')
team_SRH_B = team_SRH_B.sort_values(by='XI').head(11)
####


def team_map(value):
    if value=='CSK':
        return team_CSK
    elif value=='CSK_B':
        return team_CSK_B
    elif value=='DC':
        return team_DC
    elif value=='DC_B':
        return team_DC_B
    elif value=='GT':
        return team_GT
    elif value=='GT_B':
        return team_GT_B
    elif value=='KKR':
        return team_KKR
    elif value=='KKR_B':
        return team_KKR_B
    elif value=='LSG':
        return team_LSG
    elif value=='LSG_B':
        return team_LSG_B
    elif value=='MI':
        return team_MI
    elif value=='MI_B':
        return team_MI_B
    elif value=='PBKS':
        return team_PBKS
    elif value=='PBKS_B':
        return team_PBKS_B
    elif value=='RCB':
        return team_RCB
    elif value=='RCB_B':
        return team_RCB_B
    elif value=='RR':
        return team_RR
    elif value=='RR_B':
        return team_RR_B
    elif value=='SRH':
        return team_SRH
    elif value=='SRH_B':
        return team_SRH_B
    else:
        return pd.DataFrame()
    
#match_id = match_id

def match_scorecard(match_id, df_all):
    # Specify the output file
    output_file = "/Users/roumyadas/Desktop/IPL_Simulation/experimentation/Scorecards/matchcard_" + str(match_id) + ".txt"

    m_id = int(match_id.replace('S03M',''))
    # Redirect the output
    with open(output_file, "w") as f:
        with redirect_stdout(f):
            
            m_id = int(match_id.replace('S03M',''))
            teams = matches_list.iloc[m_id-1][1:].values[0], matches_list.iloc[m_id-1][1:].values[1]
            print(f"Match between {teams[0]}(H) and {teams[1]} !! ")
            print("```match about to begin```")
    
            ## bowler stats

            df_mod_1 = df_all[(df_all.match_id==match_id)&(df_all.innings==1)]
            df_mod_2 = df_all[(df_all.match_id==match_id)&(df_all.innings==2)]
            
            team1 = df_mod_1.batting_team.unique()[0]
            team2 = df_mod_2.batting_team.unique()[0]


            total_1 = df_mod_1['total_runs'].sum()
            extra_1 = df_mod_1['extras'].sum()
            total_2 = df_mod_2['total_runs'].sum()
            extra_2 = df_mod_2['extras'].sum()

            wickets_1 = df_mod_1['isWicket'].sum()
            wickets_2 = df_mod_2['isWicket'].sum()

            balls_1 = df_mod_1['legal_balls_bowled'].max()
            balls_2 = df_mod_2['legal_balls_bowled'].max()
            overs_1 = str(balls_1//6)+"."+str(balls_1%6)
            overs_2 = str(balls_2//6)+"."+str(balls_2%6)


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

                sr_pt = 6 if row['strike_rate']>=170 else 4 if row['strike_rate']>150 else 2 if row['strike_rate']>130 else \
                        0 if row['strike_rate']>70 else -2 if row['strike_rate']>=60 else -4 if row['strike_rate']>=50 else -6

                milestone_pt = 16 if row['runs']>=100 else 8 if row['runs']>=50 else 4 if row['runs']>=30 else 0

                total_pt = run_pt+bdry_pt+dot_pt+sr_pt+milestone_pt
                
                batter_stats.at[index, 'points'] = total_pt
                
            for index, row in bowler_stats.iterrows():
                #bowling
                wkt_pt = row['wkts']*25
                wkt_bonus_pt = (16 if row['wkts']>=5 else 8 if row['wkts']>=4 else 4 if row['wkts']>=3 else 0)
                dot_pt = row['dots']*0.25

                eco_pt = -6 if row['economy']>12 else -4 if row['economy']>11 else -2 if row['economy']>=10 else \
                          0 if row['economy']>7 else 2 if row['economy']>=6 else 4 if row['economy']>=5 else 6 

                total_pt = wkt_pt+wkt_bonus_pt+dot_pt+eco_pt
                
                bowler_stats.at[index, 'points'] = total_pt
                
                
            ######## points dictionary
            bat_pt = batter_stats[['striker','points']].rename(columns={'striker':'player','points':'points1'})
            bowl_pt = bowler_stats[['bowler','points']].rename(columns={'bowler':'player','points':'points1'})
            pt1 = pd.concat([bat_pt,bowl_pt],axis=0)
            
            
            
            print("---" * 10)
            print("  "*5)
            print("innings 1")
            print("```first inning begins```")
            
            print(f"{team2} BOWLING ---")
            print("^^"*10)
            #print(bowler_stats)
            
            print("---" * 10)
            print("  "*5)
            
            ###############
            
            separator = "---" * 10  # Separator line

            # Print column names
            print(separator)
            line = " | ".join(bowler_stats.drop('bowling_team', axis=1).columns)
            print('```', line, '```')
            print(separator)
            
            # Print rows one by one
            for _, row in bowler_stats.drop('bowling_team', axis=1).iterrows():
                line = " | ".join(map(str, row.values))  # Convert values to strings and join with "|"
                print('```', line, '```')
                print(separator)  # Add separator after each row

            print("  "*5)
            print(f"Extras = {extra_1}")
            print("  "*5)
            
            
            #########################################
            bat_1st_team = team_map(team1)['Func_Name']
            bat_2nd_team = team_map(team2)['Func_Name']

            cols_card = ['player_dismissed','batting_team','wicket_event','wicket_type','fielder','bowler','runs_scored','wickets_down']
            out_df = df_all[df_all['match_id']==match_id][df_all['isWicket']==1][cols_card]

            batter_stats_mod = pd.DataFrame()

            for player in bat_1st_team:
                if player in batter_stats['striker'].values:
                    out_info = out_df[out_df['player_dismissed'] == player]
                    bat_info = batter_stats[batter_stats['striker'] == player]

                    # Handle empty DataFrames to avoid KeyError
                    wkt_type = out_info['wicket_event'].iloc[0] if not out_info.empty else None
                    wkt_type_ = out_info['wicket_type'].iloc[0] if not out_info.empty else None
                    fielder = out_info['fielder'].iloc[0] if not out_info.empty else None
                    bowler = out_info['bowler'].iloc[0] if not out_info.empty else None
                    runs = bat_info['runs'].iloc[0] if not bat_info.empty else 0
                    balls = bat_info['balls'].iloc[0] if not bat_info.empty else 0
                    sr = bat_info['strike_rate'].iloc[0] if not bat_info.empty else 0

                    row = {'player': player, 'wkt_type': wkt_type, 'wkt_type_': wkt_type_, 'fielder': fielder,
                           'bowler': bowler, 'runs': int(runs), 'balls': int(balls), 'strike_rate': sr}

                    # Append to DataFrame instead of just printing
                    batter_stats_mod = batter_stats_mod.append(row, ignore_index=True)

            batter_stats_mod['wicket_event'] = ''

            for idx,row in batter_stats_mod.iterrows():
                wkt = row['wkt_type']
                wkt_ = row['wkt_type_']
                fielder = row['fielder']
                bowler = row['bowler']

                event = 'Not Out'
                if wkt=='Bowled':
                    event = f"Bo {bowler}"
                elif (wkt=='LBW'):
                    event = f"LBW {bowler}"
                elif wkt=='Caught':
                    event = f"C {fielder} B {bowler}"
                elif wkt=='HitWicket':
                    event = "Hit-Wicket"
                elif wkt=='Stumped/Runout by Keeper':
                    event = f"Stumped/Runout by {fielder}"

                if wkt_=='runout':
                    event = f"Run-out by {fielder}"

                batter_stats_mod.loc[idx, 'wicket_event'] = event

            batter_stats_mod[['runs','balls']] = batter_stats_mod[['runs','balls']].astype(int)
            ######################################################

            
            
            
            #########################################
            
            ###############
            
            print("--"*5)
            print(f"{team1} BATTING --")
            print("^^"*10)
            #print(batter_stats.drop(['fours','sixes','dots'], axis=1))
            print("---" * 10)
            print("  "*5)
            
            ###############
            batter_stats_mod = batter_stats_mod[['player','wicket_event','runs','balls','strike_rate']]
            
            separator = "---" * 10  # Separator line

            # Print column names
            print(separator)
            line = " | ".join(batter_stats_mod.columns)
            print('```', line, '```')
            print(separator)
            
            # Print rows one by one
            for _, row in batter_stats_mod.iterrows():
                line = " | ".join(map(str, row.values))  # Convert values to strings and join with "|"
                print('```', line, '```')
                print(separator)  # Add separator after each row

            
            ###############
            
            print("---" * 10)
            print("  "*5)
            print("<.>."*5)
            print("  "*5)
            print(f"Score :: {total_1}-{wickets_1}  ({overs_1}), run-rate = {np.round(6*total_1/balls_1, 2)}")
            print("***"*10)
            print("***"*10)

            
            
            bowler_stats = df_mod_2.groupby(['bowler','bowling_team']).agg(   ##,'innings'
                runs = ('runs_conceeded','sum'),
                balls = ('islegal' ,'sum'),
                wkts = ('isBowlerWicket','sum'),
                dots = ('isDotforbowler','sum')

            ).reset_index()

            bowler_stats['economy'] = 6*bowler_stats['runs']/bowler_stats['balls']

            bowler_stats = bowler_stats.sort_values(['wkts','economy'], ascending=[False, True]).reset_index(drop=True)

            #batting stats

            batter_stats_2 = df_mod_2.groupby(['striker','batting_team']).agg(  ##,'innings'
                runs = ('runs_off_bat','sum'),
                balls = ('is_faced_by_batter' ,'sum'),
                fours = ('isFour','sum'),
                sixes = ('isSix','sum'),
                outs = ('is_striker_Out','sum'),
                dots = ('isDotforBatter','sum')

            ).reset_index()

            batter_stats_2['strike_rate'] = 100*batter_stats_2['runs']/batter_stats_2['balls']
            for index,row in batter_stats_2.iterrows():
                batter = row['striker']
                if batter in df_mod_2.player_dismissed.unique():
                    new_out_value = 1
                    batter_stats_2.at[index, 'outs'] = new_out_value

            batter_stats_2['outs'] = batter_stats_2['outs'].replace(0,'N/O')
            batter_stats_2['outs'] = batter_stats_2['outs'].replace(1,'out')

            batter_stats_2 = batter_stats_2.sort_values(['runs','strike_rate'], ascending=[False,False]).reset_index(drop=True)

            batter_stats_2 = batter_stats_2.round(2)
            bowler_stats = bowler_stats.round(2)


            winner = str(team1)+' wins!!' if total_1>total_2 else str(team2)+ ' wins!!' if total_1<total_2\
                                                    else "it's a TIE!!!!"
            
            
            
            batter_stats_2['points'] = 0
            bowler_stats['points'] = 0
            
            for index, row in batter_stats_2.iterrows():
                #batting
                run_pt = row['runs']*1
                bdry_pt = row['fours']*1+row['sixes']*2
                dot_pt = row['dots']*(-0.25)

                sr_pt = 6 if row['strike_rate']>=170 else 4 if row['strike_rate']>150 else 2 if row['strike_rate']>130 else \
                        0 if row['strike_rate']>70 else -2 if row['strike_rate']>=60 else -4 if row['strike_rate']>=50 else -6

                milestone_pt = 16 if row['runs']>=100 else 8 if row['runs']>=50 else 4 if row['runs']>=30 else 0

                total_pt = run_pt+bdry_pt+dot_pt+sr_pt+milestone_pt
                
                batter_stats_2.at[index, 'points'] = total_pt
                
            for index, row in bowler_stats.iterrows():
                #bowling
                wkt_pt = row['wkts']*25
                wkt_bonus_pt = (16 if row['wkts']>=5 else 8 if row['wkts']>=4 else 4 if row['wkts']>=3 else 0)
                dot_pt = row['dots']*0.25

                eco_pt = -6 if row['economy']>12 else -4 if row['economy']>11 else -2 if row['economy']>=10 else \
                          0 if row['economy']>7 else 2 if row['economy']>=6 else 4 if row['economy']>=5 else 6 

                total_pt = wkt_pt+wkt_bonus_pt+dot_pt+eco_pt
                
                bowler_stats.at[index, 'points'] = total_pt

            
            ######## points dictionary
            bat_pt = batter_stats_2[['striker','points']].rename(columns={'striker':'player','points':'points2'})
            bowl_pt = bowler_stats[['bowler','points']].rename(columns={'bowler':'player','points':'points2'})
            pt2 = pd.concat([bat_pt,bowl_pt],axis=0)
            
            
            pts = pt1.merge(pt2, on='player', how='outer')
            pts.fillna(0, inplace=True)
            pts['points'] = pts['points1']+pts['points2']
            pts.sort_values(by='points', ascending=False, inplace=True)
            
            top_point = pts.head(1).player.unique()[0]
            

            print("---" * 10)
            print("  "*5)
            
            print("---" * 10)
            print("  "*5)
            print("innings 2")
            print("```second inning begins```")
            
            print(f"{team1} BOWLING ---")
            print("^^"*10)
            #print(bowler_stats)
            print("---" * 10)
            print("  "*5)
            
            ###############
            
            separator = "---" * 10  # Separator line

            # Print column names
            print(separator)
            line = " | ".join(bowler_stats.drop('bowling_team', axis=1).columns)
            print('```', line, '```')
            print(separator)
            
            # Print rows one by one
            for _, row in bowler_stats.drop('bowling_team', axis=1).iterrows():
                line = " | ".join(map(str, row.values))  # Convert values to strings and join with "|"
                print('```', line, '```')
                print(separator)  # Add separator after each row

            print("  "*5)
            print(f"Extras = {extra_2}")
            ###############
            
            ######################################
            
            batter_stats_mod_2 = pd.DataFrame()

            for player in bat_2nd_team:
                if player in batter_stats_2['striker'].values:
                    out_info = out_df[out_df['player_dismissed'] == player]
                    bat_info = batter_stats_2[batter_stats_2['striker'] == player]

                    # Handle empty DataFrames to avoid KeyError
                    wkt_type = out_info['wicket_event'].iloc[0] if not out_info.empty else None
                    wkt_type_ = out_info['wicket_type'].iloc[0] if not out_info.empty else None
                    fielder = out_info['fielder'].iloc[0] if not out_info.empty else None
                    bowler = out_info['bowler'].iloc[0] if not out_info.empty else None
                    runs = bat_info['runs'].iloc[0] if not bat_info.empty else 0
                    balls = bat_info['balls'].iloc[0] if not bat_info.empty else 0
                    sr = bat_info['strike_rate'].iloc[0] if not bat_info.empty else 0

                    row = {'player': player, 'wkt_type': wkt_type, 'wkt_type_': wkt_type_, 'fielder': fielder,
                           'bowler': bowler, 'runs': int(runs), 'balls': int(balls), 'strike_rate': sr}

                    # Append to DataFrame instead of just printing
                    batter_stats_mod_2 = batter_stats_mod_2.append(row, ignore_index=True)

            batter_stats_mod_2['wicket_event'] = ''

            for idx,row in batter_stats_mod_2.iterrows():
                wkt = row['wkt_type']
                wkt_ = row['wkt_type_']
                fielder = row['fielder']
                bowler = row['bowler']

                event = 'Not Out'
                if wkt=='Bowled':
                    event = f"Bo {bowler}"
                elif (wkt=='LBW'):
                    event = f"LBW {bowler}"
                elif wkt=='Caught':
                    event = f"C {fielder} B {bowler}"
                elif wkt=='HitWicket':
                    event = "Hit-Wicket"
                elif wkt=='Stumped/Runout by Keeper':
                    event = f"Stumped/Runout by {fielder}"

                if wkt_=='runout':
                    event = f"Run-out by {fielder}"

                batter_stats_mod_2.loc[idx, 'wicket_event'] = event

            batter_stats_mod_2[['runs','balls']] = batter_stats_mod_2[['runs','balls']].astype(int)

            
            
            ######################################
            
            print("---" * 10)
            print("  "*5)
            
            print("--"*5)
            print(f"{team2} BATTING --")
            print("^^"*10)
            #print(batter_stats.drop(['fours','sixes','dots'], axis=1))
            print("---" * 10)
            print("  "*5)
            
            ###############
            batter_stats_mod_2 = batter_stats_mod_2[['player','wicket_event','runs','balls','strike_rate']]
            
            separator = "---" * 10  # Separator line

            # Print column names
            print(separator)
            line = " | ".join(batter_stats_mod_2.columns)
            print('```', line, '```')
            print(separator)
            
            # Print rows one by one
            for _, row in batter_stats_mod_2.iterrows():
                line = " | ".join(map(str, row.values))  # Convert values to strings and join with "|"
                print('```', line, '```')
                print(separator)  # Add separator after each row

            
            ###############
            print("---" * 10)
            print("  "*5)
            
            print("  "*5)
            print("<.>."*5)
            print("  "*5)
            print(f"Score :: {total_2}-{wickets_2}  ({overs_2}), run-rate = {np.round(6*total_2/balls_2, 2)}")
            print("***"*10)
            print("***"*10)
            
            print("---" * 10)
            print("  "*5)
            
            print("```match ends```")
            print("<.>."*5)
            print(f"{winner}")
            print("***"*10)
            print("  "*5)
            print("  "*5)
            print(f"The Player of the Match is ~~ {top_point}")
        
    print(f"All output has been saved to {output_file}")
