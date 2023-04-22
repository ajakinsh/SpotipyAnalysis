def get_playlist_data(user_id, genre=None, min_popularity=None):
    playlist_data = []
    playlists = spotify.user_playlists(user_id)
    for playlist in playlists['items']:
        playlist_name = playlist['name']
        playlist_id = playlist['id']
        tracks = spotify.user_playlist_tracks(user_id, playlist_id)
        for track in tracks['items']:
            track_name = track['track']['name']
            track_id = track['track']['id']
            track_popularity = track['track']['popularity']
            artist_name = track['track']['artists'][0]['name']
            artist_id = track['track']['artists'][0]['id']
            audio_features = spotify.audio_features([track_id])[0]
            track_genre = audio_features['genres'][0] if 'genres' in audio_features else None
            if (not genre or track_genre == genre) and (not min_popularity or track_popularity >= min_popularity):
                playlist_data.append({
                    'playlist_name': playlist_name,
                    'playlist_id': playlist_id,
                    'track_name': track_name,
                    'track_id': track_id,
                    'track_popularity': track_popularity,
                    'artist_name': artist_name,
                    'artist_id': artist_id,
                    'track_genre': track_genre
                })
    return pd.DataFrame(playlist_data)

user_ids = ['spotify', 'user1', 'user2', 'user3']
for user_id in user_ids:
    playlist_data = get_playlist_data(user_id, genre='pop', min_popularity=50)
    print(f"Playlist data for user {user_id}:")
    print(playlist_data.head())


# Option 4: Perform musical network analysis to identify influential or popular nodes in the musical network

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import networkx as nx

scope = "user-library-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

# Get information about different artists, albums, or songs
# For example, you could get information about the top 50 tracks in a particular genre or musical era
genre = "INSERT_GENRE_HERE"
results = sp.search(q='genre:"{}"'.format(genre), type='track', limit=50)
tracks = results['tracks']['items']

# Build a graph based on social connections
G = nx.Graph()
for track in tracks:
    # Get the artists associated with the track
    artist_ids = [artist['id'] for artist in track['artists']]
    artist_names = [artist['name'] for artist in track['artists']]

    # Add nodes for the artists if they don't already exist
    for i in range(len(artist_ids)):
        if not G.has_node(artist_ids[i]):
            G.add_node(artist_ids[i], name=artist_names[i])

    # Add edges between the artists based on their collaborations on the track
    for i in range(len(artist_ids)):
        for j in range(i + 1, len(artist_ids)):
            if not G.has_edge(artist_ids[i], artist_ids[j]):
                G.add_edge(artist_ids[i], artist_ids[j], weight=1)
            else:
                G[artist_ids[i]][artist_ids[j]]['weight'] += 1

# Perform network analysis on the graph
# For example, you could calculate the centrality of each node and plot the graph
centrality = nx.degree_centrality(G)
nx.draw(G, with_labels=True, font_weight='bold')
plt.show()

