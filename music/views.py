from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse
#from django.utils.http imnport urlencode --- don't need?
import requests, json
from variables import ECHO_API_KEY, genres
# Create your views here.

#ECHO_API_KEY = 'VRATZ6WBCFTG00HZA'
SEVEN_DIGITAL_CONSUMER = '7dsmbgsr26pt'
SEVEN_DIGITAL_SECRET = '4r4zkx5598dragxm'

def index(request):
	return render_to_response('index.html')

def search(request):
	if request.method == "GET":
		artist = request.GET.get("name")
		if artist:
			return redirect("artist", artist_id=get_id(artist))
		else:
			return render(request, "search.html")
	else:
		if not request.POST.get('name'):
			return render(request, "search.html", {'error': "No artist's name entered!"})
		else:
			artist = request.POST['name']
			return redirect("artist", artist_id=get_id(artist))


def artist(request, artist_id = None):
	if not artist_id or artist_id == 'None':
		return redirect("search")
	else:
		context = dict(
			artist_name = get_name(artist_id),
			bio = get_bio(artist_id),
			similar = get_similar(artist_id),
			)
		print get_id(get_name(artist_id),'id:7digital-US')
		return render(request,"bio.html", context)

def get_name(artist_id):
	url = 'http://developer.echonest.com/api/v4/song/search'
	params = dict(
	api_key= ECHO_API_KEY,		
	artist_id=  artist_id,
	results = 1,
	)
	r = requests.get(url=url, params=params)
	try:
		return r.json()['response']['songs'][0]['artist_name']
	except KeyError:
		return None

def top_songs(artist_id, limit = 5, sort = 'song_hotttnesss-desc'):
	url = 'http://developer.echonest.com/api/v4/song/search'

	params = dict(
	api_key= ECHO_API_KEY,		
	artist_id=  artist_id,
	results= limit,
	bucket = ['tracks', 'id:spotify']
	)
	r = requests.get(url=url, params=params)
	#return [s['artist_foreign_ids']]
	
#Returns echonest ID for given artist parameter, takes optional namespace parameter to return id in the given namespace
def get_id(artist, namespace = None):
	url = 'http://developer.echonest.com/api/v4/artist/search'
	if namespace:
		params = dict(
		api_key= ECHO_API_KEY,
		name= artist,
		results= 1,
		bucket = namespace
		)
		r = requests.get(url=url, params=params)
		print r.url
		try:
			return r.json()['response']['artists'][0]['foreign_ids'][0]['foreign_id']
		except IndexError:
			return None		
	else:
		params = dict(
			api_key= ECHO_API_KEY,
			name= artist,
			results= 1,
			)
		r = requests.get(url=url, params=params)
		try:
			return r.json()['response']['artists'][0].get('id')
		except IndexError:
			return None
	
def get_bio(artist_id):
	url = 'http://developer.echonest.com/api/v4/artist/biographies'
	params = dict(
		api_key= ECHO_API_KEY,
		id= artist_id,
		license='cc-by-sa',
		results=5,
		)
	r = requests.get(url=url, params=params)
	data = r.json()
	try:
		bios = data['response']['biographies']
		for b in bios:
			if b['license']['attribution'] == 'Last.fm':
				return b
	except (KeyError, IndexError) as e:
		return None

def get_similar(artist_id, limit = 'False'):
	url = 'http://developer.echonest.com/api/v4/artist/similar'
	params = dict(
		api_key = ECHO_API_KEY,
		id = artist_id,
		limit = limit,
	)
	r = requests.get(url=url, params=params)
	try:
		data =  r.json()['response']['artists']
		return [a for a in data]
	except KeyError:
		return None
		
# ***** Views pertaining to genres ***** 
def genre(request, genre= None):
	if request.method == 'POST':
		return redirect('genre', request.POST.get('genre'))
	else:
		if genre:
			context = dict(
				genre = dict(
					name = genre,
					profile = get_profile(genre),
					similar = get_top_artists(genre)
					)
				)
			return render(request, 'genre.html', context)
		else:
			context = dict(
				#genres = allgenres()
				genres = genres
				)
			print allgenres()
			return render(request, 'genre_empty.html', context)

def allgenres():
	url = 'http://developer.echonest.com/api/v4/genre/list'
	params = dict(
		api_key= ECHO_API_KEY,
		)
	r = requests.get(url=url, params=params)
	return [a['name'] for a in r.json()['response']['genres']]

def get_genre(artistName):
	url = 'http://developer.echonest.com/api/v4/artist/search'
	params = dict(
		api_key= ECHO_API_KEY,
		name= artistName,
		results= 1,
		bucket= 'genre',
		)
	r = requests.get(url=url, params=params)
	data = r.json()
	try:
		return [g['name'] for g in data['response']['artists'][0]['genres'][:3]]
	except IndexError:

		return None

def get_top_artists(genre, results = 10):
	url = 'http://developer.echonest.com/api/v4/genre/artists'
	params = dict(
		api_key = ECHO_API_KEY,
		name = genre,
		results = results,
		)
	r = requests.get(url=url,params=params)
	return [a for a in r.json()['response']['artists']]

def get_profile(genre):
	url = 'http://developer.echonest.com/api/v4/genre/profile'
	params = dict(
		api_key = ECHO_API_KEY,
		name = genre,
		bucket = ['description', 'urls'],
		)
	r = requests.get(url=url,params=params)
	data = r.json()
	return dict(description = data['response']['genres'][0].get('description'), 
		url = data['response']['genres'][0].get('urls').get('wikipedia_url'),
		)