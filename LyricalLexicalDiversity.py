import re as regex
import spotipy
import spotipy.oauth2 as oauth2
import lyricsgenius
from textblob import TextBlob
from langdetect import detect
from collections import Counter

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

def get_lyrics(song_name, artist_name, print_lyrics=False):
    song = genius.search_song(song_name, artist_name)
    if song is None:
        return None
    else:
        lyrics = song.lyrics
        blob = TextBlob(lyrics)
        language = detect(lyrics)
        if language != "en":
            blob = blob.translate(from_lang=language, to="en")
            lyrics = str(blob)

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

# Define a function to get the lexical diversity of a song
def get_song_lexical_diversity(song_title, artist_name, most_common_count=20, print_words=True):
    try:
        lyrics = get_lyrics(song_title, artist_name, print_lyrics=print_words)

        # Split the lyrics into words
        words = lyrics.split()
        # Remove any punctuation from the beginning or end of each word
        words = [word.strip(",.;!?") for word in words]
        # Remove any empty words from the words list
        words = [word for word in words if word != ""]

        # Calculate the lexical diversity of the song
        unique_words = set(words)
        if print_words:
            print("\nUnique words: ", sorted(unique_words))
        lexical_diversity = len(unique_words) / len(words)

        # Count the frequency of each unique word and print the most commonly used words
        word_counts = Counter(words)
        most_common_words = word_counts.most_common(most_common_count)
        if print_words:
            print(f"\n{most_common_count} most common words in \"{song_title}\" by {artist_name}:\n")
            for word, count in most_common_words:
                print(f"{word}:\t\t{count}")

        print(f"\nLexical diversity of \"{song_title}\" by {artist_name}:")
        print(f"{len(unique_words)} unique words / {len(words)} total words = {lexical_diversity}\n")
        return lexical_diversity, unique_words
    except:
        return None

def get_playlist_lexical_diversity(playlist_id, most_common_count=20, print_words_each_song=False):
    tracks = spotify.playlist_tracks(playlist_id)
    track_names = [track['track']['name'] for track in tracks['items']]
    track_artists = [track['track']['artists'][0]['name'] for track in tracks['items']]

    # Get the lexical diversity for each track and calculate the average
    lexical_diversities = []
    all_words = []
    error_count = 0
    for track_name, track_artist in zip(track_names, track_artists):
        try:
            lexical_diversity, unique_words = get_song_lexical_diversity(track_name,
                                                                         track_artist,
                                                                         most_common_count=most_common_count,
                                                                         print_words=print_words_each_song)
            if lexical_diversity is not None:
                lexical_diversities.append(lexical_diversity)
                all_words += unique_words
            else:
                error_count += 1
        except:
            error_count += 1

    avg_lexical_diversity = sum(lexical_diversities) / len(lexical_diversities)

    # Get the most common words and their counts
    common_words = Counter(all_words).most_common(most_common_count)

    # Print the results
    print("Average lexical diversity for playlist:", avg_lexical_diversity)
    print(f"{most_common_count} most common words in the playlist:")
    for word, count in common_words:
        print(f"{word}\t\t{count}")
    print("Number of errors:", error_count)

    return avg_lexical_diversity, common_words

if __name__ == '__main__':
    # get_song_lexical_diversity("Clocks", "Coldplay", most_common_count=20, print_words=False)
    top_2022 = "https://open.spotify.com/playlist/37i9dQZF1DX18jTM2l2fJY"
    kpop = "https://open.spotify.com/playlist/37i9dQZF1DX9Ja3hVYaZeE?si=7dx1SdAzQFuOPPHxdX2Utw&nd=1"
    jpop = "https://open.spotify.com/playlist/37i9dQZF1DXdbRLJPSmnyq"
    country = "https://open.spotify.com/playlist/37i9dQZF1DWZBCPUIUs2iR?si=yigwgjIMTWSzplH3lNd27A&nd=1"
    metal = "https://open.spotify.com/playlist/37i9dQZF1DX5FZ0gGkvIRf"
    rock = "https://open.spotify.com/playlist/37i9dQZF1DWXRqgorJj26U"


    # get_playlist_lexical_diversity(top_2022, most_common_count=30, print_words_each_song=False)
    # get_playlist_lexical_diversity(kpop, most_common_count=30, print_words_each_song=False)
    # get_playlist_lexical_diversity(jpop, most_common_count=30, print_words_each_song=False)
    # get_playlist_lexical_diversity(country, most_common_count=30, print_words_each_song=False)
    # get_playlist_lexical_diversity(metal, most_common_count=30, print_words_each_song=False)
    get_playlist_lexical_diversity(rock, most_common_count=30, print_words_each_song=False)

