file = 'C:/Users/tally/Downloads/IPL-2023-schedule.csv'

# load schedule dataset


import pandas as pd
import ipywidgets as widgets
from IPython.display import display
import datetime
from matplotlib import pyplot as plt

from tkinter import *
from tkinter import ttk
from tkcalendar import Calendar
import pandas as pd

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

from selenium.webdriver.chrome.options import Options

from datetime import datetime
import plotly.graph_objs as go
import numpy as np
# Get today's date

class SOS():

    def process_Schedule(file):
        schedule_df = pd.read_csv(file)
        schedule_df = schedule_df.drop_duplicates()


        schedule_df["Date"] = pd.to_datetime(schedule_df["Date"], format="%d-%m-%y %H:%M")

        # Convert "Date" column back to string format with "d-m-y" format
        schedule_df["Date"] = schedule_df["Date"].dt.strftime("%d-%m-%Y")

        return schedule_df

    def getPointsTable():
        options = Options()
        options.headless = True

        #   create a new Chrome browser instance
        driver = webdriver.Chrome(options=options)
        url = "https://www.iplt20.com/points-table/2023"
        driver.get(url)

        # wait for the dynamic content to load
        driver.implicitly_wait(10)

        # extract the HTML content of the page
        html = driver.page_source

        # create a BeautifulSoup object from the HTML content
        soup = BeautifulSoup(html, 'html.parser')

        # find the table containing the points data
        points_table = soup.find('tbody', {'id': 'pointsdata'})

        # find all rows in the table
        rows = points_table.find_all('tr', {'class': 'ng-scope'})

        data = []

        # extract data from each row
        for row in rows:
            # extract the team name
            team_name = row.find('h2', {'class': 'ih-pt-cont'}).text

            Position = row.find_all('td', {'class': 'ng-binding'})[0].text
            
            # extract the number of matches played
            matches_played = row.find_all('td', {'class': 'ng-binding'})[1].text
            
            # extract the number of points
            Wins = row.find_all('td', {'class': 'ng-binding'})[2].text

            Losses = row.find_all('td', {'class': 'ng-binding'})[3].text

            No_Result = row.find_all('td', {'class': 'ng-binding'})[4].text

            Net_Run_Rate = row.find_all('td', {'class': 'ng-binding'})[5].text

            For = row.find_all('td', {'class': 'ng-binding'})[6].text

            Against = row.find_all('td', {'class': 'ng-binding'})[7].text

            Points = row.find_all('td', {'class': 'ng-binding'})[8].text

            data.append([team_name, matches_played, Wins, Losses, No_Result, Net_Run_Rate, For, Against, Points])

        # create a DataFrame from the extracted data and set the column names
        df = pd.DataFrame(data, columns=['Team', 'Matches Played', 'Wins', 'Losses', 'No Result', 'Net Run Rate', 'For', 'Against', 'Points'])

        df['Matches Played'] = df['Matches Played'].astype(int)
        df['Wins'] = df['Wins'].astype(int)
        df['Losses'] = df['Losses'].astype(int)
        df['No Result'] = df['No Result'].astype(int)
        df['Net Run Rate'] = df['Net Run Rate'].astype(float)
        df['Points'] = df['Points'].astype(int)

        team_name_map = {
        'GT': 'Gujarat Titans',
        'LSG': 'Lucknow Super Giants',
        'CSK': 'Chennai Super Kings',
        'RR': 'Rajasthan Royals',
        'RCB': 'Royal Challengers Bangalore',
        'MI': 'Mumbai Indians',
        'PBKS': 'Punjab Kings',
        'KKR': 'Kolkata Knight Riders',
        'SRH': 'Sunrisers Hyderabad',
        'DC': 'Delhi Capitals'
    }

    # Replace team names in points_table
        df['Team'] = df['Team'].map(team_name_map)


        return df

    def calculate_sos(ipl_points_table, team_name, num_matches=2):
        # Get the current position of the team
        team_pos = ipl_points_table[ipl_points_table['Team'] == team_name].index.values[0]
        
        # Select the upcoming matches for the team
        team_matches = ipl_points_table.iloc[team_pos]['Matches']
        upcoming_matches = ipl_points_table.iloc[team_pos:team_pos+team_matches+num_matches]['Team']
        
        # Calculate the strength of schedule
        sos = 0
        for i, opp_name in enumerate(upcoming_matches):
            opp_pos = ipl_points_table[ipl_points_table['Team'] == opp_name].index.values[0]
            opp_points = int(ipl_points_table.iloc[opp_pos]['Points'])
            sos += (i+1) * opp_points
        
        # Return the strength of schedule
        return sos



    def SOS_processing(points_df,schedule_df):

        def calculate_sos_NRR(points_table, upcoming_matches):
            sos = {}
            
            # Calculate SOS using past matches
            for team1 in points_table['Team']:
                opp_win_pct = 0
                for index, row in points_table.iterrows():
                    if row['Team'] != team1:
                        opp_win_pct += (row['Points'] / (2 * (row['Matches Played'])))
                sos[team1] = opp_win_pct / len(points_table.index)
                sos[team1] += points_table.loc[points_table['Team'] == team1]['Net Run Rate'].values[0]
            
            # Calculate SOS using upcoming matches
            for index, row in upcoming_matches.iterrows():
                home_team = row['Home Team']
                away_team = row['Away Team']
                home_team_sos = sos[home_team]
                away_team_sos = sos[away_team]
                
                # Update SOS based on upcoming match
                sos[home_team] = ((len(points_table.index) + 1) * home_team_sos - away_team_sos) / len(points_table.index)
                sos[away_team] = ((len(points_table.index) + 1) * away_team_sos - home_team_sos) / len(points_table.index)
            
            return sos
        today = datetime.today().strftime('%d-%m-%Y')
        today_datetime = datetime.strptime(today, '%d-%m-%Y')

        schedule_df['Date'] = pd.to_datetime(schedule_df['Date'], format='%d-%m-%Y')

        upcoming_matches_df = schedule_df[schedule_df['Date'] < today_datetime]

        sos_dict = calculate_sos_NRR(points_df,upcoming_matches_df)

        sos_df = pd.DataFrame.from_dict(sos_dict, orient='index', columns=['Strength Of Schedule'])
        sos_df.index.name = 'Team'
        sos_df = sos_df.reset_index().rename(columns={'index': 'Team'})

        return sos_df,sos_dict


class PlayerAnalysis():

    def PreProcessing():

        df2022 = pd.read_csv('C:/Users/tally/Desktop/Sports Analytics/IPL_Ball_by_Ball_2008_2022.csv')

        column_mapping = {
        'ID': 'id',
        'innings': 'inning',
        'overs': 'over',
        'ballnumber': 'ball',
        'batter': 'batsman',
        'bowler': 'bowler',
        'non-striker': 'non_striker',
        'extra_type': 'extras_type',
        'batsman_run': 'batsman_runs',
        'extras_run': 'extra_runs',
        'total_run': 'total_runs',
        'non_boundary': 'non_boundary',
        'isWicketDelivery': 'is_wicket',
        'player_out': 'player_dismissed',
        'kind': 'dismissal_kind',
        'fielders_involved': 'fielder',
        'BattingTeam': 'batting_team',
        'bowling_team': 'bowling_team'
    }

        # Use the rename method to rename the columns in df2 based on the mapping dictionary
        df2022 = df2022.rename(columns=column_mapping)

        df_18 = df2022[df2022['id'] >981019]

        return df_18


    def Batting_Targets(df_18):
        BallFaced_counts = df_18['batsman'].value_counts()

        BallFaced_counts = pd.DataFrame(BallFaced_counts)

        BallFaced_counts.reset_index( inplace=True)

        MedianBats = BallFaced_counts['batsman'].median()

        Batting_Targets = BallFaced_counts[BallFaced_counts['batsman']>MedianBats]

        Batting_Targets.set_index('index', inplace=True)

        batting_targets_array = np.array(Batting_Targets.index)

        batting_targets_df = pd.DataFrame({'Name': batting_targets_array})

        return batting_targets_df


    def Batsman_Analysis(Batter,df_18):

        colors = ['turquoise', 'crimson']
        
        filt=(df_18['batsman']==Batter)
        df_bat=df_18[filt]

        def count_run(df,runs):
            return len(df[df['batsman_runs']==runs])*runs
        
        def striker_segment_count(df):
            # create an empty dictionary to store the counts
            counts = {}

            # get a list of unique players
            players = df['batsman'].unique()
            
            # loop through the list of players
            for player in players:
                # filter the DataFrame for the current player
                df_player = df[df['batsman'] == player]
                
                # initialize an empty dictionary to store the counts for each segment
                segment_counts = {'pp': 0, 'mid': 0, 'drink': 0, 'end': 0}
                
                # count the instances of the player playing as striker in the Powerplay segment
                segment_counts['pp'] = len(df_player[(df_player['over'] <= 6)])
                
                # count the instances of the player playing as striker in the Mid segment
                segment_counts['mid'] = len(df_player[(df_player['over'] > 6) & (df_player['over'] <= 11)])
                
                # count the instances of the player playing as striker in the Drink segment
                segment_counts['drink'] = len(df_player[(df_player['over'] > 11) & (df_player['over'] <= 16)])
                
                # count the instances of the player playing as striker in the End segment
                segment_counts['end'] = len(df_player[df_player['over'] > 16])
                
                # add the player and their counts to the dictionary
                counts[player] = segment_counts
            
            return counts


        runs_total = df_bat['total_runs'].sum()
        balls_total = len(df_bat['batsman_runs'])

        df_bat_pp = df_bat[df_bat['over'] <= 6]
        df_bat_mid = df_bat[(df_bat['over'] > 6) & (df_bat['over'] <= 11)]
        df_bat_drink = df_bat[(df_bat['over'] > 11) & (df_bat['over'] <= 16)]
        df_bat_end = df_bat[df_bat['over'] > 16]

        runs_pp = df_bat_pp['total_runs'].sum()
        runs_mid = df_bat_mid['total_runs'].sum()
        runs_drink = df_bat_drink['total_runs'].sum()
        runs_end = df_bat_end['total_runs'].sum()

        balls_pp = len(df_bat_pp['batsman_runs'])
        balls_mid = len(df_bat_mid['batsman_runs'])
        balls_drink = len(df_bat_drink['batsman_runs'])
        balls_end = len(df_bat_end['batsman_runs'])

        
     

    

# assume you have defined the functions count_run() and df_bat

        # Calculate the values
        dot_balls = len(df_bat[df_bat['batsman_runs']==0])
        ones = count_run(df_bat, 1)
        twos = count_run(df_bat, 2)
        threes = count_run(df_bat, 3)
        fours = count_run(df_bat, 4)
        sixes = count_run(df_bat, 6)

        runs_per_ball = round((runs_total/balls_total),2)
        runs_per_ball_pp = round((runs_pp/balls_pp),2)
        runs_per_ball_mid = round((runs_mid/balls_mid),2)
        runs_per_ball_drink = round((runs_drink/balls_drink),2)
        runs_per_ball_end = round((runs_end/balls_end),2)


        def count_batting_segments(df_bat):
            # segment the batting innings by overs
            df_bat_pp = df_bat[df_bat['over'] <= 6]
            df_bat_mid = df_bat[(df_bat['over'] > 6) & (df_bat['over'] <= 11)]
            df_bat_drink = df_bat[(df_bat['over'] > 11) & (df_bat['over'] <= 16)]
            df_bat_end = df_bat[df_bat['over'] > 16]

            # create a dictionary of the counts for each segment
            counts = {
                'dot_balls_pp': len(df_bat_pp[df_bat_pp['batsman_runs']==0]),
                'ones_pp': count_run(df_bat_pp, 1),
                'twos_pp': count_run(df_bat_pp, 2),
                'threes_pp': count_run(df_bat_pp, 3),
                'fours_pp': count_run(df_bat_pp, 4),
                'sixes_pp': count_run(df_bat_pp, 6),

                'dot_balls_mid': len(df_bat_mid[df_bat_mid['batsman_runs']==0]),
                'ones_mid': count_run(df_bat_mid, 1),
                'twos_mid': count_run(df_bat_mid, 2),
                'threes_mid': count_run(df_bat_mid, 3),
                'fours_mid': count_run(df_bat_mid, 4),
                'sixes_mid': count_run(df_bat_mid, 6),

                'dot_balls_drink': len(df_bat_drink[df_bat_drink['batsman_runs']==0]),
                'ones_drink': count_run(df_bat_drink, 1),
                'twos_drink': count_run(df_bat_drink, 2),
                'threes_drink': count_run(df_bat_drink, 3),
                'fours_drink': count_run(df_bat_drink, 4),
                'sixes_drink': count_run(df_bat_drink, 6),
                'dot_balls_end': len(df_bat_end[df_bat_end['batsman_runs']==0]),
                'ones_end': count_run(df_bat_end, 1),
                'twos_end': count_run(df_bat_end, 2),
                'threes_end': count_run(df_bat_end, 3),
                'fours_end': count_run(df_bat_end, 4),
                'sixes_end': count_run(df_bat_end, 6),
                }
            
            return counts

        

        counts = count_batting_segments(df_bat)

        # Create a dictionary of the values
        data = {'Metric': ['Dot Balls', '1s', '2s', '3s', '4s', '6s', 'Runs per Ball','Runs Total','Balls Faced Total'],
                'Runs Value': [dot_balls, ones, twos, threes, fours, sixes, runs_per_ball, runs_total, balls_total],
                'Powerplay': [counts['dot_balls_pp'], counts['ones_pp'], counts['twos_pp'], counts['threes_pp'], counts['fours_pp'], counts['sixes_pp'],runs_per_ball_pp,runs_pp,balls_pp], 

                'Middle Overs (6-11)': [counts['dot_balls_mid'], counts['ones_mid'], counts['twos_mid'], counts['threes_mid'], counts['fours_mid'], counts['sixes_mid'],runs_per_ball_mid,runs_mid,balls_mid],

                'Drinks Break (11-16)': [counts['dot_balls_drink'], counts['ones_drink'], counts['twos_drink'], counts['threes_drink'], counts['fours_drink'], counts['sixes_drink'],runs_per_ball_drink,runs_drink,balls_drink],

                'Death Overs': [counts['dot_balls_end'], counts['ones_end'], counts['twos_end'], counts['threes_end'], counts['fours_end'], counts['sixes_end'], runs_per_ball_end ,runs_end,balls_end],


                

                }

        # Convert the dictionary to a dataframe
        df = pd.DataFrame.from_dict(data)



        values = df_bat['dismissal_kind'].value_counts()
        labels=df_bat['dismissal_kind'].value_counts().index
        fig2 = go.Figure(data=[go.Pie(labels=labels,values=values,hole=.3)])
        fig2.update_traces(hoverinfo='label+percent', textinfo='label', textfont_size=20,
                        marker=dict(colors=colors, line=dict(color='#000000', width=3)))
        fig2.update_layout(title="Dismissal Type",
                        titlefont={'size': 30},
                        )
       


        play_count = striker_segment_count(df_bat)
        label2 = list(play_count.keys())
        pp = []
        mid = []
        drink = []
        end = []
        for player in play_count:
            pp.append(play_count[player]['pp'])
            mid.append(play_count[player]['mid'])
            drink.append(play_count[player]['drink'])
            end.append(play_count[player]['end'])
        
        width = 0.35
        fig, ax = plt.subplots(figsize=(10,5))
        ax.bar(label2, pp, width, label='Powerplay')
        ax.bar(label2, mid, width, label='Middle')
        ax.bar(label2, drink, width, label='Drinks')
        ax.bar(label2, end, width, label='End')

        ax.set_ylabel('Balls Faced by Batting Segment')
        ax.set_xlabel('Batsman')
        ax.set_title('Batting Segment by Batsman')
        ax.legend()

        return df,fig,fig2
  