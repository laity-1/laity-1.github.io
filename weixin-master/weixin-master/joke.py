# coding: utf-8
import urllib2
import json

def getjoke():
    url = 'http://xyapi.sinaapp.com/Api/?type=joke'
    data = {'use':'test', 'key':'test', 'show':'json'}
    html = ((urllib2.urlopen(url,urllib.urlencode(data)))).read()
    joke = (json.loads(html))['joke']
    joke_info = u'%s' % (''.join(joke))
    return joke_info
