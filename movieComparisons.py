import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

#Dataset Filter System
@st.cache  #
def loadData(chosenYear, chosenMonth, chosenLang):
  url = "https://raw.githubusercontent.com/samgitmaster/CSC310/main/mymoviedb.csv"
  df = pd.read_csv(url, lineterminator='\n')
  df['Year'] = pd.DatetimeIndex(df['Release_Date']).year
  df['Month'] = pd.DatetimeIndex(df['Release_Date']).month
  df = df.drop(columns = ['Poster_Url'])
  df2 = df[df['Year'] == chosenYear]
  df3 = df2[df2['Month'] == chosenMonth]
  df4 = df3[df3['Original_Language'] == chosenLang]
  return df4
@st.cache  #
def loadRecData():
    url = "https://raw.githubusercontent.com/samgitmaster/CSC310/main/mymoviedb.csv"
    dfR = pd.read_csv(url, lineterminator='\n')

    tfidf = TfidfVectorizer(stop_words='english')

    dfR['Overview'] = dfR['Overview'].fillna('')

    tfidf_matrix = tfidf.fit_transform(dfR['Overview'])

    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    indices = pd.Series(dfR.index, index=dfR['Title']).drop_duplicates()
    return dfR, cosine_sim, indices

dfR, cosine_sim, indices = loadRecData()
@st.cache  #
def get_recommendations(title, cosine_sim=cosine_sim):
    try:
        # Get the index of the movie that matches the title
        idx = indices[title]

        # Get the pairwsie similarity scores of all movies with that movie
        sim_scores = list(enumerate(cosine_sim[idx]))
            
        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the scores of the 10 most similar movies
        sim_scores = sim_scores[1:11]

        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]

        # Return the top 10 most similar movies
        return dfR['Title'].iloc[movie_indices]
    except:
        return -1



st.title('Movie Comparison')

st.subheader("This app allows you to filter a movie dataset by year, month, and language.")
st.subheader("It also has a movie recommendation system.")
st.subheader("It displays movie ratings by vote average. The 43 most common movie languages have been provided.")
st.markdown("**For best results, use en(English) or ja(Japanese)**")

st.sidebar.header('Movies Filter')

chosenYear = st.sidebar.selectbox('Year', list(reversed(range(1970, 2023))))
chosenMonth = st.sidebar.selectbox('Month', list(range(1, 13)))
uniqueLang = ['en', 'ja', 'fr', 'hi', 'es', 'ru', 'de', 'th', 'ko', 'tr', 'cn',
       'zh', 'it', 'pt', 'ml', 'pl', 'fi', 'no', 'da', 'id', 'sv', 'nl',
       'te', 'sr', 'is', 'ro', 'tl', 'fa', 'uk', 'nb', 'eu', 'lv', 'ar',
       'el', 'cs', 'ms', 'bn', 'ca', 'la', 'ta', 'hu', 'he', 'et']
chosenLang = st.sidebar.selectbox('Language', uniqueLang)

df = loadData(chosenYear, chosenMonth, chosenLang)

st.dataframe(df)

chosenMovie = st.sidebar.selectbox('Find Recommendations', list(df['Title']))


moviesByAverage = (
    df.groupby(by=['Title']).sum()[['Vote_Average']].sort_values('Vote_Average', ascending=True)
)

figVoteAvg = px.bar(
    moviesByAverage,
    x="Vote_Average",
    y=moviesByAverage.index,
    orientation = "h",
    title = "<b>Movies By Vote Average Score</b>",
    color_discrete_sequence = ["#0083B8"] * len(moviesByAverage),
    template = "plotly_white",
)

st.plotly_chart(figVoteAvg)

st.write(f'Recommended Movies for **{chosenMovie}**')
st.markdown('***Note: Some movies may not form recommended list***')

try:
    recommended = list(get_recommendations(chosenMovie))
    for i in range(len(recommended)):
        st.write(recommended[i])
        st.text('')
except:
    st.error('The movie you chose is not available for listing - choose again...')
    st.stop()
