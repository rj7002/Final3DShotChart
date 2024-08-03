
#made by Ryan Joseph
from datetime import date
from datetime import datetime
import requests
import streamlit as st
import plotly.express as px
import pandas as pd
from courtCoordinates import CourtCoordinates
from basketballShot import BasketballShot
import pandas as pd
from sportsdataverse.nba.nba_pbp import espn_nba_pbp
import plotly.graph_objects as go  # Import Plotly graph objects separately
import time
import re
import sportsdataverse
from streamlit_plotly_events import plotly_events
from datetime import datetime, timedelta

def filter_player_actions(df, player_names):
    # Combine player names into a single regex pattern
    pattern = '|'.join([rf'{name}\s+(made|make|missed|miss|makes|misses)' for name in player_names])
    
    # Apply the filter using regex matching
    filtered_df = df[df['text'].str.contains(pattern, flags=re.IGNORECASE, regex=True)]
    
    return filtered_df

def extract_number_from_string(s):
    # Regular expression pattern to find a number in the string
    pattern = r'\b\d+\b'
    
    # Using re.findall to get all numbers matching the pattern
    numbers = re.findall(pattern, s)
    
    # If numbers list is not empty, return the first number found (as a string)
    if numbers:
        return int(numbers[0])  # Convert the first number to an integer
    else:
        return 0  # Return 0 if no numbers were found

def fetch_and_save_nba_pbp(game_id, output_file):
    try:
        # Fetch play-by-play data
        pbp_data = espn_nba_pbp(game_id)

        # Extract plays information
        plays = pbp_data['plays']

        # Convert to DataFrame
        df_plays = pd.DataFrame(plays)

        # Save to CSV
        df_plays.to_csv(output_file, index=False)

        print(f"Successfully saved play-by-play data to {output_file}")
    except Exception as e:
        print(f"Error fetching or saving play-by-play data: {e}")

def map_team_to_abbreviation(team_name):
    team_mapping = {
        'Boston Celtics': 'bos',
        'Brooklyn Nets': 'bkn',
        'New York Knicks': 'ny',
        'Philadelphia 76ers': 'phi',
        'Toronto Raptors': 'tor',
        'Chicago Bulls': 'chi',
        'Cleveland Cavaliers': 'cle',
        'Detroit Pistons': 'det',
        'Indiana Pacers': 'ind',
        'Milwaukee Bucks': 'mil',
        'Denver Nuggets': 'den',
        'Minnesota Timberwolves': 'min',
        'Oklahoma City Thunder': 'okc',
        'Portland Trail Blazers': 'por',
        'Utah Jazz': 'utah',
        'Golden State Warriors': 'gs',
        'LA Clippers': 'lac',
        'Los Angeles Lakers': 'lal',
        'Phoenix Suns': 'phx',
        'Sacramento Kings': 'sac',
        'Atlanta Hawks': 'atl',
        'Charlotte Hornets': 'cha',
        'Miami Heat': 'mia',
        'Orlando Magic': 'orl',
        'Washington Wizards': 'wsh',
        'Dallas Mavericks': 'dal',
        'Houston Rockets': 'hou',
        'Memphis Grizzlies': 'mem',
        'New Orleans Pelicans': 'no',
        'San Antonio Spurs': 'sa'
    }
    
    return team_mapping.get(team_name, 'Unknown Team')

def display_team_image(teamname, width2):
    # Construct the URL for the player image using the player ID
    image_url = f"https://a.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/{teamname}.png&scale=crop&cquality=40&location=origin&w=80&h=80"
    
    
    # Check if the image URL returns a successful response
    response = requests.head(image_url)
    
    if response.status_code == 200:
        # If image is available, display it
        st.markdown(
    f'<div style="display: flex; flex-direction: column; align-items: center;">'
    f'<img src="{image_url}" style="width: {width2}px;">'
    f'<p style="text-align: center; font-size: 20px;"></p>'
    f'</div>',
    unsafe_allow_html=True
)
    
    
        # st.image(image_url, width=width2, caption=caption2)
    else:
        image_url = "https://a.espncdn.com/combiner/i?img=/i/teamlogos/leagues/500/nba.png&w=250&h=250"
        st.markdown(
        f'<div style="display: flex; flex-direction: column; align-items: center;">'
        f'<img src="{image_url}" style="width: {width2}px;">'
        f'<p style="text-align: center;font-size: larger;">{"Image Unavailable"}</p>'
        f'</div>',
        unsafe_allow_html=True
    )



st.set_page_config(page_title="3D NBA Shot Visualizer", page_icon='https://i.imgur.com/3oGJTcf.png',layout="wide")
st.markdown(f'<h3 style="color: gray; text-align: center; font-size: 100px;">3D NBA Shot Visualizer</h3>', unsafe_allow_html=True)

st.sidebar.markdown('<div style="text-align: center;"><span style="font-size:30px;">3D NBA Shot Visualizer</span></div>', unsafe_allow_html=True)
st.sidebar.image("https://i.imgur.com/3oGJTcf.png")

input_csv = 'nba_play_by_play.csv'  # Replace with your actual CSV file path
output_csv = 'nba_play_by_play.csv'  # Replace with desired output file path


# Determine the current year
current_year = date.today().year

# Create a selectbox in Streamlit with options from 2002 to the current year
selected_season = st.selectbox('Select a season', [''] + list(range(2002, current_year + 1)), index=0)
if selected_season:
    st.sidebar.markdown('<div style="text-align: center;"><span style="font-size:20px;">Filters</span></div>', unsafe_allow_html=True)
    st.sidebar.subheader('')

    from sportsdataverse.nba.nba_loaders import load_nba_schedule
    
    # Load NBA schedule for the 2007 season
    nba_df = load_nba_schedule(seasons=[selected_season], return_as_pandas=True)
    
    # Print or inspect the loaded DataFrame
    nba_df.to_csv('season.csv')
    
    # Load the CSV file
    csv_file = 'season.csv'
    df = pd.read_csv(csv_file)
    games = []
    for index, row in df.iterrows():
        # Concatenate home team and away team names for the current row
        ddate2 = row['start_date']
        parsed_date2 = datetime.strptime(ddate2, "%Y-%m-%dT%H:%MZ")
    
        # Format the datetime object into the desired string format
        formatted_date2 = parsed_date2.strftime("%m/%d/%Y")
        typegame = row['notes_headline']
        if selected_season > 2003 and pd.isna(typegame):
            typegame = 'Regular Season' 
        elif selected_season <= 2003 and pd.isna(typegame):
            typegame = ''
        game = f"{row['away_display_name']} @ {row['home_display_name']} - {typegame} - {formatted_date2} - {row['game_id']}"
        # Append the concatenated string to the games list
        games.append(game)# Create a selectbox in Streamlit
    games = st.selectbox('Select game', [''] + games)
    parts = games.split('-')
    
    # Extract the last element (which contains the number) and strip any extra whitespace
    id = parts[-1].strip()
    st.write('')
    if id:
        date1 = parts[-2].strip()

        fdf = pd.read_csv('season.csv')
        filtered_df = fdf[fdf['game_id'] == id]
    
    # Assuming 'date' is the column you want to extract
        if not filtered_df.empty:
            ddate = filtered_df['date'].iloc[0]
            parsed_date = datetime.strptime(ddate, "%Y-%m-%dT%H:%MZ")
    
            # Format the datetime object into the desired string format
            formatted_date = parsed_date.strftime("%m/%d/%Y")
        fetch_and_save_nba_pbp(game_id=id,output_file=output_csv)
    
        df = pd.read_csv(input_csv)
    
        # Replace 1 with True and 0 with False in 'SHOT_MADE_FLAG' column
        team_id = df['homeTeamId'][1]
    
        # Write the modified DataFrame back to CSV
        # df.to_csv(output_csv, index=False)
        # Define a function to apply to each row
        def label_team(row):
            if row['team.id'] == team_id:
                return 'home'
            else:
                return 'away'
    
        # Apply the function to create a new column 'team'
        df['team'] = df.apply(label_team, axis=1)
        df['home_color'] = '0022B4'
        df['away_color'] = '99bfe5'
        df = df[df['shootingPlay'] == True]
        df = df[~df['type.text'].str.contains('free throw', case=False, na=False)]
        df['Shot Distance'] = df['text'].apply(extract_number_from_string)

    
    
        unique_periods = df['period.displayValue'].unique()
        uniqueshots = df['type.text'].unique()

        df.to_csv(output_csv, index=False)
        Make = st.sidebar.toggle('Make/Miss')
        if Make == 1:
            makemiss = st.sidebar.selectbox('',['Make','Miss'])
            if makemiss == 'Make':
                rmakemiss = True
            else:
                rmakemiss = False
        Quarter = st.sidebar.toggle('Quarter')
        if Quarter == 1:
            quart = st.sidebar.multiselect('',unique_periods)
        Player = st.sidebar.toggle('Players')
        if Player == 1:
            import sportsdataverse.nba.nba_game_rosters as nba_rosters
            roster_data = nba_rosters.espn_nba_game_rosters(game_id=id, return_as_pandas=True)
            roster_data = roster_data[roster_data['did_not_play'] != True]
            names = []
            for index, row2 in roster_data.iterrows():
                name = row2['full_name']
                team = row2['team_display_name']
                player = name + " - " + team
                names.append(player)
            # player_names = roster_data['full_name'].tolist()
            players = st.sidebar.multiselect('',names)
            player_names = []
            for player_info in players:
                # Split each player_info string by ' - ' to separate player name and team
                player_name = player_info.split(' - ')[0]
                player_names.append(player_name)

        Shottype = st.sidebar.toggle('Shot Type')
        if Shottype == 1:
            shottype = st.sidebar.multiselect('',uniqueshots)
        Points = st.sidebar.toggle('Points')
        if Points == 1:
            points = st.sidebar.selectbox('',['2','3'])
        Time = st.sidebar.toggle('Time')
        if Time == 1:
            timemin, timemax = st.sidebar.slider("Time Remaining (Minutes)", 0, 15, (0, 15))
        Shotdist = st.sidebar.toggle('Shot Distance')
        if Shotdist == 1:
            shotdistance_min, shotdistance_max = st.sidebar.slider("Shot Distance", 0, 94, (0, 94))
        
    
    
        df2 = pd.read_csv('nba_play_by_play.csv')
        last_hyphen_index = games.rfind('-')

        result = games[:last_hyphen_index].strip()
        st.markdown(f'<h3 style="color: gray;text-align:center;">{result}</h3>', unsafe_allow_html=True)
        # st.markdown(f'<h3 style="color: gray;text-align:center;">{df["homeTeamName"].iloc[0]} {df["homeTeamMascot"].iloc[0]} vs {df["awayTeamName"].iloc[0]} {df["awayTeamMascot"].iloc[0]}</h3>', unsafe_allow_html=True)
        st.subheader('')
        hometeam = df['homeTeamName'].iloc[0] + " " + df['homeTeamMascot'].iloc[0]
        awayteam = df['awayTeamName'].iloc[0] + " " + df['awayTeamMascot'].iloc[0]
        homeabbrev = map_team_to_abbreviation(hometeam)
        awayabbrev = map_team_to_abbreviation(awayteam)
        col1, col2 = st.columns(2)
        with col1:
            display_team_image(awayabbrev,300)
        with col2:
            display_team_image(homeabbrev,300)
    
    
        # # create a connection
        # @st.cache_resource
        # def create_session_object():
        #     connection_parameters = {
        #        "account": "<ACCOUNT>",
        #        "user": "<USER>",
        #        "password": "<PASSWORD>",
        #        "role": "<ROLE>",
        #        "warehouse": "<WAREHOUSE>",
        #        "database": "<DATABASE>",
        #        "schema": "<SCHEMA"
        #     }
        #     session = Session.builder.configs(connection_parameters).create()
        #     return session
    
        # session = create_session_object()
    
        # # query the data
        # @st.cache_data
        # def load_data(query):
        #     data = session.sql(query)
        #     return data.to_pandas()
            
        # play_by_play_query = """
        #     SELECT  sequence_number,
        #             coordinate_x,
        #             coordinate_y,
        #             team_id,
        #             text,
        #             scoring_play,
        #             case 
        #                 when team_id = home_team_id
        #                     then 'home'
        #                 else 'away'
        #             end as scoring_team,
        #             game_id
        #     FROM    play_by_play
        #     WHERE   shooting_play
        #     AND     score_value != 1  -- shot charts typically do not include free throws
        # """
    
        # schedule_query = """
        #     select  concat(away_display_name_short, ' @ ', home_display_name_short, ' - ', notes_headline) as game,
        #             game_id,
        #             home_color,
        #             away_color
        #     from    schedule
        #     order by game_id desc
        # """
    
        schedule_df = pd.read_csv('nba_play_by_play.csv')
        play_by_play_df = pd.read_csv('nba_play_by_play.csv')
        import sportsdataverse.nba as nba
        nba_teams_df = nba.espn_nba_teams(return_as_pandas=True)
        home = nba_teams_df[nba_teams_df['team_display_name'] == hometeam]
        away = nba_teams_df[nba_teams_df['team_display_name'] == awayteam]
        if home['team_color'].isna().all():
            home_color = 'black'
        else:
            home_color = home['team_color'].iloc[0]
            home_color = '#' + home_color
        if away['team_color'].isna().all():
            away_color = 'gray'
        else:
            away_color = away['team_color'].iloc[0]
            away_color = '#' + away_color
        if home['team_alternate_color'].isna().all():
            home_color2 = 'black'
        else:
            home_color2 = home['team_alternate_color'].iloc[0]
            home_color2 = '#' + home_color2
        if away['team_alternate_color'].isna().all():
            away_color2 = 'gray'
        else:
            away_color2 = away['team_alternate_color'].iloc[0]
            away_color2 = '#' + away_color2
    
    
        # create single selection option
        # schedule_options = schedule_df[['GAME','GAME_ID']].set_index('GAME_ID')['GAME'].to_dict()
        # game_selection = st.sidebar.selectbox('Select Game', schedule_options.keys(), format_func=lambda x:schedule_options[x])
    
        # filter game specific values
                
    
        game_shots_df = pd.read_csv('nba_play_by_play.csv')
        if Quarter:
            game_shots_df = game_shots_df[game_shots_df['period.displayValue'].isin(quart)]
        if Shotdist:
            game_shots_df = game_shots_df[(game_shots_df['Shot Distance'] >= shotdistance_min) & (game_shots_df['Shot Distance'] <= shotdistance_max)]
        if Player:
            game_shots_df = filter_player_actions(game_shots_df, player_names)
            # game_shots_df = game_shots_df[game_shots_df['text'].str.contains('|'.join(player_names), case=False, na=False)]
        if Shottype:
            game_shots_df = game_shots_df[game_shots_df['type.text'].isin(shottype)]
        if Points:
            game_shots_df = game_shots_df[game_shots_df['scoreValue'] == int(points)]
        if Time:
            game_shots_df = game_shots_df[(game_shots_df['clock.minutes'] >= timemin) & (game_shots_df['clock.minutes'] <= timemax)]
        if Make:
            game_shots_df = game_shots_df[game_shots_df['scoringPlay'] == rmakemiss]
        # st.title(game_text)
    
        color_mapping = {
            'home': home_color,
            'away': away_color
        }
    
        # draw court lines
        court = CourtCoordinates()
        court_lines_df = court.get_court_lines()
    
        fig = px.line_3d(
            data_frame=court_lines_df,
            x='x',
            y='y',
            z='z',
            line_group='line_group',
            color='color',
            color_discrete_map={
                'court': '#000000',
                'hoop': '#e47041',
                'net': '#D3D3D3',
                'backboard': 'gray'
            }
        )
        fig.update_traces(hovertemplate=None, hoverinfo='skip', showlegend=False)
    
        game_coords_df = pd.DataFrame()
        # generate coordinates for shot paths
        homecount = 0
        hometotal = 0
        awaycount = 0
        awaytotal = 0
        for index, row in game_shots_df.iterrows():
            if row['team.id'] == team_id:
                hometotal+=1
                if row['scoringPlay'] == True:
                    homecount+=1
            elif row['team.id'] != team_id:
                awaytotal+=1
                if row['scoringPlay'] == True:
                    awaycount+=1
            shot = BasketballShot(
                shot_start_x=row['coordinate.x'], 
                shot_start_y=row['coordinate.y'], 
                shot_id=row['sequenceNumber'],
                play_description=row['text'],
                shot_made=row['scoringPlay'],
                team=row['team'],
                quarter=row['period.displayValue'],
                time=row['clock.displayValue'])
                # quarter=row['period.displayValue'])
            shot_df = shot.get_shot_path_coordinates()
            game_coords_df = pd.concat([game_coords_df, shot_df])
    
        # draw shot paths
        color_map={'away':away_color,'home':home_color2}
    
        shot_path_fig = px.line_3d(
            data_frame=game_coords_df,
            x='x',
            y='y',
            z='z',
            line_group='line_id',
            color='team',
            color_discrete_map=color_map,
            custom_data=['description', 'z','quarter','time']
        )
    
        hovertemplate= '%{customdata[0]}<br>%{customdata[2]} - %{customdata[3]}<br>Height: %{customdata[1]} ft'


        hovertemplate2 = '%{customdata[0]}<br>%{customdata[2]} - %{customdata[3]}'
        shot_path_fig.update_traces(opacity=0.55, hovertemplate=hovertemplate, showlegend=False)
    
        # shot start scatter plots
        game_coords_start = game_coords_df[game_coords_df['shot_coord_index'] == 0]
        symbol_map={'made': 'circle-open', 'missed': 'cross'}
        color_map={'away':away_color2,'home':home_color}
        shot_start_fig = px.scatter_3d(
            data_frame=game_coords_start,
            x='x',
            y='y',
            z='z',
            custom_data=['description', 'z','quarter','time'],
            color='team',
            color_discrete_map=color_map,
            # color_discrete_map=color_mapping,
            
            symbol='shot_made',
            
            symbol_map=symbol_map
        )
        symbol_map2={'made': 'circle', 'missed': 'cross'}

        shot_start_fig2 = px.scatter_3d(
            data_frame=game_coords_start,
            x='x',
            y='y',
            z='z',
            custom_data=['description', 'z','quarter','time'],
            color='team',
            color_discrete_map=color_map,
            # color_discrete_map=color_mapping,
            
            symbol='shot_made',
            
            symbol_map=symbol_map2
        )
    
        shot_start_fig.update_traces(marker_size=10, hovertemplate=hovertemplate2)
        shot_start_fig2.update_traces(marker_size=7,hovertemplate=hovertemplate2)

    
        # add shot scatter plot to court plot
        for i in range(len(shot_start_fig.data)):
            fig.add_trace(shot_start_fig.data[i])
            fig.add_trace(shot_start_fig2.data[i])
        # add shot line plot to court plot
        for i in range(len(shot_path_fig.data)):
            fig.add_trace(shot_path_fig.data[i])
    
        # graph styling
        fig.update_traces(line=dict(width=5))
        fig.update_layout(    
            margin=dict(l=20, r=20, t=20, b=20),
            scene_aspectmode="data",
            height=600,
            scene_camera=dict(
                eye=dict(x=1.3, y=0, z=0.7)
            ),
            scene=dict(
                xaxis=dict(title='', showticklabels=False, showgrid=False),
                yaxis=dict(title='', showticklabels=False, showgrid=False),
                zaxis=dict(title='',  showticklabels=False, showgrid=False, showbackground=True, backgroundcolor='#d2a679'),
            ),
            showlegend=False,
            legend=dict(
                yanchor='top',
                y=0.05,
                x=0.2,
                xanchor='left',
                orientation='h',
                font=dict(size=15, color='gray'),
                bgcolor='rgba(0, 0, 0, 0)',
                title='',
                itemsizing='constant'
            )
        )
        selected_points = plotly_events(fig, click_event=True, hover_event=False)
        if selected_season >= 2015:
            st.caption("Click on a marker to view the highlight video")
# Display the plot
# st.plotly_chart(fig, use_container_width=True)

        # Display selected points
        if selected_points:
            for point in selected_points:
                # Extract point details
                x_val = point.get('x', 'N/A')
                y_val = point.get('y', 'N/A')
                z_val = point.get('z', 'N/A')
                curve_number = point.get('curveNumber', 'N/A')
                point_number = point.get('pointNumber', 'N/A')
                
                # Find the corresponding description based on index
                description = 'No description available'
                if point_number < len(game_coords_df):
                    game_coords_df2 = game_coords_df[game_coords_df['x'] == x_val]
                    game_coords_df2 = game_coords_df2[game_coords_df2['y'] == y_val]
                description = game_coords_df2['description'].iloc[0]
                time = game_coords_df2['time'].iloc[0]
                game2 = game_shots_df[game_shots_df['text'] == description]
                game2 = game2[game2['time'] == time]
                abbreviation = game2['homeTeamAbbrev'].iloc[0]
                abbreviation2 = game2['awayTeamAbbrev'].iloc[0]
                from nba_api.stats.static import teams

                nba_teams = teams.get_teams()
                # Select the dictionary for the Celtics, which contains their team ID
                # st.write(abbreviation)
                team = [team for team in nba_teams if team['abbreviation'] == abbreviation][0]
                teamidreal = team['id']
                # st.write(teamidreal)
                from nba_api.stats.endpoints import leaguegamefinder

                # Query for games where the Celtics were playing
                gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=teamidreal)
                # The first DataFrame of those returned is what we want.
                games = gamefinder.get_data_frames()[0]
                games = games[games['MATCHUP'].str.contains(abbreviation2, na=False)]
                # Convert to datetime object
# Convert to datetime object
                # st.write(games)
                date_obj = datetime.strptime(date1, '%m/%d/%Y')

                # Convert to desired format
                date2 = date_obj.strftime('%Y-%m-%d')

                # Attempt to filter games by the original date
                fgames = games[games['GAME_DATE'] == date2]

                # Check if games DataFrame is empty
                if fgames.empty:
                    # If no games found, subtract one day and filter again
                    new_date_obj = date_obj - timedelta(days=1)
                    date2 = new_date_obj.strftime('%Y-%m-%d')
                    
                    # Attempt to filter games by the new date
                    fgames = games[games['GAME_DATE'] == date2]
                games = fgames
                # st.write(date2)
                # st.write(games)
                game_id = games['GAME_ID'].iloc[0]
                playid = game2['sequenceNumber'].iloc[0]
                headers = {
                'Host': 'stats.nba.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'x-nba-stats-origin': 'stats',
                'x-nba-stats-token': 'true',
                'Connection': 'keep-alive',
                'Referer': 'https://stats.nba.com/',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache'
            }
                event_id = playid



                url = 'https://stats.nba.com/stats/videoeventsasset?GameEventID={}&GameID={}'.format(
                            event_id, game_id)
                r = requests.get(url, headers=headers)
                if r.status_code == 200:
                    json = r.json()
                    video_urls = json['resultSets']['Meta']['videoUrls']
                    playlist = json['resultSets']['playlist']
                    video_event = {'video': video_urls[0]['lurl'], 'desc': playlist[0]['dsc']}
                    video = video_urls[0]['lurl']

                # Display point details
                
                # st.write(game2)
                if selected_season >= 2015:
                    col1,col2,col3 = st.columns(3)

                    with col2:
                        st.video(video)
                        st.write(description)

       

        # graph styling
        # normalplot = st.sidebar.button('Normal Plot')
        # play = st.sidebar.button('Play by play')
        
        # if play:
        #     # Draw basketball court lines
        #     court = CourtCoordinates()
        #     court_lines_df = court.get_court_lines()
    
        #     fig = px.line_3d(
        #     data_frame=court_lines_df,
        #     x='x',
        #     y='y',
        #     z='z',
        #     line_group='line_group',
        #     color='color',
        #     color_discrete_map={
        #         'court': '#000000',
        #         'hoop': '#e47041',
        #         'net': '#D3D3D3',
        #         'backboard': 'gray'
        #     }
        # )
        #     fig.update_traces(hovertemplate=None, hoverinfo='skip', showlegend=False)
        #     fig.update_traces(line=dict(width=5))
    
        #     # Apply layout settings
        #     fig.update_layout(    
        #         margin=dict(l=20, r=20, t=20, b=20),
        #         scene_aspectmode="data",
        #         height=600,
        #         scene_camera=dict(
        #             eye=dict(x=1.5, y=0, z=0.2)
        #         ),
        #         scene=dict(
        #             xaxis=dict(title='', showticklabels=False, showgrid=False),
        #             yaxis=dict(title='', showticklabels=False, showgrid=False),
        #             zaxis=dict(title='', showticklabels=False, showgrid=False, showbackground=True, backgroundcolor='#d2a679'),
        #         )
        #     )
    
        #     # Create a Streamlit placeholder for the plot
        #     placeholder = st.empty()
    
        #     # Prepare data filters
        #     filters = {
        #         'period.displayValue': quart if Quarter else None,
        #         'Shot Distance': (shotdistance_min, shotdistance_max) if Shotdist else None,
        #         'text': players if Player else None,
        #         'type.text': finaltype if Shottype else None,
        #         'scoreValue': int(points) if Points else None,
        #         'clock.minutes': (timemin, timemax) if Time else None
        #     }
    
        #     filtered_shot_df = df.copy()
    
        #     if Quarter:
        #         filtered_shot_df = filtered_shot_df[filtered_shot_df['period.displayValue'].isin(quart)]
        #     if Shotdist:
        #         filtered_shot_df = filtered_shot_df[(filtered_shot_df['Shot Distance'] >= shotdistance_min) & (filtered_shot_df['Shot Distance'] <= shotdistance_max)]
        #     if Player:
        #         filtered_shot_df = filter_player_actions(filtered_shot_df, player_names)
        #         # game_shots_df = game_shots_df[game_shots_df['text'].str.contains('|'.join(player_names), case=False, na=False)]
        #     if Shottype:
        #         filtered_shot_df = filtered_shot_df[filtered_shot_df['type.text'].isin(shottype)]
        #     if Points:
        #         filtered_shot_df = filtered_shot_df[filtered_shot_df['scoreValue'] == int(points)]
        #     if Time:
        #         filtered_shot_df = filtered_shot_df[(filtered_shot_df['clock.minutes'] >= timemin) & (filtered_shot_df['clock.minutes'] <= timemax)]
        #     if Make:
        #         filtered_shot_df = filtered_shot_df[filtered_shot_df['scoringPlay'] == rmakemiss]
        
        #     # Initialize an empty list to store trace objects
        #     traces = []
        #     message_placeholder = st.empty()
        #     message2 = st.empty()
        #     message3 = st.empty()
        #     messages = []
    
        #     game_coords_df = pd.DataFrame()  # Initialize empty DataFrame to store all shot coordinates
    
        #     traces = []
        #     message_placeholder = st.empty()
        #     message2 = st.empty()
        #     message3 = st.empty()
        #     messages = []
            
        #     for index, row in game_shots_df.iterrows():
        #         # Assuming BasketballShot class or function to generate shot coordinates
        #         shot = BasketballShot(
        #             shot_start_x=row['coordinate.x'], 
        #             shot_start_y=row['coordinate.y'], 
        #             shot_id=row['sequenceNumber'],
        #             play_description=row['text'],
        #             shot_made=row['scoringPlay'],
        #             team=row['team'],
        #             quarter=row['period.displayValue'],
        #             time=row['clock.displayValue'])
                
        #         shot_df = shot.get_shot_path_coordinates()
        #         game_coords_df = pd.concat([game_coords_df, shot_df])
    
        #         # Draw shot paths
        #         color_map = {'home': home_color2, 'away': away_color}
        #         shot_path_fig = px.line_3d(
        #             data_frame=game_coords_df,
        #             x='x',
        #             y='y',
        #             z='z',
        #             line_group='line_id',
        #             color='team',
        #             color_discrete_map=color_map,
        #             custom_data=['description', 'z', 'quarter', 'time']
        #         )
    
        #         hovertemplate = '%{customdata[0]}<br>%{customdata[2]} - %{customdata[3]}'
        #         shot_path_fig.update_traces(opacity=0.55, hovertemplate=hovertemplate, showlegend=False)
    
        #         # Draw shot start scatter plots
        #         game_coords_start = game_coords_df[game_coords_df['shot_coord_index'] == 0]
        #         symbol_map = {'made': 'circle-open', 'missed': 'cross'}
        #         color_map = {'home': home_color, 'away': away_color2}
        #         shot_start_fig = px.scatter_3d(
        #             data_frame=game_coords_start,
        #             x='x',
        #             y='y',
        #             z='z',
        #             custom_data=['description', 'z', 'quarter', 'time'],
        #             color='team',
        #             color_discrete_map=color_map,
        #             symbol='shot_made',
        #             symbol_map=symbol_map,
        #         )
    
        #         shot_start_fig.update_traces(marker_size=10, hovertemplate=hovertemplate,showlegend=False)
    
        #         # Add shot scatter plot to the existing figure
                
    
        #         for trace in shot_start_fig.data:
        #             fig.add_trace(trace)
    
        #         # Add shot line plot to the existing figure
        #         for trace in shot_path_fig.data:
        #             fig.add_trace(trace)
    
        #         # Update layout and display the figure dynamically
        #         fig.update_traces(line=dict(width=5))
        #         message = row['text']
        #         message2 = row['period.displayValue']
        #         message3 = row['clock.displayValue']
        #         if row['scoringPlay'] == True:
        #             finalmessage = f"✅ {message} - {message2}: {message3}"
        #         else:
        #             finalmessage = f"❌ {message} - {message2}: {message3}"
        #         messages.append(finalmessage)
        #         placeholder.plotly_chart(fig, use_container_width=True)
        #         message_placeholder.text(message)
        #         if message == None:
        #             st.text('')
        #         else:
        #             message_placeholder.text(f'Latest shot: {message} - {message2}: {message3}')
        #         time.sleep(2)
        #     placeholder.plotly_chart(fig, use_container_width=True)
        #     coli1,coli2 = st.columns(2)
        #     if awaytotal != 0:
        #         awayper = (awaycount/awaytotal) * 100
        #         awayper = round(awayper,2)
        #     else:
        #         awayper = 0
        #     if hometotal != 0:
        #         homeper = (homecount/hometotal) * 100
        #         homeper = round(homeper,2)
        #     else:
        #         homeper = 0
        #     with coli1:
        #         st.markdown(f'<h3 style="text-align:center;">'
        #         f'<span style="color: {away_color2};">{df["awayTeamName"].iloc[0]} {df["awayTeamMascot"].iloc[0]}:</span> '
        #         f'<span style="color: {away_color};">{awaycount}/{awaytotal} ({awayper}%)</span> '
        #         f'</h3>', unsafe_allow_html=True)
        #     with coli2:
        #         st.markdown(f'<h3 style="text-align:center;">'
        #         f'<span style="color: {home_color2};">{df["homeTeamName"].iloc[0]} {df["homeTeamMascot"].iloc[0]}:</span> '
        #         f'<span style="color: {home_color};">{homecount}/{hometotal} ({homeper}%)</span> '
        #         f'</h3>', unsafe_allow_html=True)
        #     with st.expander('All Shots'):
        #         for msg in messages:
        #             st.text(msg)
        #     if normalplot:
        #         st.plotly_chart(fig, use_container_width=True)
        #         coli1,coli2 = st.columns(2)
        #         if awaytotal != 0:
        #             awayper = (awaycount/awaytotal) * 100
        #             awayper = round(awayper,2)
        #         else:
        #             awayper = 0
        #         if hometotal != 0:
        #             homeper = (homecount/hometotal) * 100
        #             homeper = round(homeper,2)
        #         else:
        #             homeper = 0
        #         with coli1:
        #             st.markdown(f'<h3 style="text-align:center;">'
        #             f'<span style="color: {away_color2};">{df["awayTeamName"].iloc[0]} {df["awayTeamMascot"].iloc[0]}:</span> '
        #             f'<span style="color: {away_color};">{awaycount}/{awaytotal} ({awayper}%)</span> '
        #             f'</h3>', unsafe_allow_html=True)
        #         with coli2:
        #             st.markdown(f'<h3 style="text-align:center;">'
        #             f'<span style="color: {home_color2};">{df["homeTeamName"].iloc[0]} {df["homeTeamMascot"].iloc[0]}:</span> '
        #             f'<span style="color: {home_color};">{homecount}/{hometotal} ({homeper}%)</span> '
        #             f'</h3>', unsafe_allow_html=True)

        # # else:
        #     # st.plotly_chart(fig, use_container_width=True)
        #     coli1,coli2 = st.columns(2)
        #     if awaytotal != 0:
        #         awayper = (awaycount/awaytotal) * 100
        #         awayper = round(awayper,2)
        #     else:
        #         awayper = 0
        #     if hometotal != 0:
        #         homeper = (homecount/hometotal) * 100
        #         homeper = round(homeper,2)
        #     else:
        #         homeper = 0
        #     with coli1:
        #         st.markdown(f'<h3 style="text-align:center;">'
        #         f'<span style="color: {away_color2};">{df["awayTeamName"].iloc[0]} {df["awayTeamMascot"].iloc[0]}:</span> '
        #         f'<span style="color: {away_color};">{awaycount}/{awaytotal} ({awayper}%)</span> '
        #         f'</h3>', unsafe_allow_html=True)
        #     with coli2:
        #         st.markdown(f'<h3 style="text-align:center;">'
        #         f'<span style="color: {home_color2};">{df["homeTeamName"].iloc[0]} {df["homeTeamMascot"].iloc[0]}:</span> '
        #         f'<span style="color: {home_color};">{homecount}/{hometotal} ({homeper}%)</span> '
        #         f'</h3>', unsafe_allow_html=True)
        nba_data = sportsdataverse.nba.espn_nba_pbp(game_id=id)
        # Check if 'boxscore' exists in the fetched data
        df = nba_data['boxscore']

        teams = df['teams']
        players = df['players']
        def flatten_team_data(teams):
            flat_list = []
            for team in teams:
                team_info = team['team']
                stats = {stat['label']: stat['displayValue'] for stat in team['statistics']}
                stats.update({
                    'team_id': team_info['id'],
                    'team_location': team_info['location'],
                    'team_name': team_info['name'],
                    'team_abbreviation': team_info['abbreviation'],
                    'team_displayName': team_info['displayName'],
                    'homeAway': team['homeAway']
                })
                flat_list.append(stats)
            return pd.DataFrame(flat_list)

        # Apply the function to the data
        team_df = flatten_team_data(df['teams'])
        # team_df.to_csv('route_locations_2019.csv')

        def flatten_player_data(players):
            flat_list = []
            
            for team in players:
                team_info = team['team']
                stats_labels = team['statistics'][0]['labels']
                stats_keys = team['statistics'][0]['keys']
                
                for player in team['statistics'][0]['athletes']:
                    if player['stats']:
                        player_stats = {key: value for key, value in zip(stats_keys, player['stats'])}
                        player_info = player['athlete']
                        
                        player_data = {
                            'player_id': player_info['id'],
                            'player_name': player_info['displayName'],
                            'player_shortName': player_info['shortName'],
                            'player_position': player_info['position']['displayName'],
                            'team_id': team_info['id'],
                            'team_location': team_info['location'],
                            'team_name': team_info['name'],
                            'team_abbreviation': team_info['abbreviation'],
                            'team_displayName': team_info['displayName'],
                        }
                        
                        player_data.update({label: player_stats.get(key, '') for label, key in zip(stats_labels, stats_keys)})
                        
                        flat_list.append(player_data)
            
            return pd.DataFrame(flat_list)
        playerdf = flatten_player_data(players)
        st.subheader('Team Boxscore')
        team_df = team_df.drop(columns=['team_name','team_location','team_abbreviation','team_id'])
        team_df = team_df[['team_displayName'] + [col for col in team_df.columns if col != 'team_displayName']]
        st.write(team_df)
        st.subheader('Player Boxscore')
        st.write(playerdf[['player_name','team_displayName','player_position','MIN','FG','3PT','FT','OREB','DREB','REB','AST','STL','BLK','TO','PF','+/-','PTS']])



        # # Check if the data was fetched successfully and if 'videos' exists
        # if 'videos' in nba_data and nba_data['videos']:
        #     videos_data = nba_data['videos']
            
        #     # Convert to DataFrame
        #     if isinstance(videos_data, list):
        #         try:
        #             videos_df = pd.DataFrame(videos_data)
                    
        #             # Check if 'links' column exists
        #             if 'links' in videos_df.columns:
        #                 # Extract 'links' column
        #                 links_df = pd.json_normalize(videos_df['links'])
        #                 with st.expander('Videos'):
        #                     for index, row in links_df.iterrows():
        #                         link = row['source.HD.href']
        #                         st.video(link)
                        
        #                 # Print the new DataFrame to verify                        
        #                 # Optionally, save the links DataFrame to a CSV file
        #             else:
        #                 st.error("'links' column not found in the DataFrame.")
        #         except ValueError as e:
        #             print("Error creating DataFrame:", e)
        #     else:
        #         st.error("Expected a list of dictionaries or similar format.")
        # else:
        #     st.write("")
else:
    image_url = 'https://i.imgur.com/3oGJTcf.png'

    st.markdown(f'<img src="{image_url}" style="width:100%; height:auto;">', unsafe_allow_html=True)

    
    
