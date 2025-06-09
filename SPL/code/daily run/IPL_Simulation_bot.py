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
import pandas as pd
import numpy as np

##########################################################################################################
# Replace 'YOUR_DISCORD_TOKEN' with your bot's token
TOKEN = 'MTMxMjY3MzIxODk0NzE5MDgwNA.G93vLi.jIhobnXnvrBwyg8mwShmV6VWxI4xlyNcv2z9oE'

intents = discord.Intents.default()
intents.message_content = True  # Ensure this intent is enabled
client = discord.Client(intents=intents)

def team_map(value):
    if value=='CSK':
        return team_CSK
    elif value=='DC':
        return team_DC
    elif value=='GT':
        return team_GT
    elif value=='KKR':
        return team_KKR
    elif value=='LSG':
        return team_LSG
    elif value=='MI':
        return team_MI
    elif value=='PBKS':
        return team_PBKS
    elif value=='RCB':
        return team_RCB
    elif value=='RR':
        return team_RR
    elif value=='SRH':
        return team_SRH
    ##
    elif value=='S01XI':
        return team_S01
    elif value=='S02XI':
        return team_S02
    ##
    else:
        return pd.DataFrame()
    

team_CSK = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03.xlsx', 
                        sheet_name='CSK')
team_CSK = team_CSK.sort_values(by='XI').head(11)

team_DC = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03.xlsx', 
                        sheet_name='DC')
team_DC = team_DC.sort_values(by='XI').head(11)

team_GT = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03.xlsx', 
                        sheet_name='GT')
team_GT = team_GT.sort_values(by='XI').head(11)

team_KKR = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03.xlsx', 
                        sheet_name='KKR')
team_KKR = team_KKR.sort_values(by='XI').head(11)

team_LSG = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03.xlsx', 
                        sheet_name='LSG')
team_LSG = team_LSG.sort_values(by='XI').head(11)

team_MI = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03.xlsx', 
                        sheet_name='MI')
team_MI = team_MI.sort_values(by='XI').head(11)

team_PBKS = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03.xlsx', 
                        sheet_name='PBKS')
team_PBKS = team_PBKS.sort_values(by='XI').head(11)

team_RCB = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03.xlsx', 
                        sheet_name='RCB')
team_RCB = team_RCB.sort_values(by='XI').head(11)

team_RR = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03.xlsx', 
                        sheet_name='RR')
team_RR = team_RR.sort_values(by='XI').head(11)

team_SRH = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03.xlsx', 
                        sheet_name='SRH')
team_SRH = team_SRH.sort_values(by='XI').head(11)


#####
team_S01 = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03.xlsx', 
                        sheet_name='S01XI')
team_S01 = team_S01.sort_values(by='XI').head(11)

team_S02 = pd.read_excel('/Users/roumyadas/Desktop/IPL_Simulation/Teams/SQUADS_season_03.xlsx', 
                        sheet_name='S02XI')
team_S02 = team_S02.sort_values(by='XI').head(11)


import random

def simulate_injury_event(home_team, away_team):
    # Step a: Determine if injury occurs (3% probability)
    injury_occurs = random.random() < 0.03
    if not injury_occurs:
        return None  # No injury happened
    
    # Step b: Determine number of injuries
    num_injuries = random.choices([1, 2], weights=[0.9, 0.1])[0]

    if num_injuries == 1:
        # Step c: Select a team (equal probability)
        selected_team = random.choice(["home", "away"])
        selected_player = random.choice(home_team if selected_team == "home" else away_team)
        return [(selected_team, selected_player)]

    else:  # num_injuries == 2
        # Step d.i: Decide injury distribution (hh, ha, aa)
        injury_type = random.choices(["hh", "ha", "aa"], weights=[0.2, 0.6, 0.2])[0]
        
        if injury_type == "hh":  # Both from home
            injured_players = random.sample(home_team, 2)
            return [("home", injured_players[0]), ("home", injured_players[1])]
        
        elif injury_type == "ha":  # One from each team
            injured_home = random.choice(home_team)
            injured_away = random.choice(away_team)
            return [("home", injured_home), ("away", injured_away)]
        
        else:  # "aa", both from away
            injured_players = random.sample(away_team, 2)
            return [("away", injured_players[0]), ("away", injured_players[1])]


# Function to split text into chunks wrt '---'*10
def split_text_into_chunks(text, max_length=1000):
    formatted_text = f"{text}"  # Formatting the text
    chunks = formatted_text.split('---' * 10)  # Splitting at '----------'
    return [chunk.strip() for chunk in chunks if chunk.strip()]

home = 'S01XI'
away = 'S02XI'
venue = 'PBKS'
#venue = 

venue_path = "/Users/roumyadas/Desktop/IPL_Simulation/Season_03/Stats/venue_stats.xlsx"
home_pl = team_map(home)['Func_Name'].values.tolist()
away_pl = team_map(away)['Func_Name'].values.tolist()
#toss_W = random.sample((home,away),1)[0]
####################################################
h2h_stats_file = '/Users/roumyadas/Desktop/Data/t20_cricket_data/Data/created_data/data to send/h2h_stats.xlsx'
h2h_stats_ = pd.read_excel(h2h_stats_file)
venue_stats_pitch = pd.read_excel(venue_path, sheet_name='pitch_wise')
venue_stats_overall = pd.read_excel(venue_path, sheet_name='overall')

bat_h2h_ha = h2h_stats_[(h2h_stats_['bat_team']==home)&(h2h_stats_['bowl_team']==away)].sort_values('h2h_factor_bat',ascending=False)[['striker','bowler','runs_scored','balls_bowled','outs']].head(2).reset_index(drop=True)
bat_h2h_ah = h2h_stats_[(h2h_stats_['bat_team']==away)&(h2h_stats_['bowl_team']==home)].sort_values('h2h_factor_bat',ascending=False)[['striker','bowler','runs_scored','balls_bowled','outs']].head(2).reset_index(drop=True)
bowl_h2h_ha = h2h_stats_[(h2h_stats_['bowl_team']==home)&(h2h_stats_['bat_team']==away)].sort_values('h2h_factor_bowl',ascending=False)[['striker','bowler','runs_scored','balls_bowled','outs']].head(2).reset_index(drop=True)
bowl_h2h_ah = h2h_stats_[(h2h_stats_['bowl_team']==away)&(h2h_stats_['bat_team']==home)].sort_values('h2h_factor_bowl',ascending=False)[['striker','bowler','runs_scored','balls_bowled','outs']].head(2).reset_index(drop=True)

####
spin_score = venue_stats_pitch[(venue_stats_pitch.venue==venue)&(venue_stats_pitch.pitch=='spin')]['score'].unique()[0]
pace_score = venue_stats_pitch[(venue_stats_pitch.venue==venue)&(venue_stats_pitch.pitch=='pace')]['score'].unique()[0]
neu_score = venue_stats_pitch[(venue_stats_pitch.venue==venue)&(venue_stats_pitch.pitch=='neutralish')]['score'].unique()[0]

bat1_win = venue_stats_overall[(venue_stats_overall.venue==venue)]['win%'].unique()[0]
bat1_win = np.round(bat1_win,2)
####

if bat_h2h_ha.shape[0]>0:
    if bat_h2h_ha.shape[0]>1:
        bat_h2h_ha_text = f"top two h2h (bat): \n [{home} v {away}] \n 1. {bat_h2h_ha['striker'].iloc[0]} v {bat_h2h_ha['bowler'].iloc[0]} -- {bat_h2h_ha['runs_scored'].iloc[0]} off {bat_h2h_ha['balls_bowled'].iloc[0]}, {bat_h2h_ha['outs'].iloc[0]} outs. \n 2. {bat_h2h_ha['striker'].iloc[1]} v {bat_h2h_ha['bowler'].iloc[1]} -- {bat_h2h_ha['runs_scored'].iloc[1]} off {bat_h2h_ha['balls_bowled'].iloc[1]}, {bat_h2h_ha['outs'].iloc[1]} outs."
    else:
        bat_h2h_ha_text = f"top h2h (bat): \n [{home} v {away}] \n {bat_h2h_ha['striker'].iloc[0]} v {bat_h2h_ha['bowler'].iloc[0]} -- {bat_h2h_ha['runs_scored'].iloc[0]} off {bat_h2h_ha['balls_bowled'].iloc[0]}, {bat_h2h_ha['outs'].iloc[0]} outs."
else :
    bat_h2h_ha_text = f"NO h2h found!"

if bat_h2h_ah.shape[0]>0:
    if bat_h2h_ah.shape[0]>1:
        bat_h2h_ah_text = f"top two h2h (bat): \n [{away} v {home}] \n 1. {bat_h2h_ah['striker'].iloc[0]} v {bat_h2h_ah['bowler'].iloc[0]} -- {bat_h2h_ah['runs_scored'].iloc[0]} off {bat_h2h_ah['balls_bowled'].iloc[0]}, {bat_h2h_ah['outs'].iloc[0]} outs. \n 2. {bat_h2h_ah['striker'].iloc[1]} v {bat_h2h_ah['bowler'].iloc[1]} -- {bat_h2h_ah['runs_scored'].iloc[1]} off {bat_h2h_ah['balls_bowled'].iloc[1]}, {bat_h2h_ah['outs'].iloc[1]} outs."
    else:
        bat_h2h_ah_text = f"top h2h (bat): \n [{away} v {home}] \n {bat_h2h_ah['striker'].iloc[0]} v {bat_h2h_ah['bowler'].iloc[0]} -- {bat_h2h_ah['runs_scored'].iloc[0]} off {bat_h2h_ah['balls_bowled'].iloc[0]}, {bat_h2h_ah['outs'].iloc[0]} outs."
else :
    bat_h2h_ah_text = f"NO h2h found!"

if bowl_h2h_ha.shape[0]>0:
    if bowl_h2h_ha.shape[0]>1:
        bowl_h2h_ha_text = f"top two h2h (bowl): \n [{home} v {away}] \n 1. {bowl_h2h_ha['striker'].iloc[0]} v {bowl_h2h_ha['bowler'].iloc[0]} -- {bowl_h2h_ha['runs_scored'].iloc[0]} off {bowl_h2h_ha['balls_bowled'].iloc[0]}, {bowl_h2h_ha['outs'].iloc[0]} outs. \n 2. {bowl_h2h_ha['striker'].iloc[1]} v {bowl_h2h_ha['bowler'].iloc[1]} -- {bowl_h2h_ha['runs_scored'].iloc[1]} off {bowl_h2h_ha['balls_bowled'].iloc[1]}, {bowl_h2h_ha['outs'].iloc[1]} outs."
    else:
        bowl_h2h_ha_text = f"top h2h (bowl): \n [{home} v {away}] \n {bowl_h2h_ha['striker'].iloc[0]} v {bowl_h2h_ha['bowler'].iloc[0]} -- {bowl_h2h_ha['runs_scored'].iloc[0]} off {bowl_h2h_ha['balls_bowled'].iloc[0]}, {bowl_h2h_ha['outs'].iloc[0]} outs."
else :
    bowl_h2h_ha_text = f"NO h2h found!"

if bowl_h2h_ah.shape[0]>0:
    if bowl_h2h_ah.shape[0]>1:
        bowl_h2h_ah_text = f"top two h2h (bowl): \n [{away} v {home}] \n 1. {bowl_h2h_ah['striker'].iloc[0]} v {bowl_h2h_ah['bowler'].iloc[0]} -- {bowl_h2h_ah['runs_scored'].iloc[0]} off {bowl_h2h_ah['balls_bowled'].iloc[0]}, {bowl_h2h_ah['outs'].iloc[0]} outs. \n 2. {bowl_h2h_ah['striker'].iloc[1]} v {bowl_h2h_ah['bowler'].iloc[1]} -- {bowl_h2h_ah['runs_scored'].iloc[1]} off {bowl_h2h_ah['balls_bowled'].iloc[1]}, {bowl_h2h_ah['outs'].iloc[1]} outs."
    else:
        bowl_h2h_ah_text = f"top h2h (bowl): \n [{away} v {home}] \n {bowl_h2h_ah['striker'].iloc[0]} v {bowl_h2h_ah['bowler'].iloc[0]} -- {bowl_h2h_ah['runs_scored'].iloc[0]} off {bowl_h2h_ah['balls_bowled'].iloc[0]}, {bowl_h2h_ah['outs'].iloc[0]} outs."
else :
    bowl_h2h_ah_text = f"NO h2h found!"


#bat_h2h_ah_text = f"top two h2h (bat): \n {bat_h2h_ah['striker']} v {bat_h2h_ah['bowler']} -- {bat_h2h_ha['runs_scored']} off {bat_h2h_ha['balls_bowled']}, {bat_h2h_ha['outs']} outs."
#bowl_h2h_ha_text = f"top two h2h (bat): \n {bat_h2h_ha['striker']} v {bat_h2h_ha['bowler']} -- {bat_h2h_ha['runs_scored']} off {bat_h2h_ha['balls_bowled']}, {bat_h2h_ha['outs']} outs."
#bowl_h2h_ah_text = f"top two h2h (bat): \n {bat_h2h_ha['striker']} v {bat_h2h_ha['bowler']} -- {bat_h2h_ha['runs_scored']} off {bat_h2h_ha['balls_bowled']}, {bat_h2h_ha['outs']} outs."

match = '01'
m = 'S03M0'+match

bBb_file = f'/Users/roumyadas/Desktop/IPL_Simulation/Season_03/Match_flows/ball-by-ball_{int(match)}.txt'
bBb = pd.read_fwf(bBb_file)
m_card_file = f'/Users/roumyadas/Desktop/IPL_Simulation/Season_03/Scorecards/matchcard_{m}.txt'
m_card = pd.read_fwf(m_card_file)
rating_file = f'/Users/roumyadas/Desktop/IPL_Simulation/Season_03/Match_Rating/Match_{match}.txt'
#rating = pd.read_fwf(rating_file)
run_chart_pic = f"/Users/roumyadas/Desktop/IPL_Simulation/Season_03/plots/run_charts/{m}.jpg"
score_worm = f"/Users/roumyadas/Desktop/IPL_Simulation/Season_03/plots/score_worms/{m}.jpg"
runrate = f"/Users/roumyadas/Desktop/IPL_Simulation/Season_03/plots/run_rate/{m}.jpg"
p_ship = f"/Users/roumyadas/Desktop/IPL_Simulation/Season_03/plots/partnership/{m}.jpg"
awards = f"/Users/roumyadas/Desktop/IPL_Simulation/Season_03/awards/awards_{m}.txt"
impact = f"/Users/roumyadas/Desktop/IPL_Simulation/Season_03/total_impact/{m}_impact.txt"

#--------UNCHANGED BELOW---------
#pts_table = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/Season_03/Stats/points_table.csv')
#bat_stat = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/batter_stats_30.csv')
#bowl_stat = pd.read_csv('/Users/roumyadas/Desktop/IPL_Simulation/bowler_stats_30.csv')
wait_text = "```... a slight wait, 'cuz they deserve it ...```"

####################################################
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    # Log received messages to check if bot receives them
    print(f"Received message: {message.content}")

    if message.author == client.user:
        return "-------------"
    
    if message.content.startswith('!toss'):
        await message.channel.send(random.sample((home,away,home,away,home,away),1)[0])

    if message.content.startswith('!XI'):
        await message.channel.send(f"(Home) {home} XI : \n {home_pl} \n\n\n (Away) {away} XI : \n {away_pl}")

    if message.content.startswith('!injury'):
        #await message.channel.send(simulate_injury_event(home_pl, away_pl))
        await message.channel.send("**NO injuries occurred**" if random.random() >= 0.075 else
            [(random.choice(["Player - ", "Player - "]), 
              random.choice(home_pl if random.random() < 0.5 else away_pl), 
              random.choices(["1 game", "2 games", '5 games'], weights=[0.725, 0.225, 0.05])[0])] 
            if random.choices([1, 2], weights=[0.9, 0.1])[0] == 1 else 
            (lambda it: 
                [(t, p, random.choices(["1 game", "2 games", "5 games"], weights=[0.725, 0.225, 0.05])[0]) for t, p in 
                 (zip(["Home Team - "]*2, random.sample(home_pl, 2)) if it == "hh" else
                  zip(["Away Team - "]*2, random.sample(away_pl, 2)) if it == "aa" else
                  zip(["Home Team - ", "Away Team - "], [random.choice(home_pl), random.choice(away_pl)]))]
            )(random.choices(["hh", "ha", "aa"], weights=[0.2, 0.6, 0.2])[0])
           )

    if message.content.startswith('!sim_ping'):
        await message.channel.send('Pong!')

    if message.content.startswith('!basics'):
        await message.channel.send(f"Venue: {venue} \n \n Bat 1st avg score :: \n \n Spin pitch: {spin_score} \n Pace pitch: {pace_score} \n Neutral pitch: {neu_score}")
        await message.channel.send("----------------------------------------------------")
        await message.channel.send(f"Bat 1st win percentage: {bat1_win}")
        await message.channel.send("----------------------------------------------------")
        await message.channel.send(f"{bat_h2h_ha_text} \n \n {bat_h2h_ah_text} \n \n {bowl_h2h_ha_text} \n \n {bowl_h2h_ah_text}")
    

    if message.content.startswith('!plots'):
        try:
            #run_chart
            with open(run_chart_pic, 'rb') as f:
                picture = discord.File(f, filename=f"{m}.jpg") #f"{m}.jpg"
                await message.channel.send(file=picture)

            #score_worm
            with open(score_worm, 'rb') as f:
                picture = discord.File(f, filename=f"{m}.jpg")
                await message.channel.send(file=picture)

            #partnership
            with open(p_ship, 'rb') as f:
                picture = discord.File(f, filename=f"{m}.jpg")
                await message.channel.send(file=picture)

            #run-rate
            with open(runrate, 'rb') as f:
                picture = discord.File(f, filename=f"{m}.jpg")
                await message.channel.send(file=picture)

            
        except FileNotFoundError:
            await message.channel.send('file not found!')

    if message.content.startswith('!run_match'):
        await message.channel.send("~~~")
        try:
            #await message.channel.send(bBb)
            # Read the text file
            with open(bBb_file, "r", encoding="utf-8") as file:
                text = file.read()

            # Split into chunks
            chunks = split_text_into_chunks(text)

            # Send each chunk
            for chunk in chunks:
                await message.channel.send(chunk)
                await asyncio.sleep(0.5)
                await message.channel.send(wait_text)
                await asyncio.sleep(0.5)
        
        except Exception as E:
            await message.channel.send(E)

    if message.content.startswith('!card'):
        await message.channel.send("~~~")
        try:
            with open(m_card_file, "r", encoding="utf-8") as file:
                text = file.read()
            # Split into chunks
            chunks = split_text_into_chunks(text)
            # Send each chunk
            for chunk in chunks:
                await message.channel.send(chunk)
        except Exception as E:
            await message.channel.send(E)

    if message.content.startswith('!rating'):
        await message.channel.send("~~~")
        try:
            with open(rating_file, "r", encoding="utf-8") as file:
                text = file.read()
                await message.channel.send(text)
        except Exception as E:
            await message.channel.send(E)

    if message.content.startswith('!award'):
        await message.channel.send("~~~")
        try:
            with open(awards, "r", encoding="utf-8") as file:
                text = file.read()
                await message.channel.send(text)
        except Exception as E:
            await message.channel.send(E)
    
    if message.content.startswith('!impact'):
        await message.channel.send("~~~")
        try:
            with open(impact, "r", encoding="utf-8") as file:
                text = file.read()
                # Split into chunks
                chunks = split_text_into_chunks(text)

                # Send each chunk
                for chunk in chunks:
                    await message.channel.send(chunk)
                #await message.channel.send(text)
        except Exception as E:
            await message.channel.send(E)
    
    if message.content.startswith('!run_chart'):
        try:
            with open(run_chart_pic, 'rb') as f:
                picture = discord.File(f, filename=f"{m}.jpg") #f"{m}.jpg"
                await message.channel.send(file=picture)
        except FileNotFoundError:
            await message.channel.send('file not found!')

    if message.content.startswith('!score_worm'):
        try:
            with open(score_worm, 'rb') as f:
                picture = discord.File(f, filename=f"{m}.jpg")
                await message.channel.send(file=picture)
        except FileNotFoundError:
            await message.channel.send('file not found!')

    if message.content.startswith('!p_ship'):
        try:
            with open(p_ship, 'rb') as f:
                picture = discord.File(f, filename=f"{m}.jpg")
                await message.channel.send(file=picture)
        except FileNotFoundError:
            await message.channel.send('file not found!')

    if message.content.startswith('!runrate'):
        try:
            with open(runrate, 'rb') as f:
                picture = discord.File(f, filename=f"{m}.jpg")
                await message.channel.send(file=picture)
        except FileNotFoundError:
            await message.channel.send('file not found!')

    
    """
    if message.content.startswith('!bat_stat'):
        await message.channel.send("~~~")
        try:
            await message.channel.send(bat_stat)
        except Exception as E:
            await message.channel.send(E)

    if message.content.startswith('!bowl_stat'):
        await message.channel.send("~~~")
        try:
            await message.channel.send(bowl_stat)
        except Exception as E:
            await message.channel.send(E)
    """
    if message.content.startswith('!table'):
        await message.channel.send("~~~")
        try:
            await message.channel.send(pts_table)
        except Exception as E:
            await message.channel.send(E)

   

# Run the bot in the background
if __name__ == "__main__":
    import asyncio
    asyncio.run(client.start(TOKEN))

##################################################################################################
