# import random
# import time
import pandas as pd
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
    tracks = spotify.playlist_tracks(playlist_id)
    for track in tracks['items']:
        track_name = track['track']['name']
        track_id = track['track']['id']
        artist_name = track['track']['artists'][0]['name']
        audio_features = spotify.audio_features([track_id])[0]
        print(f"Adding {track_name} by {artist_name}")
        playlist_data.append({
                    'playlist_id': playlist_id,
                    'track_name': track_name,
                    'artist_name': artist_name,
                    'audio_features': audio_features
                })
    print(playlist_data)
    return pd.DataFrame(playlist_data)

top_2022 = "https://open.spotify.com/playlist/37i9dQZF1DX18jTM2l2fJY"
get_playlist_audio_features(top_2022)