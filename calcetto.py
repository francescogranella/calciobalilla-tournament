# import pandas as pd
# import numpy as np
# import streamlit as st
#
# pd.set_option('display.max_rows', 50)
# pd.set_option('display.max_columns', 500)
# pd.set_option('display.width', 1000)
#
# cols = list('abcde')
# data = np.array([
#     [-1,-1,0,1,1],
#     [3,3,0,-3,-3],
#     [0,2,2,-2,-2]
# ])
#
# df = pd.DataFrame(data, columns=cols)
#
# def fetch_data():
#     data = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vTMY3vUGk6ghEpKPxcJ3usmyD6JPdLKvJNq6ELpGHMENcSp-Gy986Qyl2cP77Ad75SO3KAobPLsnWFc/pub?gid=0&single=true&output=csv', skiprows=3)
#     data.drop(columns=['Unnamed: 0', 'Validi'], inplace=True)
#     return data
#
#
# def get_all_possible_teams(players):
#     import itertools
#     return [sorted(x) for x in itertools.combinations(players, 2)]
#
#
# def get_all_possible_matches(players):
#     all_possible_teams = get_all_possible_teams(players)
#     all_possible_matches = [sorted(x) for x in itertools.combinations(all_possible_teams, 2) if len(set(itertools.chain(*x)))==4]
#     return all_possible_matches
#
# data = fetch_data()
# players = sorted(data.drop(columns='Esterni').columns.to_list())
# all_possible_teams = get_all_possible_teams(players)
# all_possible_teams = pd.DataFrame(all_possible_teams, columns=['player1', 'player2'])
# # all_possible_matches = pd.DataFrame(all_possible_matches, columns=['team1', 'team2'])
#
# score = data.drop(columns='Esterni').mean().reset_index().rename(columns={'index': 'player', 0: 'score'})
#
# # %% INterface
# player1 = st.selectbox(label='Player 1, Team 1', options=players)
# player2 = st.selectbox(label='Player 2, Team 1', options=players)
# player3 = st.selectbox(label='Player 1, Team 2', options=players)
# player4 = st.selectbox(label='Player 2, Team 2', options=players)
#
#
# # %%
# matches = []
# teams = []
# for i, row in data.iterrows():
#     winner = tuple(sorted(row[row>0].index.to_list()))
#     loser = tuple(sorted(row[row<0].index.to_list()))
#     match = tuple(sorted((winner, loser)))  # sorted so order of winner/loser doesn't matter
#     teams.append(winner)
#     teams.append(loser)
#     matches.append(match)
# t = {item:teams.count(item) for item in set(teams)}
# m = {item:matches.count(item) for item in set(matches)}
#
# t = pd.DataFrame(t, index=[0]).T.reset_index()
# t.columns = ['player1', 'player2', 'nmatches']
# m = pd.DataFrame(m, index=[0]).T.reset_index()
# m.columns = ['team1', 'team2', 'nmatches']
# t.sort_values('nmatches')
#
# df = pd.merge(all_possible_teams, t, how='outer').fillna(0)\
#     .merge(score.rename(columns={'player': 'player1', 'score': 'score1'}), on='player1')\
#     .merge(score.rename(columns={'player': 'player2', 'score': 'score2'}), on='player2')\
#     .assign(team_score=lambda x: (x.score1+x.score2/2))\
#     .assign(in_team_imbalance=lambda x: np.abs(x.score1 - x.score2))\
#     .sort_values(by=['nmatches', 'in_team_imbalance'], ascending=[True, True]).rename(columns={'score1': 'avg_score_player1', 'score2': 'avg_score_player2'})
#
# if player1 != player2 != player3 != player4:
#     player1, player2 = sorted((player1, player2))
#     player3, player4 = sorted((player3, player4))
#
#     team1 = (player1, player2)
#     team2 = (player3, player4)
#
#     try:
#         nprevious = m.loc[ (m.team1==team1) & (m.team2==team2) | ((m.team1==team2) & (m.team2==team1)), 'nmatches'].iloc[0]
#     except IndexError:
#         nprevious = 0
#
#     chosen_team = df[((df.player1==player1) & (df.player2==player2)) | ((df.player1==player3) & (df.player2==player4))].reset_index(drop=True)
#     match_imbalance = np.round(chosen_team.team_score.diff().iloc[1], 2)
#     st.dataframe(chosen_team)
#     st.write(f'Number of previous matches: {nprevious}')
#     st.write(f'Match imbalance: {match_imbalance}\n\n')
# else:
#     st.write(':red[Duplicate player]')
#
# avg_imbalance = np.round(np.nanmean(data[data<0].values), 2)
# st.write(f'Average imbalance (score difference): {avg_imbalance}')
# st.write('-'*80)
# st.write('List of possible teams')
# st.dataframe(df.reset_index(drop=True))
import gspread
import streamlit as st
import pandas as pd

gc = gspread.service_account()
sh = gc.open("calcetto-test")


def _get_data(sh):
    return pd.DataFrame(sh.sheet1.get_values()[1:], columns=sh.sheet1.get_values()[0]).apply(pd.to_numeric)


def get_names(df):
    return sorted(df.columns.to_list())

# def _connection_url():
#     url = 'https://drive.google.com/file/d/10nJ-42ia6Tojl_IAt9A-RClbDtZa0WuJ/view?usp=sharing'
#     file_id = url.split('/')[-2]
#     dwn_url = 'https://drive.google.com/uc?id=' + file_id
#     return dwn_url
#
# def _get_data():
#     dwn_url = _connection_url()
#     df = pd.read_csv(dwn_url)
#     return df
#
#
#
#
# def _write_data(df):
#     pass


st.set_page_config(page_title='Streamlit App', page_icon=':bar_chart:', layout='centered')
st.title('Calcetto neverending tournament ⚽')
# st.sidebar.title('')

tab1, tab2, tab3 = st.tabs(["// Input results //  ",  "// 📈 Data //  ", "  // First-time player //  "])

with tab1:
    st.title('Input results')
    st.subheader('Players')

    df = _get_data()
    names = ['---'] + get_names(df)

    col1, col2 = st.columns(2)
    with col1:
        st.header('Team 1')
        option1 = st.selectbox('Player 1', names)
        option2 = st.selectbox('Player 2', names)
    with col2:
        st.header('Team 2')
        option3 = st.selectbox('Player 3', names)
        option4 = st.selectbox('Player 4', names)

    st.subheader('Result')
    col1, col2 = st.columns(2)
    with col1:
        int1 = st.number_input('Team 1', value=0, min_value=-10, max_value=10, step=1)
    with col2:
        int2 = st.number_input('Team 2', value=-int1, min_value=-10, max_value=10, step=1)

    if int1 + int2 != 0:
        st.error('The sum of the two integers must be equal to zero.')

    if st.button('Submit', 'submit-results'):
        if int1 + int2 == 0:
            st.write(f'You selected options {option1}, {option2}, {option3}, and {option4}.')
            st.write(f'You entered integers {int1} and {int2}.')

            new_match = pd.DataFrame(columns=sh.sheet1.get_values()[0])
            new_match.loc[0, 'Francesco G'] = 0
            new_match.loc[0, 'Matteo C'] = 0

            df = pd.concat([df, new_match], axis=0)
            df = df.fillna('').apply(lambda x: x.astype(str))
            sh.sheet1.update([df.columns.values.tolist()] + df.values.tolist())

            st.write('Data updated!')
        else:
            st.error('The sum of the two integers must be equal to zero.')
    st.write("\n\n\n\n\n\n\nThink you've made a mistake? Drop a line to francesco.granella@eiee.org")

with tab2:
    st.title('📈 Data')
    df = _get_data()
    _df = df.mean().sort_values(ascending=False).round(3).reset_index()
    _df.columns = ['Player', 'Avg. score']
    # _df = _df.append(pd.DataFrame([['',' '*100]], columns=['Player', 'Avg. score']), ignore_index=True)
    st.dataframe(_df, width=1000)


with tab3:
    st.subheader('Enter your name here')
    text = st.text_area('')
    st.subheader('Enter your company here')
    # company = st.text_area('')
    if st.button('Submit', 'submit-name'):
        # update dataset
        st.write('Name succesfully inserted in the database!')

# Make tab name larger
css = '''
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:2rem;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)