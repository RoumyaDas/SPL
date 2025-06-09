#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import glob
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import random
from collections import Counter

df_all = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_02/df_all_round_sim.csv')

##reading all STATS from one excel##
excel_filename = "/Users/roumyadas/Desktop/IPL_Simulation/Season_02/STATS_S02.xlsx"

pts_table = pd.read_excel(excel_filename, sheet_name='POINTS_TABLE')

matches_list = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Fixtures/IPL_2024_schedule.xlsx',
                            sheet_name='Season_02')

matches_list = matches_list[['Date','Team One','Team Two']]
mts_done = pts_table['matches_played'].sum()/2
matches_list_mod = matches_list[int(mts_done):]
matches_list_mod['winner'] = ''


# In[2]:


q_master_list = []


# In[3]:


get_ipython().run_cell_magic('time', '', '\n# Vectorized simulation\nfor _ in range(10**4):\n    # Randomly assign winners\n    matches_list_mod["winner"] = np.where(\n        np.random.rand(len(matches_list_mod)) < 0.5, \n        matches_list_mod["Team One"], \n        matches_list_mod["Team Two"]\n    )\n\n    # Count wins and calculate points\n    sim_win = matches_list_mod["winner"].value_counts().reset_index()\n    sim_win.columns = ["team", "wins"]\n    sim_win["pts"] = sim_win["wins"] * 2\n\n    # Merge results with original points table\n    pts_table_mod = pts_table.merge(sim_win, on="team", how="left").fillna(0)\n    pts_table_mod["pts_final"] = pts_table_mod["points"] + pts_table_mod["pts"]\n    pts_table_mod["NRR_final"] = pts_table_mod["NRR"] + np.random.normal(0, 0.1, len(pts_table_mod))\n\n    # Sort by points and NRR\n    pts_table_mod = pts_table_mod.sort_values(by=["pts_final", "NRR_final"], ascending=False)\n\n    # Get top 4 teams\n    q_master_list.append(pts_table_mod["team"].head(4).tolist())\n\nflat_list = [item for sublist in q_master_list for item in sublist]\ncounts = Counter(flat_list)\n\ndf = pd.DataFrame(counts.items(), columns=["String", "Count"])\n\ndf = df.sort_values(by="Count", ascending=False).reset_index(drop=True)\ndf[\'prob_qualification\'] = 100*df[\'Count\']/len(q_master_list)')


# In[8]:


print("Qualification Probabilities ::")
for idx, row in df[['String','prob_qualification']].iterrows():
    print(f"{row['String']} -- {row['prob_qualification']}")


# In[ ]:





# In[ ]:




