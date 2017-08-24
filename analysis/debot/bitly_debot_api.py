# -*- coding: utf-8 -*-
import datetime 
import time
import pprint
import bitly_api
import detect
import json
import util
import requests
import urllib2
import timeline_new

BITLY_ACCESS_TOKEN = "cd984321d42cddb0e6f43048a775ccc158f17046"
GOOGLE_API_KEY = "AIzaSyDAmnXhJkg4SmIqGIOtCpWbZjFdGVBwyyY"
OW_API_KEY = ""
DLVR_API_KEY = "1baddd6207554a18a2fa07399cc0430f"
cache = {}


def google_api(path):
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?shortUrl='+path+'&projection=FULL&key='+GOOGLE_API_KEY
    r = requests.get(post_url)
    data = json.loads(r.text)
    print data
    print data['analytics']['allTime']['referrers']
    return int(data['analytics']['allTime']['shortUrlClicks'])

# access click data from ow ly
def ow_api(path):
	# does not work, don't have API key
	post_url = 'http://ow.ly/api/1.1/url/clickStats?&shortUrl=http://hootsuite.com'  # apiKey='+GOOGLE_API_KEY+'
	r = requests.get(post_url)
	print r.text.encode('utf-8', 'ignore')
	#data = json.loads(r.text)

def dlvr_api(path):
	# does not work, api does not support click stat search
	pass

def extract_url_from_twitter_page(path, prefix):
	#mydata=[('screen_name','@'+user)] 
	#mydata=urllib.urlencode(mydata)
	req=urllib2.Request(path)
	#req.add_header("Content-type", "application/x-www-form-urlencoded")
	page=urllib2.urlopen(req).read()
	if prefix in page:
		index = page.index('http://'+prefix)
		endindex = page.index('class="twitter-timeline-link', index)
		print index, endindex
		if endindex - index < 200:
			print page[index:endindex-2]
			cache[path] = page[index:endindex-2]
			return page[index:endindex-2]
	else:
		return None

def load_user(prefix):
	full_prefix = util.get_full_prefix(prefix)
	detector = detect.SpamDetector(prefix = full_prefix)
	group = detector.get_spam_group()

	"""
	Run those two lines of code of url info file does not exist
	
	url_info = detector.get_url_per_user()
	json.dump(url_info, open('metadata/'+prefix+'_user_url_dictionary.json','w'))
	"""

	url_info = json.load(open('metadata/'+prefix+'_user_url_dictionary.json','r'))
	print len(url_info)

	#alluser = set([])
	# id_count = 1

	for index, g in enumerate(group):
		unique_url = set([])
		for user in group[g]['spam_user']:
			for url in url_info[str(user)]:
				if prefix in url:
					unique_url.add(url)
				else:
					if 'twitter.com' in url:
						if url in cache:
							print 'find url in cache'
							unique_url.add(cache[url])
						else:
							try:
								print url
								new_url = extract_url_from_twitter_page(url, prefix)
								if new_url:
									unique_url.add(new_url)
							except Exception, e:
								print e
								time.sleep(2)

			#unique_url = unique_url.union(set(url_info[str(user)])) 
			#print len(unique_url)

		#pprint.pprint(unique_url)
		group[g]['unique_url'] = list(unique_url)
	json.dump(group, open('metadata/'+prefix+'_spam_group_with_unique_url.json','w'))

def get_connection():
    """Create a Connection base on username and access token credentials"""
    # if BITLY_ACCESS_TOKEN not in os.environ:
    #     raise ValueError("Environment variable '{}' required".format(BITLY_ACCESS_TOKEN))
    # access_token = os.getenv(BITLY_ACCESS_TOKEN)
    bitly = bitly_api.Connection(access_token=BITLY_ACCESS_TOKEN)
    return bitly

def get_click_data(prefix):
	if prefix == 'bit':
		bitly = get_connection()
		print dir(bitly)

	group = json.load(open('metadata/'+prefix+'_spam_group_with_unique_url.json', 'r'))
	for g in group:
		total = 0
		twitter_total = 0
		print 'total num of unique url is %d' %(len(group[g]['unique_url']))
		for url in group[g]['unique_url']:
			print url
			if '?' in url:
				index = url.index('?')
				url = url[:index]
				print 'updated url is'
				print url 
			try:
				if prefix == 'bit':
					#data = bitly.link_clicks(link = url, unit = 'month', units = 12)
					data = bitly.link_referrers(link=url, unit = 'month', units = 12)
					for i in data:
						if 't.co' in i['referrer'] or 'twitter' in i['referrer']:
							twitter_total += i['clicks']
						else:
							print "NO twitter: ", i['referrer']
						total += i['clicks']
				elif prefix == 'goo':
					total += google_api(url)
			except Exception as e:
					print e
		print total, twitter_total
		print 
		group[g]['total_click'] = total
		group[g]['twitter_refer_click'] = twitter_total
	json.dump(group, open('metadata/'+prefix+'_spam_group_with_total_click.json','w'))

def spam_category_click(prefix, attribute):
	dic = json.load(open('spam_category.json', 'r'))
	for v in dic:
		if prefix == v.keys()[0]:
			dic = v[v.keys()[0]]
			break

	group = json.load(open('metadata/'+prefix+'_spam_group_with_total_click.json','r'))

	labels = []
	sizes = []
	for category in ['malware', 'bot followers', 'porn', 'news bot', 'click bait', 'Quran verses', 'other']:
		print category
		total = sum([group[group.keys()[group_id - 1]][attribute] for group_id in dic[category]['spam_group_id']])
		print [[group[group.keys()[group_id - 1]]['twitter_refer_click']*1.0/(group[group.keys()[group_id - 1]]['total_click']+0.0001) for group_id in dic[category]['spam_group_id']]]
		# neet to exclude one exceedingly large group
		print total

		if prefix == 'bit':
			if total > 1000000:
				total = 0
		sizes.append(total)
		labels.append(category)
		
	timeline_new.plot_pie(labels, sizes, filename = 'spam_category/' + prefix + '_spam_category_url_' + attribute)


def testReferrer():
    bitly = get_connection()
    data = bitly.referrers(hash='a')
    assert data is not None
    assert len(data) > 1

#extract_url_from_twitter_page('https://twitter.com/i/web/status/829930118034231298')
#load_user('bit')
#google_api('https://goo.gl/64Twrb')
#get_click_data('bit')
spam_category_click('bit', 'twitter_refer_click')
#ow_api('asdf')
