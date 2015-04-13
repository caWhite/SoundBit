from string import ascii_letters, digits
from random import choice
from urllib2 import quote 
from django_music.settings import SEVEN_DIGITAL_CONSUMER, SEVEN_DIGITAL_SECRET
import hashlib, hmac, base64, time

def generate_nonce(size=12):
    return ''.join([choice(ascii_letters+digits) for a in range(size)])

def url_encode(data):
	return quote(data,'')

def generate_signature(base_url):
	h = hmac.HMAC(SEVEN_DIGITAL_SECRET + '&', base_url, hashlib.sha1).digest()
	return url_encode(base64.b64encode(h))	

def stream(track_id):
	url = 'http://previews.7digital.com/clip/%s'
	values = dict(
	oauth_consumer_key = SEVEN_DIGITAL_CONSUMER,
	oauth_signature_method = 'HMAC-SHA1',
	oauth_version = '1.0',
	oauth_nonce = generate_nonce(),
	oauth_timestamp = int(time.time()),
	country = 'US',
	)
	base_string = 'GET&' + url_encode(url%track_id) + '&' + url_encode('&'.join(["%s=%s" % (a,b) for a,b in sorted(values.items())]))
	values['oauth_signature'] = generate_signature(base_string)

	return url%track_id + '?' + '&'.join(["%s=%s" % (a,b) for a,b in values.items()])
