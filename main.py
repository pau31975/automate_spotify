from datetime import datetime as dt
from datetime import timedelta as td
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
from automate_spotify import *



if __name__ == "__main__":

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
    user_id='galaxynotetheworld'
    playlist_id='0yRBdBzOuFX6pQnF6szeeD'
    
    delete_all_in_new_release_playlist(sp, user_id, playlist_id)
    
    # get all songs to add, consider appears_on
    all_songs_to_add=[]
    new_release_albums = get_followed_artists_new_release(sp)
    for artist in new_release_albums:
        for album in new_release_albums[artist]:
            artist_name = artist[0]
            album_id = album[1]
            album_group = album[3]
            album_type = album[4]

            if album_type == "appears_on":
                for appears_on_track in sp.album_tracks(album_id, offset=0)['items']:
                    for appears_on_artist in appears_on_track['artists']:
                        if appears_on_artist['name']==artist_name:
                            to_add = (appears_on_track['name'], appears_on_track['uri'],
                                      appears_on_track['artists'], track['album']['album_type'])
                            all_songs_to_add.apppend(to_add)
            else:
                list_songs_to_add = []
                x_list = list_songs_to_add_from_album(sp, album_id)
                for song in x_list:
                    if artist_name in song[2]:
                        list_songs_to_add.append(song)

                all_songs_to_add+=list_songs_to_add

    # prioritize top50 artists
    all_prioritized_artists = get_all_prioritized_artists(sp)
    add_to_playlist_list_prioritized = []
    add_to_playlist_list = []
    for song in all_songs_to_add:
        if song[2] in all_prioritized_artists:
            add_to_playlist_list_prioritized.append(song[1])
        else:
            add_to_playlist_list.append(song[1])
    
    print(f"\nprioritized artists song total: {len(add_to_playlist_list_prioritized)}")
    if len(add_to_playlist_list_prioritized)!=0:
        add_new_release_to_playlist(sp, playlist_id, add_to_playlist_list_prioritized, 0)
    
    # add following song and clean data
    add_following_songs(sp, playlist_id, add_to_playlist_list, len(add_to_playlist_list_prioritized))
    clean_duplicates(sp, playlist_id)