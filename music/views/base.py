from django.shortcuts import render, redirect
# from artist import get_id
from artist import searchArtist
def index(request):
	return render(request, 'index.html')

def about(request):
	return render(request, 'about.html')

def search(request):
	if request.method == 'POST':
		artist_name = request.POST.get('name')
		if not artist_name:
			return render(request, "search_error.html", {'error': "No artist's name entered!"})
		else:
			artist = searchArtist(artist_name)
			if artist:
				return redirect("artist", artist_id = artist['id'])
			else:
				return render(request, "search_error.html", {'error': "We couldn't find any artist by that name!"} )
	else:
		return render(request, 'index.html')
