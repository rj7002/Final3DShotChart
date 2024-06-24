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
        'Los Angeles Clippers': 'lac',
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
        image_url = "https://cdn.nba.com/headshots/nba/latest/1040x760/fallback.png"
        st.markdown(
        f'<div style="display: flex; flex-direction: column; align-items: center;">'
        f'<img src="{image_url}" style="width: {width2}px;">'
        f'<p style="text-align: center;font-size: larger;">{"Image Unavailable"}</p>'
        f'</div>',
        unsafe_allow_html=True
    )



st.set_page_config(page_title="3D NBA Shot Visualizer", page_icon='https://www.shutterstock.com/image-vector/basketball-player-shooting-ball-abstract-260nw-1059100829.jpg',layout="wide")
st.markdown(f'<h3 style="color: gray; text-align: center; font-size: 100px;">3D NBA Shot Visualizer</h3>', unsafe_allow_html=True)

st.sidebar.markdown('<div style="text-align: center;"><span style="font-size:30px;">3D NBA Shot Visualizer</span></div>', unsafe_allow_html=True)
input_csv = 'nba_play_by_play.csv'  # Replace with your actual CSV file path
output_csv = 'nba_play_by_play.csv'  # Replace with desired output file path


# Determine the current year
current_year = date.today().year

# Create a selectbox in Streamlit with options from 2002 to the current year
selected_season = st.selectbox('Select a season', [''] + list(range(2002, current_year + 1)), index=0)
from sportsdataverse.nba.nba_loaders import load_nba_schedule

# Load NBA schedule for the 2007 season
nba_df = load_nba_schedule(seasons=[selected_season], return_as_pandas=True)

# Print or inspect the loaded DataFrame
nba_df.to_csv('season.csv')

# Load the CSV file
csv_file = 'season.csv'
df = pd.read_csv(csv_file)
# Assuming 'game_id' is the column in season.csv that contains game IDs
game_ids = df['game_id'].tolist()

# Create a selectbox in Streamlit
final_gameid = st.selectbox('Select Game ID', ['']+ game_ids)

if final_gameid:
    fdf = pd.read_csv('season.csv')
    filtered_df = fdf[fdf['game_id'] == final_gameid]

# Assuming 'date' is the column you want to extract
    if not filtered_df.empty:
        ddate = filtered_df['date'].iloc[0]
        parsed_date = datetime.strptime(ddate, "%Y-%m-%dT%H:%MZ")

        # Format the datetime object into the desired string format
        formatted_date = parsed_date.strftime("%m/%d/%Y")
    fetch_and_save_nba_pbp(game_id=final_gameid,output_file=output_csv)

    df = pd.read_csv(input_csv)

    # Replace 1 with True and 0 with False in 'SHOT_MADE_FLAG' column
    team_id = df['team.id'][1]

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
    df['Shot Distance'] = ((df['coordinate.x'] - 25).pow(2) +
                       (df['coordinate.y'] - df.apply(lambda row: 89.75 if row['team'] == 'away' else 4.25, axis=1)).pow(2)).pow(0.5)
    df.loc[df['team'] == 'away', 'Shot Distance'] = abs(df.loc[df['team'] == 'away', 'Shot Distance'] - 94)



    df.to_csv(output_csv, index=False)
    Quarter = st.sidebar.toggle('Quarter')
    if Quarter == 1:
        quart = st.sidebar.multiselect('',['1st Quarter','2nd Quarter','3rd Quarter','4th Quarter'])
    Player = st.sidebar.toggle('Players')
    if Player == 1:
        import sportsdataverse.nba.nba_game_rosters as nba_rosters
        roster_data = nba_rosters.espn_nba_game_rosters(game_id=final_gameid, return_as_pandas=True)
        player_names = roster_data['full_name'].tolist()
        players = st.sidebar.multiselect('',player_names)
    Shottype = st.sidebar.toggle('Shot Type')
    if Shottype == 1:
        shottype = st.sidebar.selectbox('', ['Jump Shot', 'Layup','Dunk','Other'])
        if shottype == 'Jump Shot':
            jumpshottype = st.sidebar.multiselect('', ['Step Back Jump shot', 'Running Pull-Up Jump Shot','Turnaround Fade Away shot','Fade Away Jump Shot','Pullup Jump Shot','Jump Bank Shot','Jump Shot'])
            finaltype = jumpshottype
        elif shottype == 'Layup':
            layuptype = st.sidebar.multiselect('', ['Layup Shot', 'Running Finger Roll Layup Shot','Cutting Layup Shot','Driving Layup Shot','Running Layup Shot','Alley Oop Layup shot','Tip Layup Shot','Reverse Layup Shot','Driving Reverse Layup Shot','Running Reverse Layup Shot'])
            finaltype = layuptype
        elif shottype == 'Dunk':
            dunktype = st.sidebar.multiselect('', ['Running Dunk Shot', 'Cutting Dunk Shot','Running Reverse Dunk Shot','Running Alley Oop Dunk Shot','Dunk Shot','Tip Dunk Shot'])    
            finaltype = dunktype
        elif shottype == 'Other':
            othertype = st.sidebar.multiselect('', ['Driving Floating Jump Shot', 'Floating Jump shot','Driving Floating Bank Jump Shot','Driving Bank Hook Shot','Driving Hook Shot','Turnaround Hook Shot','Hook Shot'])
            finaltype = othertype
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
    st.markdown(f'<h3 style="color: gray;text-align:center;">{df["homeTeamName"].iloc[0]} {df["homeTeamMascot"].iloc[0]} vs {df["awayTeamName"].iloc[0]} {df["awayTeamMascot"].iloc[0]} - {formatted_date}</h3>', unsafe_allow_html=True)
    st.subheader('')
    hometeam = df['homeTeamName'].iloc[0] + " " + df['homeTeamMascot'].iloc[0]
    awayteam = df['awayTeamName'].iloc[0] + " " + df['awayTeamMascot'].iloc[0]
    homeabbrev = map_team_to_abbreviation(hometeam)
    awayabbrev = map_team_to_abbreviation(awayteam)
    col1, col2 = st.columns(2)
    with col1:
        display_team_image(homeabbrev,300)
    with col2:
        display_team_image(awayabbrev,300)


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
         game_shots_df = game_shots_df[game_shots_df['text'].str.contains('|'.join(players), case=False, na=False)]
    if Shottype:
        game_shots_df = game_shots_df[game_shots_df['type.text'].isin(finaltype)]
    if Points:
        game_shots_df = game_shots_df[game_shots_df['scoreValue'] == int(points)]
    if Time:
        game_shots_df = game_shots_df[(game_shots_df['clock.minutes'] >= timemin) & (game_shots_df['clock.minutes'] <= timemax)]
    home_color = schedule_df['home_color']
    away_color = schedule_df['away_color']
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
            'hoop': '#e47041'
        }
    )
    fig.update_traces(hovertemplate=None, hoverinfo='skip', showlegend=False)

    game_coords_df = pd.DataFrame()
    # generate coordinates for shot paths
    for index, row in game_shots_df.iterrows():
        shot = BasketballShot(
            shot_start_x=row['coordinate.x'], 
            shot_start_y=row['coordinate.y'], 
            shot_id=row['sequenceNumber'],
            play_description=row['text'],
            shot_made=row['scoringPlay'],
            team=row['team'])
            # quarter=row['period.displayValue'])
        shot_df = shot.get_shot_path_coordinates()
        game_coords_df = pd.concat([game_coords_df, shot_df])

    # draw shot paths
    color_map={'home':'blue','away':'red'}

    shot_path_fig = px.line_3d(
        data_frame=game_coords_df,
        x='x',
        y='y',
        z='z',
        line_group='line_id',
        color='team',
        color_discrete_map=color_map,
        custom_data=['description']
    )

    hovertemplate=' %{customdata[0]}'
    shot_path_fig.update_traces(opacity=0.55, hovertemplate=hovertemplate, showlegend=False)

    # shot start scatter plots
    game_coords_start = game_coords_df[game_coords_df['shot_coord_index'] == 0]
    symbol_map={'made': 'circle-open', 'missed': 'cross'}
    color_map={'home':'blue','away':'red'}
    shot_start_fig = px.scatter_3d(
        data_frame=game_coords_start,
        x='x',
        y='y',
        z='z',
        custom_data=['description'],
        color='team',
        color_discrete_map=color_map,
        # color_discrete_map=color_mapping,
        
        symbol='shot_made',
        
        symbol_map=symbol_map
    )

    shot_start_fig.update_traces(marker_size=7, hovertemplate=hovertemplate)

    # add shot scatter plot to court plot
    for i in range(len(shot_start_fig.data)):
        fig.add_trace(shot_start_fig.data[i])

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
            zaxis=dict(title='',  showticklabels=False, showgrid=False, showbackground=True, backgroundcolor='#D2B48C'),
        ),
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
        ),
        legend_traceorder="reversed"
    )
    play = st.button('Play by play')
    if play:
                # Draw basketball court lines
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
                'hoop': '#e47041'
            }
        )
        fig.update_traces(hovertemplate=None, hoverinfo='skip', showlegend=False)

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
                zaxis=dict(title='',  showticklabels=False, showgrid=False, showbackground=True, backgroundcolor='#D2B48C'),
            ),
            # legend=dict(
            #     yanchor='top',
            #     y=0.05,
            #     x=0.2,
            #     xanchor='left',
            #     orientation='h',
            #     font=dict(size=15, color='gray'),
            #     bgcolor='rgba(0, 0, 0, 0)',
            #     title='',
            #     itemsizing='constant'
            # ),
            # legend_traceorder="reversed"
        )
        # Create a Streamlit placeholder for the plot
        placeholder = st.empty()

        # Iterate through each row in the DataFrame to add scatter points one by one
        for index, row in df.iterrows():
            # Assuming you have a utility to get shot path coordinates
            shot = BasketballShot(
                shot_start_x=row['coordinate.x'],
                shot_start_y=row['coordinate.y'],
                shot_id=row['sequenceNumber'],
                play_description=row['text'],
                shot_made=row['scoringPlay'],
                team=row['team']
            )
            shot_df = shot.get_shot_path_coordinates()
            if Quarter:
                shot_df = shot_df[shot_df['period.displayValue'].isin(quart)]
            if Shotdist:
                shot_df = shot_df[(shot_df['Shot Distance'] >= shotdistance_min) & (shot_df['Shot Distance'] <= shotdistance_max)]
            if Player:
                shot_df = shot_df[shot_df['description'].str.contains('|'.join(players), case=False, na=False)]
            if Shottype:
                shot_df = shot_df[shot_df['type.text'].isin(finaltype)]
            if Points:
                shot_df = shot_df[shot_df['scoreValue'] == int(points)]
            if Time:
                shot_df = shot_df[(shot_df['clock.minutes'] >= timemin) & (shot_df['clock.minutes'] <= timemax)]

            # Determine color and symbol based on shot made or missed
            if row['scoringPlay']:
                marker_color = 'blue' if row['team'] == 'home' else 'red'
                marker_symbol = 'circle-open'
            else:
                marker_color = 'blue' if row['team'] == 'home' else 'red'
                marker_symbol = 'x'

            # Add each point one by one to the figure
            text_all = (
)
            hover_template = (
            "<b>%{customdata[0]}<br>")
            shot_df['text'] = shot_df['description']
            
            for _, shot_row in shot_df.iterrows():
                fig.add_trace(
                    go.Scatter3d(
                        x=[shot_row['x']],
                        y=[shot_row['y']],
                        z=[shot_row['z']],
                        mode='markers',
                        marker=dict(
                            size=4,
                            color=marker_color,
                            symbol=marker_symbol,
                            line=dict(width=0)
                        ),
                        hoverinfo='text',
                        hovertemplate="<b>%{customdata}</b><extra></extra>",
                        customdata=[shot_row['description']],
                         showlegend=False
                    )
                )

                # Update the placeholder with the updated figure
                placeholder.plotly_chart(fig, use_container_width=True)

        # Final update of the placeholder with the fully rendered figure
        placeholder.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(fig, use_container_width=True)
