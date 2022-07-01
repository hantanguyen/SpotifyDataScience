

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id="5c2ff10a7a374881a03eaf571eacfba4", client_secret="1dd884442eea467996efd90d524772fd")
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

artist_name = []
track_name = []
track_popularity = []
artist_id = []
track_id = []
for i in range(0, 1000, 50):
    track_results = sp.search(q='year:2021', type='track', limit=50,offset=i)
    for i, t in enumerate(track_results['tracks']['items']):
        artist_name.append(t['artists'][0]['name'])
        artist_id.append(t['artists'][0]['id'])
        track_name.append(t['name'])
        track_id.append(t['id'])
        track_popularity.append(t['popularity'])

track_df = pd.DataFrame({'artist_name' : artist_name, 'track_name' : track_name, 'track_id' : track_id, 'track_popularity' : track_popularity, 'artist_id' : artist_id})
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
track_df = track_df.sort_values(by="artist_popularity", ascending=False)
row5 = track_df.head(5)
print(row5)

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
track_df['track_name'] = track_df['track_name'].astype("string")
track_df['track_id'] = track_df['track_id'].astype("string")
track_df['artist_id'] = track_df['artist_id'].astype("string")
tf_df['duration_ms'] = pd.to_numeric(tf_df['duration_ms'])
tf_df['instrumentalness'] = pd.to_numeric(tf_df['instrumentalness'])
tf_df['time_signature'] = tf_df['time_signature'].astype("category")
print(track_df.info())
print(tf_df.info())

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

plt.pie(value[0:10],labels=keys[0:10])
plt.axis('equal')
plt.show()
print("")

# placeholder for pie chart
# here we could include 5-8 different music genres (rock, kpop, classical, pop...etc)
# labels = []
# # (does every "50" account for each pie slice?) not sure here
# sizes = [50,50,50]
# # same here
# plt.pie(sizes,labels=labels,explode=(0.1,0.1,0.1))
# # (this sets a proper axis)
# plt.axis('equal')
# # displays the pie chart
# plt.show()

df_merge_difkey = pd.merge(track_df, tf_df, left_on='track_id', right_on='id')
artist_name = df_merge_difkey["artist_name"]
artist_name = pd.value_counts(artist_name)
keys = artist_name.keys()
value = artist_name.values
plt.title("Amount of Songs Per Artist in the Top 100")
plt.barh(keys[0:10], value[0:10])
plt.show()

# # this option is for a scatterplot, we can either do artists popularity over time or genre popularity over time
# plt.scatter(iris["length"], iris["width"], color = "blue")
# plt.title("Scatter Plot")
# plt.xlabel("length")
# plt.ylabel("width")
# plt.show

# i also do want the pokemon looking graph too, i just have no idea what it is called

#feature_labels = list

# kyle's graph
track_df.drop_duplicates(subset=['artist_name'], keep=False, inplace=True)
track_df.sort_values(by=['artist_followers'], ascending=False)
track_df.plot(x='artist_name', y='artist_followers', kind="bar", logy='sym')
plt.ylabel("Artist Followers (Natural Log)", size=15)
plt.title("Artist Popularity Based on Followers", size=18)
plt.show()
