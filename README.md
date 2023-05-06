# SpotipyAnalysis
Term Project for CIS 400 Social Media and Data Mining Course: Sentiment Analysis &amp; More Using Spotify API

This project uses the following python packages: regex, spotipy, spotipy_random, lyricsgenius, textblob, langdetect, and NLTK 

Download "requirements.txt" then run the command "pip install -r ./requirements.txt" to install these packages.

To use NLTK VADER, once the nltk package is installed, you may also need to run the command: "nltk.download('vader_lexicon')" or just "nltk.download()"

The project is broken into 4 main Python files. Each one has commented lines in the main that can be run.

SentimentAnalysis.py can perform this feature on songs and playlists using TextBlob. 

SentimentAnalyis_NLTK.py does the same using NLTK.

LyricalLexicalDiversity.py calculates the Lexical Diversity numbers for songs and playlists.

AudioFeatureAnalysis.py analyzes the Audio Features, obtained from Spotify for songs and averaged over playlists.
