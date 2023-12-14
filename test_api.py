from datetime import datetime as dt
from datetime import timedelta as td
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random

OAuth = SpotifyOAuth(
    client_id = os.environ.get("SPOTIFY_ID"),
    client_secret = os.environ.get("SPOTIFY_SECRET"),
    redirect_uri = "http://example.com",
    scope = ["user-follow-read",
             "user-top-read",
            "playlist-read-private",
            "playlist-modify-public",
            "playlist-modify-private"]
)

sp = spotipy.Spotify(auth_manager=OAuth)
print('login finished!')

user_id='galaxynotetheworld'
playlist_id='0yRBdBzOuFX6pQnF6szeeD'

print(type(sp.playlist_items(playlist_id, limit=100, offset=0, additional_types=('track', 'episode'))['total']))