import requests
from django.shortcuts import render
from music.settings import SPOTIFY_CLIENT_ID
from django.views.decorators.cache import cache_page

spotify_base_url = "https://api.spotify.com/v1/"
echonest_base_url = "http://developer.echonest.com/api/v4/"

@cache_page(60 * 10)
def artist(request, artist_id = None):
	if artist_id and isValidArtistID(artist_id):
		artist = getArtist(artist_id)
		albums = getAlbums(artist_id)

		similar = getSimilarArtists(artist_id)

		context = {
			'artist': artist,
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


def searchArtist(name):
	"""
	Returns <int> id:spotify:artist if succesful, None otherwise
	"""

	endpoint = "search"
	url = "%s%s" % (spotify_base_url,endpoint)
	r = requests.get(url, params = {
		"q": name,
		"type": "artist"
		})
	if r.status_code == 200:
		response = r.json()
		artists = response.get("artists",{})
		if artists and artists.get("items",[]):
			artist_id = artists.get("items")[0]["id"]
			return artist_id


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

	response = requests.get(echonest_base_url + endpoint,
		params= {	'api_key': ECHO_API_KEY,
					'id': "spotify:artist:" + artist_id,
					"bucket": ['biographies', 'news', 'artist_location']}).json().get('response',{}).get('artist')
	if response:
		return {k:v for (k,v) in response.items()}


def getNews(artist_id, limit = 5, relevance = True):
	endpoint = "artist/news"
	return requests.get(echonest_base_url + endpoint, params ={
		"api_key": ECHO_API_KEY,
		"id": "spotify:artist:" + artist_id,
		"results": limit,
		"high_relevance": str(relevance).lower()
		}).json().get('response',{}).get("news")
