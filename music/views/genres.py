import requests
import music.views
from music.variables import GENRES
from django.shortcuts import render, redirect
from django_music.settings import ECHO_API_KEY

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
	'api_key': ECHO_API_KEY,
	'name': genre,
	'results': results,
	"bucket": ["id:spotify","images"] })
	
	top_artists = []
	for artist in r.json()['response']['artists']:
		artist['foreign_ids'] = artist['foreign_ids'][0]['foreign_id'][15:]
		top_artists.append(artist)
	
	return top_artists

def get_profile(genre):
	url = 'http://developer.echonest.com/api/v4/genre/profile'
	r = requests.get(url=url,params={ 
	'api_key' : ECHO_API_KEY,
	'name' : genre,
	'bucket' : ['description', 'urls']})

	return dict(description = r.json()['response']['genres'][0].get('description'), 
		url = r.json()['response']['genres'][0].get('urls').get('wikipedia_url'))