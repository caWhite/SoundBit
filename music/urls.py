from django.conf.urls import url, patterns, include

urlpatterns = patterns('music.views',
	url(r'^$', 'index', name = 'index'),
	url(r'^search$', 'search', name = 'search'),
	url(r'^artist/(?P<name>.+)', 'artist', name = 'artist'),
	)