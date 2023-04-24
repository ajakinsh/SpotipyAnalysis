import spotipy
import spotipy.oauth2 as oauth2
import lyricsgenius

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

# Get the top 50 tracks from the user's Spotify library
results = sp.current_user_saved_tracks(limit=50)
tracks = [item['track'] for item in results['items']]

# Define a function to get the lyrical diversity of a song
def get_lyrical_diversity(track):
    # Get the lyrics for the song from the Genius API
    song = genius.search_song(track['name'], track['artists'][0]['name'])
    if song is None:
        return None
    lyrics = song.lyrics
    # Calculate the lyrical diversity of the song
    words = lyrics.split()
    unique_words = set(words)
    return len(unique_words) / len(words)

# Calculate the average lyrical diversity of the 50 songs
total_lyrical_diversity = 0
count = 0
for track in tracks:
    lyrical_diversity = get_lyrical_diversity(track)
    if lyrical_diversity is not None:
        total_lyrical_diversity += lyrical_diversity
        count += 1
average_lyrical_diversity = total_lyrical_diversity / count

# Print the average lyrical diversity
print(f"The average lyrical diversity of the top 50 tracks in your library is {average_lyrical_diversity:.2f}")