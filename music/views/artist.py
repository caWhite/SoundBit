import requests
from django.shortcuts import render
from django.http import HttpResponse
from django_music.settings import ECHO_API_KEY
from django.views.decorators.cache import cache_page

#SPOTIFY MIGRATION
spotify_base_url = "https://api.spotify.com/v1/"
echonest_base_url = "http://developer.echonest.com/api/v4/"

@cache_page(60 * 10)
def artist(request, artist_id = None):
	if artist_id and isValidArtistID(artist_id):
		artist = getArtist(artist_id)
		albums = getAlbums(artist_id)
		profile = getProfile(artist_id)
		news = getNews(artist_id)
		similar = getSimilarArtists(artist_id)

		context = {
			'artist': artist,
			"location": profile.get('artist_location'),
			"news": news,
			"similar": similar[:6] if similar != None else None,
		}

		if albums:
			for a in albums:
				a['tracks'] = getAlbumTracks(a.get("id"))
				a['preview_url'] = next((s.get('preview_url') for s in a.get('tracks') 
									if s.get('preview_url') is not None), None)
			context['albums'] = albums[:6]

		return render(request, "bio.html", context)
	else:
		return render(request, "search_error.html", {'error': 'There was an error processing your request'})


def searchArtist(name, limit = 1):
	"""
	returns one or more Spotify artist objects
	"""
	r = requests.get("https://api.spotify.com/v1/search",
		params ={
			'q': name,
			'type': 'artist',
			'limit': limit
		}).json()['artists']['items']

	if r:
		return r if len(r) > 1 else r[0]

def isValidArtistID(artist_id):
	endpoint = "artists/%s" % artist_id
	r = requests.get(spotify_base_url + endpoint)

	return True if r.status_code == 200 else False

def getArtist(artist_id):
	endpoint = "artists/%s" % artist_id
	return requests.get(spotify_base_url + endpoint).json()

def getAlbums(artist_id, limit = 15):
	endpoint = "artists/%s/albums" % artist_id
	response = requests.get(spotify_base_url+endpoint, 
		params = {
			"limit": limit,
			"album_type": "album",
			"market": "US"
		}).json()

	items = ','.join(set(map(lambda x: x['id'], response['items'])))
	
	endpoint = "albums"
	response = requests.get(spotify_base_url + endpoint, params = {
		'ids': items
		}).json().get('albums',[])

	if response:
		sorted_top_albums = sorted(response, key = lambda x: x['popularity'], reverse = True)
		return sorted_top_albums

def getAlbumTracks(album_id):
	endpoint = "albums/%s/tracks" % album_id
	response = requests.get(spotify_base_url+endpoint).json()
	return response.get('items')

def getSimilarArtists(artist_id, limit = 5):
	"""
	returns one or more similar Spotify artist objects
	"""
	response = requests.get("https://api.spotify.com/v1/artists/%s/related-artists"%artist_id).json()
	
	return response.get('artists')

def getProfile(artist_id):
	endpoint = "artist/profile"
	
	response = requests.get(echonest_base_url + endpoint, params= {
		'api_key': ECHO_API_KEY,
		'id': "spotify:artist:" + artist_id,
		"bucket": ['biographies', 'news', 'artist_location']}).json()['response']['artist']

	return {k:v for (k,v) in response.items()}

def getNews(artist_id, limit = 5, relevance = True):
	endpoint = "artist/news"
	return requests.get(echonest_base_url + endpoint, params ={
		"api_key": ECHO_API_KEY,
		"id": "spotify:artist:" + artist_id,
		"results": limit,
		"high_relevance": str(relevance).lower()
		}).json().get('response',{}).get("news")