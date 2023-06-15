import pandas as pd
import numpy as np
import streamlit as st

pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

cols = list('abcde')
data = np.array([
    [-1,-1,0,1,1],
    [3,3,0,-3,-3],
    [0,2,2,-2,-2]
])

df = pd.DataFrame(data, columns=cols)

def fetch_data():
    data = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vTMY3vUGk6ghEpKPxcJ3usmyD6JPdLKvJNq6ELpGHMENcSp-Gy986Qyl2cP77Ad75SO3KAobPLsnWFc/pub?gid=0&single=true&output=csv', skiprows=3)
    data.drop(columns=['Unnamed: 0', 'Validi'], inplace=True)
    return data


def get_all_possible_teams(players):
    import itertools
    return [sorted(x) for x in itertools.combinations(players, 2)]


def get_all_possible_matches(players):
    all_possible_teams = get_all_possible_teams(players)
    all_possible_matches = [sorted(x) for x in itertools.combinations(all_possible_teams, 2) if len(set(itertools.chain(*x)))==4]
    return all_possible_matches

data = fetch_data()
players = sorted(data.drop(columns='Esterni').columns.to_list())
all_possible_teams = get_all_possible_teams(players)
all_possible_teams = pd.DataFrame(all_possible_teams, columns=['player1', 'player2'])
# all_possible_matches = pd.DataFrame(all_possible_matches, columns=['team1', 'team2'])

score = data.drop(columns='Esterni').mean().reset_index().rename(columns={'index': 'player', 0: 'score'})

# %% INterface
player1 = st.selectbox(label='Player 1, Team 1', options=players)
player2 = st.selectbox(label='Player 2, Team 1', options=players)
player3 = st.selectbox(label='Player 1, Team 2', options=players)
player4 = st.selectbox(label='Player 2, Team 2', options=players)


# %%
matches = []
teams = []
for i, row in data.iterrows():
    winner = tuple(sorted(row[row>0].index.to_list()))
    loser = tuple(sorted(row[row<0].index.to_list()))
    match = tuple(sorted((winner, loser)))  # sorted so order of winner/loser doesn't matter
    teams.append(winner)
    teams.append(loser)
    matches.append(match)
t = {item:teams.count(item) for item in set(teams)}
m = {item:matches.count(item) for item in set(matches)}

t = pd.DataFrame(t, index=[0]).T.reset_index()
t.columns = ['player1', 'player2', 'nmatches']
m = pd.DataFrame(m, index=[0]).T.reset_index()
m.columns = ['team1', 'team2', 'nmatches']
t.sort_values('nmatches')

df = pd.merge(all_possible_teams, t, how='outer').fillna(0)\
    .merge(score.rename(columns={'player': 'player1', 'score': 'score1'}), on='player1')\
    .merge(score.rename(columns={'player': 'player2', 'score': 'score2'}), on='player2')\
    .assign(team_score=lambda x: (x.score1+x.score2/2))\
    .assign(in_team_imbalance=lambda x: np.abs(x.score1 - x.score2))\
    .sort_values(by=['nmatches', 'in_team_imbalance'], ascending=[True, True]).rename(columns={'score1': 'avg_score_player1', 'score2': 'avg_score_player2'})

player1 = 'Leo'
player2 = 'Stefania'
player3 = 'Matteo C'
player4 = 'Francesco G'

if player1 != player2 != player3 != player4:
    player1, player2 = sorted((player1, player2))
    player3, player4 = sorted((player3, player4))

    team1 = (player1, player2)
    team2 = (player3, player4)

    try:
        nprevious = m.loc[ (m.team1==team1) & (m.team2==team2) | ((m.team1==team2) & (m.team2==team1)), 'nmatches'].iloc[0]
    except IndexError:
        nprevious = 0

    chosen_team = df[((df.player1==player1) & (df.player2==player2)) | ((df.player1==player3) & (df.player2==player4))]
    match_imbalance = np.round(chosen_team.team_score.diff().iloc[1], 2)
    st.dataframe(chosen_team)
    st.write(f'Number of previous matches: {nprevious}')
    st.write(f'Match imbalance: {match_imbalance}\n\n')
else:
    st.write(':red[Duplicate player]')

avg_imbalance = np.round(np.nanmean(data[data<0].values), 2)
st.write(f'Average imbalance (score difference): {avg_imbalance}')
st.write('-'*80)
st.write('List of possible teams')
st.dataframe(df)
