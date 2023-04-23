import random
import time
import spotipy
import spotipy.oauth2 as oauth2
from spotipy_random import get_random
import lyricsgenius
from textblob import TextBlob
from langdetect import detect


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
genius = lyricsgenius.Genius(GENIUS_CLIENT_ACCESS_TOKEN, timeout=20)

# Define a function to retrieve song lyrics from Genius
def get_lyrics(song_name, artist_name):
    song = genius.search_song(song_name, artist_name)
    if song is None:
        return None
    else:
        return song.lyrics

# Perform sentiment analysis on song lyrics
def analyze_lyrics(song_name, artist_name):
    try:
        lyrics = get_lyrics(song_name, artist_name)
        blob = TextBlob(lyrics)
        language = detect(lyrics)
        if language != "en":
            blob = blob.translate(from_lang=language, to="en")
        print(blob.sentiment)
        return blob.sentiment
    except:
        return None

def random_training_set(num_trials):
    analyzed_count = 0
    sentiment_totals = [0, 0]
    error_count = 0
    for i in range(num_trials):
        print(f'Song {i+1}:')
        random_pop_song_json: str = get_random(spotify, type="track")
        # extract the name of the song and the name of the artist from the dictionary
        song_name = random_pop_song_json['name']
        artist_name = random_pop_song_json['artists'][0]['name']

        try:
            sentiment = analyze_lyrics(song_name, artist_name)
            if sentiment is not None:
                sentiment_totals = (sentiment_totals[0] + sentiment.polarity, sentiment_totals[1] + sentiment.subjectivity)
            else:
                error_count += 1
        except:
            error_count += 1

    analyzed_count = num_trials - error_count
    if analyzed_count > 0:
        avg_sentiment_scores = [(sentiment_totals[0] / analyzed_count), (sentiment_totals[1] / analyzed_count)]
    else:
        sentiment_totals = [0, 0]

    avg_sentiment_scores = tuple(avg_sentiment_scores)
    print("Average sentiment (Polarity, Subjectivity):" , avg_sentiment_scores)
    print("Number of errors:", error_count)
    return avg_sentiment_scores


def analyze_playlist(playlist_id):
    # Get playlist tracks
    tracks = spotify.playlist_tracks(playlist_id)
    # Extract track names
    track_names = [track['track']['name'] for track in tracks['items']]
    track_artists = [track['track']['artists'][0]['name'] for track in tracks['items']]

    # Perform sentiment analysis on track names
    polarity_sum = 0
    subjectivity_sum = 0
    error_count = 0
    for track_name, track_artist in zip(track_names, track_artists):
        try:
            sentiment = analyze_lyrics(track_name, track_artist)
            if sentiment is not None:
                polarity_sum += sentiment.polarity
                subjectivity_sum += sentiment.subjectivity
            else:
                error_count += 1
        except:
            error_count += 1

    # Compute average polarity and subjectivity
    analyzed_count = len(track_names) - error_count
    if analyzed_count > 0:
        average_polarity = polarity_sum / analyzed_count
        average_subjectivity = subjectivity_sum / analyzed_count
    else:
        average_polarity = 0
        average_subjectivity = 0

    print("Average Polarity:", average_polarity)
    print("Average Subjectivity:", average_subjectivity)
    print("Number of errors:", error_count)
    return (average_polarity, average_subjectivity)

def analyze_playlist_average(playlist_id, num_trials):
    polarity_sum = 0
    subjectivity_sum = 0
    for i in range(num_trials):
        print("Running analysis for trial", i+1)
        sentiment = analyze_playlist(playlist_id)
        polarity_sum += sentiment[0]
        subjectivity_sum += sentiment[1]
    average_polarity = polarity_sum / num_trials
    average_subjectivity = subjectivity_sum / num_trials
    print("Average Polarity over 50 trials:", average_polarity)
    print("Average Subjectivity over 50 trials:", average_subjectivity)

# Playlist URL for global top songs of 2022
# top_2022 = "https://open.spotify.com/playlist/37i9dQZF1DX18jTM2l2fJY"
# # analyze_playlist_average(top_2022, 50)
# analyze_playlist(top_2022)

# sent = analyze_lyrics("We'll Be Coming Back", "Calvin Harris")
# print(sent)

random_training_set(1000)