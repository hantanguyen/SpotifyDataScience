import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go


client_credentials_manager = SpotifyClientCredentials(client_id="9774215a1cd446eab76c481665f994bf", client_secret="b67cc6e6c6ff43a1998d79584f88b703")
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

artist_name = []
track_name = []
track_popularity = []
artist_id = []
track_id = []
for i in range(0, 500, 50):
    track_results = sp.search(q='year:2022 ', type='track', limit=50, offset=i)
    for i, t in enumerate(track_results['tracks']['items']):
        artist_name.append(t['artists'][0]['name'])
        artist_id.append(t['artists'][0]['id'])
        track_name.append(t['name'])
        track_id.append(t['id'])
        track_popularity.append(t['popularity'])

track_df = pd.DataFrame({'artist_name': artist_name, 'track_name': track_name, 'track_id': track_id, 'track_popularity': track_popularity, 'artist_id': artist_id})
print(track_df.shape)
track_df.head()

artist_popularity = []
artist_genres = []
artist_followers = []
for a_id in track_df.artist_id:
    artist = sp.artist(a_id)
    artist_popularity.append(artist['popularity'])
    artist_genres.append(artist['genres'])
    artist_followers.append(artist['followers']['total'])

track_df = track_df.assign(artist_popularity=artist_popularity, artist_genres=artist_genres, artist_followers=artist_followers)
track_df.head()

track_features = []
for t_id in track_df['track_id']:
    af = sp.audio_features(t_id)
    track_features.append(af)

tf_df = pd.DataFrame(columns=['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'type', 'id', 'uri', 'track_href', 'analysis_url', 'duration_ms', 'time_signature'])
for item in track_features:
    for feat in item:
        tf_df = tf_df.append(feat, ignore_index=True)
tf_df.head()

track_df['artist_name'] = track_df['artist_name'].astype("string")
track_df['artist_followers'] = pd.to_numeric(track_df['artist_followers'])
track_df['track_name'] = track_df['track_name'].astype("string")
track_df['track_id'] = track_df['track_id'].astype("string")
track_df['artist_id'] = track_df['artist_id'].astype("string")
tf_df['duration_ms'] = pd.to_numeric(tf_df['duration_ms'])
tf_df['instrumentalness'] = pd.to_numeric(tf_df['instrumentalness'])
tf_df['time_signature'] = tf_df['time_signature'].astype("category")

# kyle's popularity function
by_popularity = pd.DataFrame(track_df.sort_values(by=['track_popularity'], ascending=False)[['artist_name', 'track_name']])
print(by_popularity.head(10))

def count_vowels(parameter):
    vowels = ['a', 'e', 'i', 'o', 'u']
    x = 0
    for char in parameter:
        if char in vowels:
            x = x + 1
    return x / len(parameter)

track_df["track_name"] = track_df["track_name"].apply(lambda x: count_vowels(x))

plot = track_df.plot(x='track_name', y='track_popularity', style='o')
plt.title("Popularity based on Vowels")
plt.show()

df_merge_difkey = pd.merge(track_df, tf_df, left_on='track_id', right_on='id')

plt.scatter(df_merge_difkey["track_popularity"], df_merge_difkey["danceability"], color="black")
plt.title("Track Popularity vs Track Dancability")
plt.xlabel("Popularity")
plt.ylabel("Dancability")
plt.show()

plt.title("Top 10 Genres")
artist_genres = [x for xs in artist_genres for x in xs]
artist_genres = pd.value_counts(artist_genres)
keys = artist_genres.keys()
value = artist_genres.values

plt.pie(value[0:10], labels=keys[0:10])
plt.axis('equal')
plt.show()
print("")

df_merge_difkey = pd.merge(track_df, tf_df, left_on='track_id', right_on='id')
artist_name = df_merge_difkey["artist_name"]
artist_name = pd.value_counts(artist_name)
keys = artist_name.keys()
value = artist_name.values
plt.title("Amount of Songs Per Artist in the Top 100")
plt.barh(keys[0:10], value[0:10])
plt.show()

# kyle's radial plot graph
track_pop = pd.DataFrame(track_df.sort_values(by=['track_popularity'], ascending=False)[['track_popularity','track_name'
                                                                                        , 'artist_name','artist_genres',
                                                                                          'track_id']])

# Dropping all Unnecessary Columns to Radial Plot
tf_df = tf_df.drop(columns=['key', 'mode', 'type', 'uri', 'track_href', 'analysis_url', 'duration_ms', 'time_signature',
                            'loudness', 'tempo'])

categories = tf_df.columns.tolist()
# Creating on Data Set to Display Features on Top 125 Songs
top_125_feat = pd.DataFrame(columns=categories)
for i, track in track_pop[:125].iterrows():
    features = tf_df[tf_df['id'] == track['track_id']]
    top_125_feat = top_125_feat.append(features, ignore_index=True)

# Splicing List and Taking 'id' category out so, it does not appear on plot
categories = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']

top_125_feat = top_125_feat[categories]

mean_values = pd.DataFrame(columns=categories)
mean_values = mean_values.append(top_125_feat.mean(), ignore_index=True)
mean_values = mean_values.append(tf_df[categories].mean(), ignore_index=True)

fig = go.Figure(
    data=[
        go.Scatterpolar(r=mean_values.iloc[0], theta=categories, fill='toself', name="Top 125"),
        go.Scatterpolar(r=mean_values.iloc[1], theta=categories, fill='toself', name="All Tracks"),
    ],
        layout=go.Layout(
        title=go.layout.Title(text='Comparison of Features'),
        polar={'radialaxis': {'visible': True}},
        showlegend=True
    )
)

fig.show()

# kyle's bar graph
artist_follow = pd.DataFrame(track_df.sort_values(by=['artist_followers'], ascending=False)[['artist_name','artist_followers']])
artist_follow.drop_duplicates(subset=['artist_name'], keep=False, inplace=True)
artist_follow.plot(x='artist_name', y='artist_followers', kind="bar", logy='sym')
plt.xlabel("Artists' Names", size=14)
plt.ylabel("Artist Followers (Natural Log)", size=14)
plt.title("Artist Popularity Based on Followers", size=18)
plt.xlim(-0.5, 10.5)
plt.show()
