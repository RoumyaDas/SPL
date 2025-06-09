import pandas as pd
import glob
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

df_all = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/df_all_round_sim.csv')

df_all['phase'] = np.where(df_all['legal_balls_bowled']<=36, 'pp', 
                        np.where(df_all['legal_balls_bowled']>=90, 'death',
                            'middle'))


## phase wise batting SR, bowling Eco

bat_phase = df_all.groupby(['striker','phase']).agg(
    num_innings = ('match_id','nunique'),
    runs = ('total_runs','sum'),
    balls = ('is_faced_by_batter' ,'sum')
    
).reset_index()

bat_phase['strike_rate'] = 100*bat_phase['runs']/bat_phase['balls']
bat_phase['runs'] = bat_phase['runs'].astype(int)
bat_phase = bat_phase.round(2)



bowl_phase = df_all.groupby(['bowler','phase']).agg(
    num_innings = ('match_id','nunique'),
    runs = ('runs_conceeded','sum'),
    balls = ('islegal' ,'sum')
    
).reset_index()

bowl_phase['economy'] = 6*bowl_phase['runs']/bowl_phase['balls']
bowl_phase['runs'] = bowl_phase['runs'].astype(int)
bowl_phase = bowl_phase.round(2)

## h2h stats

h2h_stats = df_all.groupby(['striker','bowler']).agg(
    
    runs_scored = ('runs_off_bat','sum'),
    #runs_conceeded = ('runs_conceeded','sum'),
     
    balls_faced = ('is_faced_by_batter' ,'sum'),
    #balls_bowled = ('islegal','sum'),
    
    outs = ('isBowlerWicket','sum')
    
).reset_index()


h2h_stats['bat_sr'] = 100*h2h_stats['runs_scored']/h2h_stats['balls_faced']

#h2h_stats



excel_filename = '/Users/roumyadas/Desktop/IPL_Simulation/Season_01/separate_stats.xlsx'

# Use ExcelWriter to write multiple sheets
with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
    bat_phase.to_excel(writer, sheet_name='BAT_phase', index=False)
    bowl_phase.to_excel(writer, sheet_name='BOWL_phase', index=False)
    h2h_stats.to_excel(writer, sheet_name='h2h', index=False)



