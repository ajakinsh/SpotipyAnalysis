import re as regex
import spotipy
import spotipy.oauth2 as oauth2
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
sp = spotipy.Spotify(client_credentials_manager=credentials)

# Create a Genius API instance; Timeout increased to 20 seconds from default 5 sec (too short)
genius = lyricsgenius.Genius(GENIUS_CLIENT_ACCESS_TOKEN, timeout=20)

# Define a function to get the lexical diversity of a song
def get_song_lexical_diversity(song_title, artist_name):
    try:
        # Get the lyrics for the song from the Genius API
        song = genius.search_song(song_title, artist_name)
        lyrics = song.lyrics
        blob = TextBlob(lyrics)
        language = detect(lyrics)
        if language != "en":
            blob = blob.translate(from_lang=language, to="en")
            lyrics = str(blob)

        print("LYRICS BEFORE PROCESSING:\n", lyrics)

        lyrics = lyrics.splitlines()[1:]  # skip the first line (song and contributor info)
        lyrics = "\n".join(lyrics) # put back into string

        # Define a regular expression to match bracketed text that genius puts in lyrics
        # For example the label of [Chorus] or [Pre-Chorus]
        bracketed_text_re = r'\[.*?\]'
        # Remove the bracketed text from the lyrics by replacing with empty string
        lyrics = regex.sub(bracketed_text_re, '', lyrics)

        # Calculate the lexical diversity of the song
        words = lyrics.split()
        unique_words = set(words)
        print("LYRICS AFTER PROCESSING:\n", lyrics)

        print("Unique words: ", unique_words)

        lexical_diversity = len(unique_words) / len(words)

        print(f"Lexical diversity of {song_title} by {artist_name}:")
        print(f"{len(unique_words)} unique words / {len(words)} total words = {lexical_diversity}")
        return lexical_diversity
    except:
        return None

get_song_lexical_diversity("Deify", "Disturbed")