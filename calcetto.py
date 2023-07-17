import gspread
import streamlit as st
import numpy as np
import pandas as pd
import platform
import plotly.express as px

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
    type = type,
    project_id = project_id,
    private_key_id = private_key_id,
    private_key = private_key,
    client_email = client_email,
    client_id = client_id,
    auth_uri = auth_uri,
    token_uri = token_uri,
    auth_provider_x509_cert_url = auth_provider_x509_cert_url,
    client_x509_cert_url = client_x509_cert_url,
    universe_domain = universe_domain,
    )
    gc = gspread.service_account_from_dict(creds)

sh = gc.open("calcetto-app")


def _get_data(sh):
    return pd.DataFrame(sh.sheet1.get_values()[1:], columns=sh.sheet1.get_values()[0]).apply(pd.to_numeric)


def get_names(df):
    return sorted(df.columns.to_list())


st.set_page_config(page_title='Streamlit App', page_icon=':bar_chart:', layout='centered')
st.title('Calcetto never-ending tournament ⚽')

tab1, tab2, tab3 = st.tabs(["// Input results //  ",  "// 📈 Data //  ", "  // Insert new players //  "])

with tab1:
    st.title('Input results')

    df = _get_data(sh)
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

    st.subheader('Score for *Team 1*')
    score = st.slider('', min_value=-10, max_value=10, step=1, value=0)
    if score < 0:
        st.write(f'Team 2 wins over Team 1 by {score}')
    if score > 0:
        st.write(f'Team 1 wins over Team 2 by {score}')

    if st.button('Submit', 'submit-results'):
        st.write(f'You selected options {option1}, {option2}, {option3}, and {option4}.')

        new_match = pd.DataFrame(columns=sh.sheet1.get_values()[0])
        new_match.loc[0, 'Francesco G'] = 0
        new_match.loc[0, 'Matteo C'] = 0

        df = pd.concat([df, new_match], axis=0)
        df = df.fillna('').apply(lambda x: x.astype(str))
        sh.sheet1.update([df.columns.values.tolist()] + df.values.tolist())

        st.write('Data updated!')

    st.write("\n\n\n\n\n\n\nWant to make a correction? Have ideas and suggestions? Drop a line to francesco.granella@eiee.org")

with tab2:
    st.title('📈 Data')
    df = _get_data(sh)
    _df = df.mean().sort_values(ascending=False).round(3).reset_index()
    _df.columns = ['Player', 'Avg. score']
    # _df = _df.append(pd.DataFrame([['',' '*100]], columns=['Player', 'Avg. score']), ignore_index=True)
    _df.index = _df.index + 1
    st.dataframe(_df, width=1000)

    _plot_df = pd.merge(df.count().to_frame(), df.mean().to_frame(), left_index=True, right_index=True)
    _plot_df.columns = ['Count', 'Avg. score']
    fig = px.scatter(_plot_df['Count'], _plot_df['Avg. score'])
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
    font-size:2rem;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)