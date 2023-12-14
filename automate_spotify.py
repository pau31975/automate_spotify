from datetime import datetime as dt
from datetime import timedelta as td
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random

def get_followed_artists_new_release(sp):

    all_followed_artists_new_release = {}
    followed_artists_result = sp.current_user_followed_artists(limit=50)
    finished_count = 0

    while len(followed_artists_result['artists']['items'])!=0:

        for artist in followed_artists_result['artists']['items']:

            # add new release
            new_release_list = []
            for album in sp.artist_albums(artist['id'], album_type="album,single,appears_on", limit=50, offset=0)['items']:

                try:
                    dt_release_date = dt.strptime(album['release_date'], "%Y-%m-%d")
                except:
                    continue

                if dt_release_date > dt.today() - td(days=7) and album['album_type']!='compilation':
                    new_release_list.append((album['name'], album['id'], album['release_date'], album['album_group'], album['album_type']))

            all_followed_artists_new_release[(artist['name'], artist['id'])] = new_release_list

            finished_count+=1
            print(f"finished: {finished_count}/{followed_artists_result['artists']['total']}")
        # if finished_count==50:
        #     break

        followed_artists_result = sp.current_user_followed_artists(limit=50, after=artist['id'])
    return all_followed_artists_new_release

def get_top_50_artists_new_release(sp):

    all_top_50_artists_new_release = {}
    top_50_artists_result = sp.current_user_top_artists(limit=50, offset=0, time_range='medium_term')
    finished_count = 0

    for artist in top_50_artists_result['items']:

        # add new release
        new_release_list = []
        for album in sp.artist_albums(artist['id'], album_type="album,single,appears_on", limit=50, offset=0)['items']:

            try:
                dt_release_date = dt.strptime(album['release_date'], "%Y-%m-%d")
            except:
                continue

            if dt_release_date > dt.today() - td(days=7) and album['album_type']!='compilation':
                new_release_list.append((album['name'], album['id'], album['release_date'], album['album_group'], album['album_type']))

        all_top_50_artists_new_release[(artist['name'], artist['id'])] = new_release_list

        finished_count+=1
        print(f"finished: {finished_count}/50")

    return all_top_50_artists_new_release

def get_all_prioritized_artists(sp):
    return_list = []

    for artist in sp.current_user_top_artists(limit=50, offset=0, time_range='short_term')['items']:
        return_list.append(artist['name'])

    for artist in sp.current_user_top_artists(limit=50, offset=0, time_range='medium_term')['items']:
        if artist['name'] not in return_list:
            return_list.append(artist['name'])

    for artist in sp.current_user_top_artists(limit=50, offset=0, time_range='long_term')['items']:
        if artist['name'] not in return_list:
            return_list.append(artist['name'])
        
    return return_list

def list_songs_to_add_from_album(sp, album_id):
    id_list=[]
    pop_dict={}
    return_list=[]
    
    exclude_words = [
        'anniversary',
        'remix',
        'mix',
        'remaster',
        'version',
        'edition',
        'deluxe'
    ]
    
    # remove excluded words in albums
    for word in exclude_words:
        if word in sp.album(album_id)['name'].lower():
            return []
    
    # get tracks from album
    for track in sp.album_tracks(album_id, limit=50, offset=0)['items']:
          id_list.append(track['id'])    
        
    # get popularity from album tracks
    for track in sp.tracks(tracks=id_list)['tracks']:
        
        artist_list = []
        for artist in track['artists']:
            artist_list.append(artist['name'])
        
        pop_dict[(track['name'], track['uri'], tuple(artist_list), track['album']['album_type'])] = track['popularity']

    pop_dict = sorted(pop_dict.items(), key=lambda x: x[1], reverse=True)
    

    if len(pop_dict)<3:
        for track in pop_dict:
            return_list.append(track[0])
    else:
        for track in pop_dict[:3]:
            return_list.append(track[0])
            
    # remove unwanted alternate versions of singles
    if return_list[0][3] == 'single':
        return_list = [return_list[0]]
        
    # remove excluded words in songs
    return_list_copy=return_list.copy()
    for song in return_list_copy:
        for word in exclude_words:
            if word in song[0].lower():
                try:
                    return_list.remove(song)
                except:
                    continue
    
    return return_list

def add_new_release_to_playlist(sp, playlist_id, add_to_playlist_list, pos):
    sp.playlist_add_items(playlist_id, add_to_playlist_list, position=pos)
    for i in add_to_playlist_list:
        req = sp.track(i)
        print(f"Adding: {req['name']} - {req['artists'][0]['name']}")

def delete_all_in_new_release_playlist(sp, user_id, playlist_id):
    remove_list = []
    
    # check if the playlist is empty
    if sp.user_playlist_tracks(user_id, playlist_id, fields=None, limit=100, offset=0)['total'] == 0:
        return
    
    for track in sp.user_playlist_tracks(user_id, playlist_id, fields=None, limit=100, offset=0)['items']:
        remove_list.append(track['track']['id'])
    sp.user_playlist_remove_all_occurrences_of_tracks(user_id, playlist_id, tracks=remove_list, snapshot_id=None)

def add_following_songs_and_clean(sp, playlist_id, add_to_playlist_list, len_add_to_playlist_list_prioritized):
    
    the_rest_num=50-len_add_to_playlist_list_prioritized
    print(f"following artists song total: {len(add_to_playlist_list)}")
    
    if the_rest_num > 0:
        if len(add_to_playlist_list) <= the_rest_num:
            add_new_release_to_playlist(sp, playlist_id, add_to_playlist_list, len_add_to_playlist_list_prioritized)
        else:
            add_new_release_to_playlist(sp, playlist_id, random.sample(add_to_playlist_list, k=the_rest_num), len_add_to_playlist_list_prioritized)


    playlist_result = sp.playlist_items(playlist_id, limit=100, offset=0, additional_types=('track', 'episode'))

    # delete duplicates
    song_to_remove = []
    all_songs_dict = {}
    for song in playlist_result['items']:

        song_display_name = f"{song['track']['artists'][0]['name']} - {song['track']['name']}"

        if song_display_name not in all_songs_dict:
            all_songs_dict[song_display_name] = [song['track']['id']]
        else:
            all_songs_dict[song_display_name].append(song['track']['id'])

    for unique_song in all_songs_dict:
        if len(all_songs_dict[unique_song]) > 1:
            song_to_remove+=all_songs_dict[unique_song][1:]
        else:
            continue

    sp.playlist_remove_all_occurrences_of_items(playlist_id, song_to_remove, snapshot_id=None)
    for i in song_to_remove:
        req = sp.track(i)
        print(f"Removing: {req['name']} - {req['artists'][0]['name']}")