import re as regex
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

def random_training_set(num_songs=1000):
    analyzed_count = 0
    sentiment_totals = {'neg': 0, 'neu': 0, 'pos': 0, 'compound': 0}
    error_count = 0

    for i in range(num_songs):
        print(f'Song {i+1}:')
        random_pop_song_json: str = get_random(spotify, type="track")

        # extract the name of the song and the name of the artist from the dictionary
        song_name = random_pop_song_json['name']
        artist_name = random_pop_song_json['artists'][0]['name']

        try:
            sentiment = analyze_song_sentiment(song_name, artist_name)
            if sentiment is not None:
                for category in sentiment_totals:
                    sentiment_totals[category] += sentiment[category]
            else:
                error_count += 1
        except:
            error_count += 1


    analyzed_count = num_songs - error_count
    if analyzed_count > 0:
        avg_sentiment_scores = {category: sentiment_totals[category] / analyzed_count for category in sentiment_totals}
    else:
        avg_sentiment_scores = {'neg': 0, 'neu': 0, 'pos': 0, 'compound': 0}

    print(f"Average sentiment over {num_songs} random songs:\n {avg_sentiment_scores}")
    return avg_sentiment_scores

def analyze_song_sentiment(song_title, artist_name):
    try:
        # Set up NLTK sentiment analyzer
        sid = SentimentIntensityAnalyzer()
        lyrics = get_lyrics(song_title, artist_name)
        blob = TextBlob(lyrics)
        language = detect(lyrics)
        if language != "en":
            blob = blob.translate(from_lang=language, to="en")
            lyrics = str(blob)

        # Perform sentiment analysis using NLTK
        sentiment_scores = sid.polarity_scores(lyrics)

        # Print results
        print(f"Song: \"{song_title}\" by {artist_name}")
        # print(f"Lyrics: {lyrics}")
        print(f"Sentiment Scores: {sentiment_scores}\n")
        return sentiment_scores
    except:
        return None


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
    print(f"Average playlist sentiment:\n {avg_sentiment_scores}")
    return avg_sentiment_scores

def analyze_playlist_average(playlist_id, num_trials=10):
    sentiment_totals = {'neg': 0, 'neu': 0, 'pos': 0, 'compound': 0}
    for i in range(num_trials):
        print("Running analysis for trial", i+1)
        sentiment = analyze_playlist_sentiment(playlist_id)
        for category in sentiment:
            sentiment_totals[category] += sentiment[category]
    avg_sentiment_scores = {category: sentiment_totals[category] / num_trials for category in sentiment_totals}
    print(f"\nAverage playlist sentiment scores over {num_trials} trials:\n {avg_sentiment_scores}")
    return avg_sentiment_scores

if __name__ == '__main__':
    top_2022 = "https://open.spotify.com/playlist/37i9dQZF1DX18jTM2l2fJY"
    kpop = "https://open.spotify.com/playlist/37i9dQZF1DX9Ja3hVYaZeE?si=7dx1SdAzQFuOPPHxdX2Utw&nd=1"
    jpop = "https://open.spotify.com/playlist/37i9dQZF1DXdbRLJPSmnyq"
    country = "https://open.spotify.com/playlist/37i9dQZF1DWZBCPUIUs2iR?si=yigwgjIMTWSzplH3lNd27A&nd=1"
    metal = "https://open.spotify.com/playlist/37i9dQZF1DX5FZ0gGkvIRf"
    rock = "https://open.spotify.com/playlist/37i9dQZF1DWXRqgorJj26U"

    # analyze_song_sentiment("Uptown Girl", "Billy Joel")
    # analyze_playlist_sentiment(top_2022)

    # average of the average
    # analyze_playlist_average(top_2022)
    # analyze_playlist_average(kpop)
    # analyze_playlist_average(jpop)
    # analyze_playlist_average(country)
    # analyze_playlist_average(metal)
    analyze_playlist_average(rock)

    # random_training_set(1000)