import re as regex
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
def get_lyrics(song_name, artist_name, print_lyrics=False):
    song = genius.search_song(song_name, artist_name)
    if song is None:
        return None
    else:
        lyrics = song.lyrics
        if print_lyrics:
            print("\nLYRICS BEFORE PROCESSING:\n", lyrics)
        lyrics = lyrics.splitlines()[1:]  # skip the first line (song and contributor info)
        lyrics = "\n".join(lyrics) # put back into string

        # Define regular expressions to match odd text that genius puts in lyrics
        # Replace with empty string
        # If search fails, a numbered list of potential songs will be returned
        # These are not actual lyrics, so we must return None
        # For example the label of [Chorus] or [Intro]
        # Some odd lines like "270embed"
        # Or the following example ad insert:
        # # "see red hot chili peppers liveget tickets as low as $37you might also like"
        # Also remove parentheses and curly brackets
        # Substitute leftover single quotes for spaces

        numbered_list_regex = r'^\d+\. "\w+" - \w+'
        bracketed_text_regex = r'\[.*?\]'
        embed_regex = r'(?i)see\s+(.+?)\s+liveget tickets as low as \$(\d+)you might also like|\d+embed'
        parens_and_curly_brackets_regex = r'[\(\)\{\}]'
        standalone_quote_regex = r"\b ' \b|\b \" \b"
        if regex.search(numbered_list_regex, lyrics):
           return None
        lyrics = regex.sub(bracketed_text_regex, '', lyrics)
        lyrics = regex.sub(embed_regex, '', lyrics)
        lyrics = regex.sub(parens_and_curly_brackets_regex, '', lyrics)
        lyrics = regex.sub(standalone_quote_regex, ' ', lyrics)
        lyrics = lyrics.lower() # make all lowercase for more accurate sets
        if print_lyrics:
            print("\nLYRICS AFTER PROCESSING:\n", lyrics)
        return lyrics

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

def random_training_set(num_songs=1000):
    analyzed_count = 0
    sentiment_totals = [0, 0]
    error_count = 0
    for i in range(num_songs):
        print(f'Song {i+1}:')
        random_song_json: str = get_random(spotify, type="track")
        # extract the name of the song and the name of the artist from the dictionary
        song_name = random_song_json['name']
        artist_name = random_song_json['artists'][0]['name']

        try:
            sentiment = analyze_lyrics(song_name, artist_name)
            if sentiment is not None:
                sentiment_totals = (sentiment_totals[0] + sentiment.polarity, sentiment_totals[1] + sentiment.subjectivity)
            else:
                error_count += 1
        except:
            error_count += 1

    analyzed_count = num_songs - error_count
    if analyzed_count > 0:
        avg_sentiment_scores = [(sentiment_totals[0] / analyzed_count), (sentiment_totals[1] / analyzed_count)]
    else:
        sentiment_totals = [0, 0]

    avg_sentiment_scores = tuple(avg_sentiment_scores)
    print(f"Average sentiment (Polarity, Subjectivity) over {num_songs} random songs:\n {avg_sentiment_scores}")
    print(f"Number of errors: {error_count}")
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

def analyze_playlist_average(playlist_id, num_trials=10):
    polarity_sum = 0
    subjectivity_sum = 0
    for i in range(num_trials):
        print("Running analysis for trial", i+1)
        sentiment = analyze_playlist(playlist_id)
        polarity_sum += sentiment[0]
        subjectivity_sum += sentiment[1]
    average_polarity = polarity_sum / num_trials
    average_subjectivity = subjectivity_sum / num_trials
    print(f"Average Polarity over {num_trials} trials:", average_polarity)
    print(f"Average Subjectivity over {num_trials} trials:", average_subjectivity)

if __name__ == '__main__':
    # Playlist URL for global top songs of 2022
    top_2022 = "https://open.spotify.com/playlist/37i9dQZF1DX18jTM2l2fJY"
    kpop = "https://open.spotify.com/playlist/37i9dQZF1DX9Ja3hVYaZeE?si=7dx1SdAzQFuOPPHxdX2Utw&nd=1"
    jpop = "https://open.spotify.com/playlist/37i9dQZF1DXdbRLJPSmnyq"
    country = "https://open.spotify.com/playlist/37i9dQZF1DWZBCPUIUs2iR?si=yigwgjIMTWSzplH3lNd27A&nd=1"
    metal = "https://open.spotify.com/playlist/37i9dQZF1DX5FZ0gGkvIRf"
    rock = "https://open.spotify.com/playlist/37i9dQZF1DWXRqgorJj26U"

    # analyze_playlist_average(top_2022, 10)
    # analyze_playlist_average(kpop, 10)
    # analyze_playlist_average(jpop, 10)
    # analyze_playlist_average(country, 10)
    # analyze_playlist_average(metal, 10)
    analyze_playlist_average(rock, 10)

    # analyze_lyrics("We'll Be Coming Back", "Calvin Harris")

    # random_training_set(1000)