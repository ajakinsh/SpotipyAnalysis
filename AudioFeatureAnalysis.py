# import random
# import time
import pandas as pd
import json
import spotipy
import spotipy.oauth2 as oauth2
# from spotipy_random import get_random
# import lyricsgenius
# from textblob import TextBlob
# from langdetect import detect

# Set up API credentials for Spotify and Genius
SPOTIFY_CLIENT_ID = '6695d089e5ac49379246228bcec06b2f'
SPOTIFY_CLIENT_SECRET = 'ba1da5124c8a47348d4fb3108940fa3e'
GENIUS_CLIENT_ACCESS_TOKEN = 'ViTixLIAigqJtrE4sBDgHRtiPReAnFLRy90Iq1U0WM5ahTifyA86ioflDGHzTP3_'

# Set up authentication for the Spotify API
credentials = oauth2.SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET)

# Create a Spotify API instance
spotify = spotipy.Spotify(client_credentials_manager=credentials)

# Create a Genius API instance; Timeout increased to 20 seconds from default 5 sec (too short)
# genius = lyricsgenius.Genius(GENIUS_CLIENT_ACCESS_TOKEN, timeout=20)

def get_playlist_audio_features(playlist_id):
    playlist_data = []
    sum_features = {}
    avg_features = {}

    tracks = spotify.playlist_tracks(playlist_id)
    for track in tracks['items']:
        track_name = track['track']['name']
        track_id = track['track']['id']
        artist_name = track['track']['artists'][0]['name']
        audio_features = spotify.audio_features([track_id])[0]
        numeric_audio_features = {}
        for key, value in audio_features.items():
            if isinstance(value, (int, float)):
                numeric_audio_features[key] = value
        print(f"Adding {track_name} by {artist_name}")
        playlist_data.append({
                    # 'playlist_id': playlist_id,
                    'track_name': track_name,
                    'artist_name': artist_name,
                    'audio_features': numeric_audio_features
                })

        for feature, value in numeric_audio_features.items():
            sum_features[feature] = sum_features.get(feature, 0) + value

    for feature, value in sum_features.items():
        avg_features[feature] = value / len(tracks['items'])

    print(pd.DataFrame(playlist_data))
    print("\n")
    print(json.dumps(avg_features))
    return avg_features

print("Starting...")
top_2022 = "https://open.spotify.com/playlist/37i9dQZF1DX18jTM2l2fJY"
get_playlist_audio_features(top_2022)