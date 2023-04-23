import random
import time
import spotipy
import spotipy.oauth2 as oauth2
from spotipy_random import get_random
import lyricsgenius
from textblob import TextBlob
from langdetect import detect
from nltk.sentiment.vader import SentimentIntensityAnalyzer

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
        return blob.sentiment
    except:
        return None

def random_training_set(num_trials):
    analyzed_count = 0
    for i in range(num_trials):

        random_pop_song_json: str = get_random(spotify, type="track")

        polarity_sum = 0
        subjectivity_sum = 0
        error_count = 0

        # extract the name of the song and the name of the artist from the dictionary
        song_name = random_pop_song_json['name']
        artist_name = random_pop_song_json['artists'][0]['name']

        try:
            sentiment = analyze_lyrics(song_name, artist_name)
            if sentiment is not None:
                polarity_sum += sentiment.polarity
                subjectivity_sum += sentiment.subjectivity
                analyzed_count += 1
            else:
                error_count += 1
        except:
            error_count += 1

        # print the song name and artist name
        print(f'Song {i+1}:')

    if analyzed_count > 0:
        average_polarity = polarity_sum / analyzed_count
        average_subjectivity = subjectivity_sum / analyzed_count
    else:
        average_polarity = 0
        average_subjectivity = 0

    print(f'Average Polarity over {num_trials} song test set:', average_polarity)
    print(f'Average Subjectivity over {num_trials} song test set:', average_subjectivity)
    print("Number of errors:", error_count)
    return (average_polarity, average_subjectivity)


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


# NLTK PART
def analyze_song_sentiment(song_title, artist_name):

    try:
        # Set up NLTK sentiment analyzer
        sid = SentimentIntensityAnalyzer()
        song = genius.search_song(song_title, artist_name)
        lyrics = song.lyrics
        blob = TextBlob(lyrics)
        language = detect(lyrics)
        if language != "en":
            blob = blob.translate(from_lang=language, to="en")
            lyrics = str(blob)

        # Perform sentiment analysis using NLTK
        sentiment_scores = sid.polarity_scores(lyrics)

        # Print results
        print(f"Song: {song_title} by {artist_name}")
        # print(f"Lyrics: {lyrics}")
        print(f"Sentiment Scores: {sentiment_scores}\n")
        return sentiment_scores
    except:
        return None


# # Example usage
# song_titles = ['Shape of You', 'Hello']
# artist_names = ['Ed Sheeran', 'Adele']


#analyze_song_sentiment(song_titles, artist_names)


def analyze_playlist_sentiment(playlist_id):
    # Get the tracks from the playlist
    results = spotify.playlist_items(playlist_id)
    tracks = results['items']
    song_titles = []
    artist_names = []
    sid = SentimentIntensityAnalyzer()
    # Extract the song titles and artist names
    for track in tracks:
        song_titles.append(track['track']['name'])
        artist_names.append(track['track']['artists'][0]['name'])

    # Analyze the sentiment of each song and keep track of positive and negative scores
    sentiment_totals = {'neg': 0, 'neu': 0, 'pos': 0, 'compound': 0}
    error_count = 0
    num_songs = len(song_titles)

    for track_name, track_artist in zip(song_titles, artist_names):
        try:
            sentiment_scores = analyze_song_sentiment(track_name, track_artist)
            if sentiment_scores is not None:
                for category in sentiment_scores:
                    sentiment_totals[category] += sentiment_scores[category]
            else:
                error_count += 1
        except:
            error_count += 1

    analyzed_count = num_songs - error_count
    if analyzed_count > 0:
        avg_sentiment_scores = {category: sentiment_totals[category] / analyzed_count for category in sentiment_totals}
    else:
        avg_sentiment_scores = {'neg': 0, 'neu': 0, 'pos': 0, 'compound': 0}
    # Print results
    print(f"Playlist: {playlist_id}")
    print(f"Number of songs analyzed: {analyzed_count}")
    # for category in avg_sentiment_scores:
    #     print(f"Average {category.capitalize()} Score: {avg_sentiment_scores[category]}")
    print("Average playlist sentiment:\n", avg_sentiment_scores)
    return avg_sentiment_scores

def analyze_playlist_average(playlist_id, num_trials):
    sentiment_totals = {'neg': 0, 'neu': 0, 'pos': 0, 'compound': 0}
    for i in range(num_trials):
        print("Running analysis for trial", i+1)
        sentiment = analyze_playlist_sentiment(playlist_id)
        for category in sentiment:
            sentiment_totals[category] += sentiment[category]
    avg_sentiment_scores = {category: sentiment_totals[category] / num_trials for category in sentiment_totals}
    print("Average playlist sentiment scores over", num_trials, "trials:")
    print(avg_sentiment_scores)
    return avg_sentiment_scores

top_2022 = "https://open.spotify.com/playlist/37i9dQZF1DX18jTM2l2fJY"
# analyze_playlist_sentiment(top_2022)

#average of the average
analyze_playlist_average(top_2022, 3)

#random training set (1000)