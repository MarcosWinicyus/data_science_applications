from enum import unique
from altair.vegalite.v4.api import selection
from altair.vegalite.v4.schema.core import Header
import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def view():
    st.title('NFL Player Stats Exprorer')

    st.markdown(""""
    This app performs simple webscrapring of NFL player stats data!
    *  **Python libraries:** Base64, pandas, streamlit
    * **Data source:** [Basketball-reference.com](https://www.https://www.basketball-reference.com)
    """)

    st.sidebar.header('User input Features')
    selected_year = st.sidebar.selectbox('Year', list(reversed(range(1990,2021))))

    # Web scraping of NBA player stats
    # carregamento do cashe de dados já acessados para proporcionar um melhor carregamento
    @st.cache
    def load_data(year):
        url = "https://www.pro-football-reference.com/years/" + str(year) + "/rushing.htm"
        html = pd.read_html(url, header = 1)
        df = html[0]
        raw = df.drop(df[df.Age == 'Age'].index) # Deletes repeating headers in content
        raw = raw.fillna(0)
        playerstats = raw.drop(['Rk'], axis=1)
        return playerstats
    playerstats = load_data(selected_year)

    # Sidebar - Team selection
    sorted_unique_team = sorted(playerstats.Tm.unique())
    selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

    # Side Bar - Position selection
    unique_pos = ['RB','QB','WR','FB','TE']
    selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

    #filtering data 
    df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

    st.header('Display player Stats of Selected Team(s)')
    st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns.')
    st.dataframe(df_selected_team)

    # Download NBA player stats data

    def filedownload(df):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;dase64,{b64}" download= "playerstats.csv">Download CSV File</a>'
        return href

    st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

    #heatmap
    if st.button('Intercorrelation Heatmap'):
        st.header('Intercorrelation Matrix Heatmap')
        df_selected_team.to_csv('output.csv',index=False)
        df = pd.read_csv('output.csv')

        corr = df.corr()
        mask = np.zeros_like(corr)
        mask[np.triu_indices_from(mask)] = True
        with sns.axes_style("white"):
            f, ax = plt.subplots(figsize=(7,5))
            ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
        
        st.pyplot(f)

