import requests
from bs4 import BeautifulSoup
from spotipy import Spotify
from spotipy import SpotifyOAuth
from pprint import pprint
from dotenv import load_dotenv
import os

load_dotenv()
client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')

Date = input("Enter the date you want to listen the music from (YYYY-MM-DD): ")
URL = f'https://www.billboard.com/charts/hot-100/{Date}/'

#-----------------Getting top 100 billboard songs-------------------------------
response = requests.get(url=URL)
Website = response.text

soup = BeautifulSoup(Website, 'html.parser')

song_list = soup.find_all(name = 'li', class_ = 'o-chart-results-list__item // lrv-u-flex-grow-1 lrv-u-flex lrv-u-flex-direction-column lrv-u-justify-content-center lrv-u-border-b-1 u-border-b-0@mobile-max lrv-u-border-color-grey-light lrv-u-padding-l-050 lrv-u-padding-l-1@mobile-max')
song_title = [song.find(name = 'h3').getText().replace('\n', ' ').replace('\t', '').strip() for song in song_list]
print(song_title)

#------------Setting up the Spotify APP----------------------------------------
spot = Spotify(auth_manager=(
    SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        scope='playlist-modify-private playlist-read-private',
        redirect_uri='http://localhost:8080',
        cache_path='tocken.txt'
        )
))

#Creating the URI for songs extracted from billboard
URI = []
for song in song_title:
    uri = spot.search(q=f'track: {song} year: {Date.split("-")[0]}',type='track')
    uri_link = uri['tracks']['items'][0]['uri']
    URI.append(uri_link)


#Checking if same anme playlist exists or not
playlist_name_list = spot.current_user_playlists()
playlists = [name['name'] for name in playlist_name_list['items']]
playlist_name = f'{Date} Billboard 100'   

if playlist_name in playlists:
    print('Playlist already exists') 
else:
    id_ = spot.me()['id']
    playlist = spot.user_playlist_create(user=id_, name= playlist_name, public= False, collaborative=False, description='Billboard 100')
    spot.playlist_add_items(playlist_id=playlist['id'], items=URI)

