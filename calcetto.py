import gspread
import streamlit as st
import pandas as pd

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
sh = gc.open("calcetto-test")


def _get_data(sh):
    return pd.DataFrame(sh.sheet1.get_values()[1:], columns=sh.sheet1.get_values()[0]).apply(pd.to_numeric)


def get_names(df):
    return sorted(df.columns.to_list())

st.set_page_config(page_title='Streamlit App', page_icon=':bar_chart:', layout='centered')
st.title('Calcetto neverending tournament ⚽')
# st.sidebar.title('')

tab1, tab2, tab3 = st.tabs(["// Input results //  ",  "// 📈 Data //  ", "  // First-time player //  "])

with tab1:
    st.title('Input results')
    st.subheader('Players')

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