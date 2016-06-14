
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from artist import searchArtist

def index(request):
	return render(request, 'index.html')


def about(request):
	return render(request, 'about.html')


@require_POST
def search(request):
	artist_name = request.POST.get('name')
	if not artist_name:
		return render(request, "search_error.html", {'error': "No artist's name entered!"})
	else:
		artist_id = searchArtist(artist_name)
		if artist_id:
			return redirect("artist", artist_id = artist_id)
		else:
			return render(request, "search_error.html", {'error': "We couldn't find any artist by that name!"} )


def callback(request):
	return
