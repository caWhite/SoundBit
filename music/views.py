from django.shortcuts import render, redirect
from keys import *
from helpers import *
from variables import GENRES
from bs4 import BeautifulSoup
import requests

def index(request):
	return render(request, 'index.html')
def about(request):
	return render(request, 'about.html')
def search(request):
	if request.method == 'POST':
		if not request.POST.get('name'):
			return render(request, "search_error.html", {'error': "No artist's name entered!"})
		else:
			artist_name = request.POST.get('name')
			try:
				return redirect("artist", artist_id = get_id(artist_name))
			except ValueError:
				return render(request, "search_error.html", {'error': "We couldn\'t find any artist by that name!"} )
	else:
		return render(request, 'index.html')

def artist(request, artist_id = None):
	if not artist_id:
		return render(request, "search_error.html", {'error': 'No artist specified'})
	elif not validID(artist_id):
		return render(request, "search_error.html", {'error': 'Malformed artist ID'})
	else:
		context = {'profile' : artist_profile(artist_id),'similar' : get_similar(artist_id)}
		top = top_songs(context['profile']['seven_id']) if context['profile'].get('seven_id') else None
		if top:
			song_stream = [ {'name': s['name'] ,'url': stream(s['id']) } for s in top ]
			context['song_stream'] = song_stream
		return render(request,"bio.html", context)

def validID(artist_id):
	url = 'http://developer.echonest.com/api/v4/artist/profile'
	r = requests.get(url=url,params={
	'api_key' : ECHO_API_KEY,
	'id' : artist_id})
	return False if int(r.json()['response']['status']['code']) == 5 else True

def top_songs(artist_id, limit = 3):
	url = 'http://api.7digital.com/1.2/artist/toptracks'
	r = requests.get(url=url, params={
	'oauth_consumer_key' : SEVEN_DIGITAL_CONSUMER,		
	'artistId' :  artist_id,
	'pageSize'  : limit})
	rurl = r.url
	soup = BeautifulSoup(r.text).tracks.find_all('track')
	return [{'name': song.title.text,'id':song['id']} for song in soup]
	

def get_id(artist, namespace = None):
	"""
	Retreive Echonest ID for given artist
	Args: 
		(string) artist : Value equal to artist's name
		(string, optional) namespace : When incluced, returns artist's id in 
		the given namespace rather than the Echnost ID

	Returns:
		(int) ID if succuessful

	Raises:
		ValueError: If lookup fails
	"""
	url = 'http://developer.echonest.com/api/v4/artist/search'
	params ={'api_key': ECHO_API_KEY,'name': artist,'results': 1}
	if namespace:
		params['namespace'] = namespace
		r = requests.get(url=url, params=params)
		try:
			return r.json()['response']['artists'][0]['foreign_ids'][0]['foreign_id']
		except:
			raise ValueError('Could not retrieve foreign ID')
	else:
		r = requests.get(url=url, params=params)
		data = r.json()
		try:
			return r.json()['response']['artists'][0].get('id')
		except:
			raise ValueError('Could not retrieve Echonest ID')
			
def get_similar(artist_id, limit = 3):
	"""
	Obtain list of simliar artists 

	Args:
		(int) artist_id: Echonest ID for the seeding artist 
		(int, optional) limit: Restricts the number of returned artists  
	Returns:
		(list) artist names if succuessful, else None
	"""
	url = 'http://developer.echonest.com/api/v4/artist/similar'
	r = requests.get(url=url,params={
	'api_key' : ECHO_API_KEY,
	'id' : artist_id,
	'results' : limit})
	try:
		return [a for a in r.json()['response'].get('artists')]
	except KeyError:
		return None

def artist_profile(artist_id):
	url = 'http://developer.echonest.com/api/v4/artist/profile'
	r = requests.get(url=url, params={
	'api_key' : ECHO_API_KEY,
	'id' : artist_id,
	'bucket' : ['images','id:7digital-US','genre']})
	profile = {
	'name' : r.json()['response']['artist']['name'],
	'genre' : [g['name'] for g in r.json()['response']['artist']['genres']][:3]}
	try:
		profile['image'] = r.json()['response']['artist']['images'][2]['url']
	except Exception:
		pass
	try:
		profile['seven_id'] = r.json()['response']['artist'].get('foreign_ids')[0].get('foreign_id')[19:]
	except Exception:
		pass		
	return profile

# ***** Views pertaining to genres ***** 
def genre(request, genre= None):
	if request.method == 'POST':
		return redirect('genre', request.POST.get('genre'))
	else:
		if genre:
			if genre in GENRES:
				return render(request, 'genre.html',{
				'genre' : {
				'name' : genre,
				'profile' : get_profile(genre),
				'similar' : get_top_artists(genre)}})
			else:
				return render(request, 'search_error.html', {'error': 'We couldn\'nt find that genre'})
		else:
			context = dict(genres = GENRES)
			return render(request, 'genre_empty.html', context)

def get_genre(artistName):
	"""
	Returns the genres associated with an artist 

	Args:
		(string) Name of artist to return genres for
	Returns:
		(list, string) list of the 3 most revelent genres if succuessful, else None
	"""
	url = 'http://developer.echonest.com/api/v4/artist/search'
	r = requests.get(url=url,params={
	'api_key' : ECHO_API_KEY,
	'name' : artistName,
	'results' : 1,
	'bucket' : 'genre'})
	try:
		return [g['name'] for g in r.json()['response']['artists'][0]['genres'][:3]]
	except IndexError:
		pass

def get_top_artists(genre, results = 10):
	url = 'http://developer.echonest.com/api/v4/genre/artists'
	r = requests.get(url=url,params={
	'api_key' : ECHO_API_KEY,
	'name' : genre,
	'results' : results})
	return [a for a in r.json()['response']['artists']]

def get_profile(genre):
	url = 'http://developer.echonest.com/api/v4/genre/profile'
	r = requests.get(url=url,params={ 
	'api_key' : ECHO_API_KEY,
	'name' : genre,
	'bucket' : ['description', 'urls']})
	return dict(description = r.json()['response']['genres'][0].get('description'), 
		url = r.json()['response']['genres'][0].get('urls').get('wikipedia_url'))