from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse
import requests, json
# Create your views here.

ECHO_API_KEY = 'VRATZ6WBCFTG00HZA'

def index(request):
	return render_to_response('index.html')

def register(request):
	pass

def login(request):
	pass	

def search(request):
	context = {}
	if request.method == 'POST':
		artist = request.POST.get('search')

		context['artist'] = artist
		context['similar'] = get_similar(artist)
		context['bio'] = get_bio(artist)

		return redirect('artist', name=artist)


	else:
		return render(request, 'search.html')

def artist(request, name):
		artist_id = get_id(name)
		context = dict(
		artist=name.replace('-',' '),
		similar=get_similar(artist_id),
		bio=get_bio(artist_id),
		)
		print get_bio(artist_id)
		return render(request, 'bio.html', context)

def get_id(artist):
	url = 'http://developer.echonest.com/api/v4/artist/search'
	params = dict(
		api_key= ECHO_API_KEY,
		name= artist,
		results= 1,
		)
	r = requests.get(url=url, params=params)
	data = json.loads(r.text)
	return data['response']['artists'][0].get('id')

def get_bio(artist_id):
	url = 'http://developer.echonest.com/api/v4/artist/biographies'
	params = dict(
		api_key= ECHO_API_KEY,
		id= artist_id,
		results= 1,
		)
	r = requests.get(url=url, params=params)
	data = json.loads(r.text)
	return data['response']['biographies'][0]['text']

def get_similar(artist_id, limit = 'False'):
	url = 'http://developer.echonest.com/api/v4/artist/similar'
	params = dict(
		api_key = ECHO_API_KEY,
		id = artist_id,
		bucket = 'images',
		limit = limit,
	)
	r = requests.get(url=url, params=params)
	data =  json.loads(r.text)['response']['artists']
	return [a for a in data]

