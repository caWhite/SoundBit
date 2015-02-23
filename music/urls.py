from django.conf.urls import url, patterns, include

urlpatterns = patterns('music.views',
	url(r'^$', 'index', name = 'index'),
	url(r'^search/$', 'search', name = 'search'),
	url(r'^artist/(?P<artist_id>.+)$', 'artist', name = 'artist'),
	url(r'^artist/', 'artist', name = 'artist'),
	url(r'^genre/(?P<genre>.+)/', 'genre', name = 'genre'),
	url(r'^genre/$','genre', name = 'genre')
	)