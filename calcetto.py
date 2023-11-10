import gspread
import streamlit as st
import networkx as nx
import numpy as np
import pandas as pd
import platform
import plotly.express as px
from scipy.optimize import leastsq


if platform.system() == 'Windows':
    gc = gspread.service_account()
else:
    type = st.secrets['gcp_service_account']['type']
    project_id = st.secrets['gcp_service_account']['project_id']
    private_key_id = st.secrets['gcp_service_account']['private_key_id']
    private_key = st.secrets['gcp_service_account']['private_key']
    client_email = st.secrets['gcp_service_account']['client_email']
    client_id = st.secrets['gcp_service_account']['client_id']
    auth_uri = st.secrets['gcp_service_account']['auth_uri']
    token_uri = st.secrets['gcp_service_account']['token_uri']
    auth_provider_x509_cert_url = st.secrets['gcp_service_account']['auth_provider_x509_cert_url']
    client_x509_cert_url = st.secrets['gcp_service_account']['client_x509_cert_url']
    universe_domain = st.secrets['gcp_service_account']['universe_domain']

    creds = dict(
        type=type,
        project_id=project_id,
        private_key_id=private_key_id,
        private_key=private_key,
        client_email=client_email,
        client_id=client_id,
        auth_uri=auth_uri,
        token_uri=token_uri,
        auth_provider_x509_cert_url=auth_provider_x509_cert_url,
        client_x509_cert_url=client_x509_cert_url,
        universe_domain=universe_domain,
    )
    gc = gspread.service_account_from_dict(creds)

sh = gc.open("calcetto-app")


def _get_data(sh):
    return pd.DataFrame(sh.sheet1.get_values()[1:], columns=sh.sheet1.get_values()[0]).apply(pd.to_numeric)


def get_names(df):
    return sorted(df.columns.to_list())


def _error(x, scores, participation_matrix):
    return scores - np.dot(participation_matrix,x)


def get_centrality(data):
    df = data.copy()
    df = np.sign(np.abs(df))
    df = df.dropna(how='all', axis=1)

    l = []
    for col in df.columns:
        _df = df.groupby(col).sum().reset_index()
        sorted_cols = sorted(_df.columns)
        _df = _df[sorted_cols]
        _df.index = [col]
        l.append(_df)
    m = pd.concat(l)
    m.sort_index(inplace=True)

    for col in m.columns:
        m.loc[col, col] = 0

    G = nx.from_pandas_adjacency(m)
    weights = [G[u][v]['weight'] for u, v in G.edges()]
    bcent = nx.betweenness_centrality(G, weight='weight')
    bcent_df = pd.DataFrame({'Player': bcent.keys(), 'Centrality': bcent.values()})
    return bcent_df


st.set_page_config(page_title='Streamlit App', page_icon=':bar_chart:', layout='centered')
st.title('Calcetto never-ending tournament ⚽')

tab1, tab2, tab3 = st.tabs(["// Enter results //  ",  "// 📈 Data //  ", "  // Insert new players //  "])

with tab1:
    st.title('Enter results')

    df = _get_data(sh)
    names = ['---'] + get_names(df)

    form = st.form(key='form', clear_on_submit=True)
    with form:

        col1, col2 = st.columns(2)
        with col1:
            st.header('Team 1')
            player1 = st.selectbox('Player 1', names)
            player2 = st.selectbox('Player 2', names)
        with col2:
            st.header('Team 2')
            player3 = st.selectbox('Player 3', names)
            player4 = st.selectbox('Player 4', names)

        st.subheader('Score')
        # score = st.slider('', min_value=-10, max_value=10, step=1, value=0)
        score_str = st.select_slider('Final score', options=[str(f'10:{x}') for x in range(10)] + ['10:10'] + [str(f'{x}:10') for x in range(9,-1,-1)],
                                     value='10:10',
                                     label_visibility='hidden')
        t1, t2 = score_str.split(':')
        score = int(t1) - int(t2)

        players = [player1, player2, player3, player4]

        # No action if inputs are not OK
        # if score == 0 or '---' in players or len(set(players))<4:
        #     disabled = True
        # else:
        #     disabled = False
        #     if score < 0:
        #         st.write(f'Team 2 wins over Team 1 by {score}')
        #     if score > 0:
        #         st.write(f'Team 1 wins over Team 2 by {score}')
        # st.form_submit_button('Submit')
        # If inputs are OK, button is activated
    if score_str == '10:10':
       disabled = True
    st.write(score_str)
    if form.form_submit_button('Submit', 'submit-results', disabled=disabled):
        st.write(f'You selected players {player1}, {player2}, {player3}, and {player4}.')

        new_match = pd.DataFrame(columns=sh.sheet1.get_values()[0])
        new_match.loc[0, player1] = score
        new_match.loc[0, player2] = score
        new_match.loc[0, player3] = -score
        new_match.loc[0, player4] = -score

        df = pd.concat([df, new_match], axis=0)
        df = df.fillna('').apply(lambda x: x.astype(str))
        sh.sheet1.update([df.columns.values.tolist()] + df.values.tolist())

        st.write('Data updated!')


        def clear_form():
            st.session_state["Player 1"] = "---"
            st.session_state["bar"] = ""

    st.write("\n\n\n\n\n\n\nWant to make a correction? Have ideas and suggestions? Drop a line to francesco.granella@eiee.org")

with tab2:
    st.title('📈 Data')
    df = _get_data(sh)

    participation_matrix = np.sign(df).fillna(0)
    scores = df.max(axis=1)
    initial_estimate = np.zeros(df.shape[1])
    added_value, _ = leastsq(_error, initial_estimate, args=(scores, participation_matrix))
    added_value = (added_value - added_value.min()) / (added_value.max() - added_value.min()) * 10
    added_value = pd.DataFrame(added_value, index=df.columns, columns=['added_value']).round(3)

    avg_score = df.mean().to_frame().rename(columns={0:'avg_score'})

    _df = pd.merge(avg_score, added_value, left_index=True, right_index=True, how='inner')\
        .sort_values(by='added_value', ascending=False)\
        .reset_index()\
        .rename(columns={'index':'Player', 'avg_score':'Avg. score', 'added_value':'Added value, 0 to 10*'})
    _df.index = _df.index + 1
    cent_df = get_centrality(df)
    _df = pd.merge(_df, cent_df, on='Player', how='left')
    st.dataframe(_df, width=1000)
    st.markdown('_$^*$Takes into consideration the composition of teams_. See Wiki for a definition of [centrality](https://en.wikipedia.org/wiki/Betweenness_centrality).')

    l = []
    for i, row in df.iterrows():
        _row = row.dropna()
        winning = _row[_row > 0].index.to_list()
        losing = _row[_row < 0].index.to_list()
        if len(winning)==1:
            winning += ['']
        if len(losing)==1:
            losing += ['']
        l.append(
            pd.DataFrame(winning + losing + [10,  int(10+_row.min())]).T
        )
    games = pd.concat(l, axis=0).dropna(axis=1)
    if len(games.columns) == 6:
        games.columns = ['Team 1', 'Team1', 'Team 2', 'Team2', 'Score 1', 'Score2']
    latest_games = games.iloc[-5:].reset_index(drop=True).sort_index(ascending=False).reset_index(drop=True)

    st.write('Latest games')
    st.dataframe(latest_games)

    _plot_df = pd.merge(df.count().to_frame(), df.mean().to_frame(), left_index=True, right_index=True).reset_index()
    _plot_df.columns = ['player', 'count', 'score']
    fig = px.scatter(_plot_df, x='count', y='score', hover_data='player', labels=dict(count='Number of matches', score='Avg. score'))
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")

with tab3:
    new_player_name = st.text_input('Enter your name here')
    new_player_company = st.text_input('Enter your company here')
    new_player = f'{new_player_name} ({new_player_company})'
    if st.button('Submit', 'submit-name'):
        df = _get_data(sh)
        registered_players = df.columns.to_list()

        if new_player in registered_players:
            st.markdown("⚠️ :red[This player or a namesake already exists in the database]")
            st.write("Couldn't insert the player")
        else:
            # update dataset
            df[new_player] = np.nan
            df = df.fillna('').apply(lambda x: x.astype(str))
            sh.sheet1.update([df.columns.values.tolist()] + df.values.tolist())
            st.write('Player succesfully inserted in the database! ⚽⚽⚽')

# Make tab name larger
css = '''
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:1.25rem;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)