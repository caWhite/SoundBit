from django.shortcuts import render, redirect
import requests, json
from helpers import *
from variables import ECHO_API_KEY, genres
from bs4 import BeautifulSoup

# Create your views here.

ECHO_API_KEY = 'VRATZ6WBCFTG00HZA'
SEVEN_DIGITAL_CONSUMER = '7dsmbgsr26pt'
SEVEN_DIGITAL_SECRET = '4r4zkx5598dragxm'

def index(request):
	return render(request, 'index.html')

def about(request):
	return render(request, 'about.html')
def search(request):
	if not request.POST.get('name'):
		return render(request, "search_error.html", {'error': "No artist's name entered!"})
	else:
		artist = request.POST['name']
		artist_id = get_id(artist)
		if artist_id:
			return redirect("artist", artist_id=artist_id)
		else:
			return render(request, "search_error.html", {'error': "We couldn\'t find any artist by that name!"})



def artist(request, artist_id = None):
	if not artist_id or artist_id == 'None':
		return redirect("search")
	else:
		profile = artist_profile(artist_id)
		context = dict(
			profile = profile,
			similar = get_similar(artist_id),
			)
		if profile.get('seven_id'):
			top = top_songs(profile['seven_id'])
			if top:
				song_stream = [ {'name': s['name'] ,'url': stream(s['id']) } for s in top ]
				context['song_stream'] = song_stream
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

def top_songs(artist_id, limit = 3):
	url = 'http://api.7digital.com/1.2/artist/toptracks'
	params = dict(
	oauth_consumer_key= SEVEN_DIGITAL_CONSUMER,		
	artistId=  artist_id,
	pageSize = limit,
	)
	r = requests.get(url=url, params=params)
	rurl = r.url
	soup = BeautifulSoup(r.text).tracks.find_all('track')
	return [{'name': song.title.text,'id':song['id']} for song in soup]
	
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

def get_similar(artist_id, limit = 3):
	url = 'http://developer.echonest.com/api/v4/artist/similar'
	params = dict(
		api_key = ECHO_API_KEY,
		id = artist_id,
		results = limit,
	)
	r = requests.get(url=url, params=params)
	try:
		data =  r.json()['response']['artists']
		return [a for a in data]
	except KeyError:
		return None

def artist_profile(artist_id):
	url = 'http://developer.echonest.com/api/v4/artist/profile'
	params = dict(
		api_key = ECHO_API_KEY,
		id = artist_id,
		bucket = ['images','id:7digital-US','genre'],)
	r = requests.get(url=url, params=params)
	data = r.json()
	profile = dict(
		name = data['response']['artist']['name'],
		genre = [g['name'] for g in data['response']['artist']['genres']][:3],
		)
	try:
		profile['image'] = data['response']['artist']['images'][2]['url']
	except Exception:
		pass
	try:
		profile['seven_id'] = data['response']['artist'].get('foreign_ids')[0].get('foreign_id')[19:]
	except Exception:
		pass		
	return profile

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
				genres = genres
				)
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