import json
import urlparse
import pickle
import collections
from pymongo import MongoClient
import datetime
import time
import os
from collections import Counter
import pprint
import timeline_new
import detect

def load_directory():
    # directory will be the first entry
    with open('config.json') as json_data_file:
            data = json.load(json_data_file)
            return data

DATA_DIR = load_directory()["PATH_RAWDATA"]

def get_full_prefix(prefix):
	return 'processed_data/' + prefix + '/' + prefix + '_tweet_'

def get_full_src_path(prefix):
	ind_start = prefix.index('/') 
	ind_end = prefix.index('/', 16)
	return DATA_DIR + prefix[ind_start:ind_end] + '.txt'

def test_expand_url():
	st = r'http:\\/\\/ti.me\\/1vBSjOi'
	print st
	st = st.replace(r'\\', '')
	print st
	print urlparse.urlparse('http://ti.me/1vBSjOi').netloc
	print urlparse.urlparse('http:\\/\\/ti.me\\/1vBSjOi').netloc

def loadjson(source):	
	# returns a generator of tweets
	with open(source, 'r') as f:
		for line in f:
			#print line
			t = json.loads(line)
			t = json.loads(t)
			if 'text' in t:
				yield t

def get_percent_porn_related(source):
	count = 0
	total = 0
	for tweet in loadjson(source):
		total += 1
		for word in ['girl', 'nude', 'porn', 'dick', 'cock', 'adult', 'pussy', 'sex', 'nake', 'hardcore', 'teen']:
			if word in tweet['text']:
				#print tweet['text']
				count += 1
				break
	print count
	print total

def get_top_embedd_url(prefix, source):
	if not os.path.isfile(prefix + 'top_embedded_url.p'):
		c = collections.Counter()
		counter = 0
		for tweet in source:
			if counter % 1000 == 0:
				print "%d tweets processed" %(counter)

			counter += 1

			if len(tweet['entities']['urls']) > 0:
				for entry in tweet['entities']['urls']:
					if entry['expanded_url'] is not None:
						url = urlparse.urlparse(entry['expanded_url']).netloc
						c[url] += 1
		pickle.dump(dict(c), open(prefix + 'top_embedded_url.p', 'w'))
	return pickle.load(open(prefix + 'top_embedded_url.p', 'rb'))
	

def get_num_tweet(year, month, day, userlist):
	"""
	The function is almost the same as slice_data, but instead of 
	becoming a generator, this function counts the number of tweets
	created by a list of users defined in 'userlist'

	"""
	userlist = set(userlist)
	count = 0
	result = 0
	client = MongoClient()                           # connect to the server             
	db = client.hongkong  # choose a database (geoTurkeyCrawlonlyElectionJune32015 hongkong)
	collection = db.posts              				 # choose a collection (posts, etc,.)
	end_time = datetime.datetime(year, month, day + 1)
	start_time = datetime.datetime(year, month, day)
	
	# convert datetime to unix timestamp_ms
	low = str(int(time.mktime(start_time.timetuple()) * 1000))
	high = str(int(time.mktime(end_time.timetuple()) * 1000))
	print low, high

	for tweet in collection.find({"timestamp_ms": {"$lt": high, "$gt": low}}):
		if count % 1000 == 0:
			print count
		count += 1
		if 'created_at' in tweet:
			if tweet['user']['id'] in userlist:
				result += 1
	return result

def slice_data(year, month, day):
	# slide a large dataset into days, and pick one day 
	# for spam detection
	# possible datasets: Hongkong, Turkey
	# 
	# make sure timestamp_ms is indexed in MongoDB, otherwise following function
	# does not work :/

	count = 0
	client = MongoClient()                           # connect to the server             
	db = client.hongkong  # choose a database (geoTurkeyCrawlonlyElectionJune32015 hongkong)
	collection = db.posts              				 # choose a collection (posts, etc,.)
	end_time = datetime.datetime(year, month, day + 1)
	start_time = datetime.datetime(year, month, day)
	
	# convert datetime to unix timestamp_ms
	low = str(int(time.mktime(start_time.timetuple()) * 1000))
	high = str(int(time.mktime(end_time.timetuple()) * 1000))
	print low, high

	for tweet in collection.find({"timestamp_ms": {"$lt": high, "$gt": low}}):
		if count % 1000 == 0:
			print count
		count += 1
		if 'created_at' in tweet:
			yield(tweet)

def slice_and_store(year, month, day, filename):
	# slide a large dataset into days, and pick one day 
	# for spam detection
	# possible datasets: Hongkong, Turkey
	# 
	# make sure timestamp_ms is indexed in MongoDB, otherwise following function
	# does not work :/
	if os.path.isfile(filename):
		print 'File already exists!'
		return
	f = open(filename, 'wb')
	count = 0
	client = MongoClient()                           # connect to the server             
	db = client.hongkong                             # choose a database (geoTurkeyCrawlonlyElectionJune32015 hongkong)
	collection = db.posts              				 # choose a collection (posts, etc,.)
	end_time = datetime.datetime(year, month, day + 1)
	start_time = datetime.datetime(year, month, day)
	
	# convert datetime to unix timestamp_ms
	low = str(int(time.mktime(start_time.timetuple()) * 1000))
	high = str(int(time.mktime(end_time.timetuple()) * 1000))
	print low, high

	#for tweet in collection.find({"timestamp_ms": {"$lt": high, "$gt": low}}):
	for tweet in collection.find():
		if count % 1000 == 0:
			print count
		count += 1
		if 'created_at' in tweet:
			del tweet['_id']
			json.dump(json.dumps(tweet), f)
			f.write('\n')
			f.flush()

def url_analysis(filename):
	url = Counter()
	count = 0
	for tweet in loadjson(filename):
		if count % 1000 == 0:
			print count
		count += 1
		if len(tweet['entities']['urls']) > 0:
			embedded_url = tweet['entities']['urls'][0]['expanded_url']
			if embedded_url is not None:
				embedded_url = embedded_url.replace("\\","") 
				embedded_url = urlparse.urlparse(embedded_url).netloc
				#print embedded_url
				url[embedded_url] += 1
	pprint.pprint(url.most_common(100))

def compare_spam_users():

		def load_spam_user(filename):
			spam_group = json.load(open(filename, 'r'))
			spam_user = set([])
			for value in spam_group.values():
				spam_user = spam_user.union(set(value['spam_user']))
			return spam_user

		f1 = 'hongkong_10_10_50cutoff/hongkong_tweet_spam_group.json'
		f2 = 'hongkong_10_10/hongkong_tweet_spam_group.json'
		u1 = load_spam_user(f1)
		u2 = load_spam_user(f2)
		print len(u1)
		print len(u2)
		print len(u1.intersection(u2))
		print len(u1.intersection(u2)) * 1.0 / len(u1)
		#pprint.pprint(sorted(u1.difference(u2)))
		pprint.pprint(sorted(u2.difference(u1)))
		# do set intersection

def spam_group_num_tweet_pie_chart_miniplot():
	# manully get the percent of tweet of each URL service
	convert = {'bit':4.44, 'ift':3.54, 'ow':3.22,'tinyurl':5.70,'dld':13.36,'viid':21.66,'goo':2.70,'dlvr':13.34, 'lnis':26.65}
	spam_group_dic = json.load(open('user_num_tweet_per_spam_group_all_URL_shorteners.json','r'))
	all_labels = []
	all_sizes = []
	titles = []
	dic = json.load(open('spam_category.json', 'r'))
	for entry in sorted(dic):
		labels = []
		sizes = []
		prefix = entry.keys()[0]
		titles.append(prefix+' ('+str(convert[prefix])+'%)')
		#for category in entry[prefix]:
		for category in ['malware', 'bot followers', 'porn', 'news bot', 'click bait', 'Quran verses', 'other']:
			#if entry[prefix][category]["spam_group_id"] != []:
				labels.append(category)
				total = sum([spam_group_dic[prefix][str(group)] for group in entry[prefix][category]["spam_group_id"]])
				sizes.append(total)
		all_labels.append(labels)
		all_sizes.append(sizes)
	print all_labels
	print all_sizes
	print titles
	timeline_new.plot_pie_miniplot(labels = all_labels, sizes = all_sizes, titles = titles, filename = 'spam_category/all_url_shorteners_spam_category_tweet_based')

def load_user(prefix, group_id):
    full_prefix = get_full_prefix(prefix)
    detector = detect.SpamDetector(prefix = full_prefix)
    group = detector.get_spam_group()
    user_info = detector.get_user_info()
    #alluser = set([])
    id_count = 1
    for g in group:
        if id_count == group_id:
			return group[g]['spam_user'], user_info
        id_count += 1

def spam_group_pie_chart():
	dic = json.load(open('spam_category.json', 'r'))
	for entry in dic:
		labels = []
		sizes = []
		prefix = entry.keys()[0]
		for category in entry[prefix]:
			if entry[prefix][category]["spam_group_id"] != []:
				if "promotion" in category:
					labels.append("click bait")
				else:	
					labels.append(category)
				sizes.append(sum(entry[prefix][category]["total_user"]))

		timeline_new.plot_pie(labels, sizes, filename = 'spam_category/' + prefix + '_spam_category')

# de-duplicate and use new bot categorization
def spam_group_pie_chart_miniplot_new():
	convert = {'bit':2.40, 'ift':2.56, 'ow':3.15,'tinyurl':3.52,'dld':4.41,'viid':4.95,'goo':6.31,'dlvr':7.90, 'lnis':23.07}
	all_labels = []
	all_sizes = []
	titles = []
	dic = json.load(open('spam_category.json', 'r'))
	for entry in sorted(dic):
		labels = []
		sizes = []
		prefix = entry.keys()[0]
		titles.append(prefix+' ('+str(convert[prefix])+'%)')
		
		full_prefix = get_full_prefix(prefix)
		detector = detect.SpamDetector(prefix = full_prefix)
		group = detector.get_spam_group()
		for category in ['malware', 'bot followers', 'porn', 'news bot', 'click bait', 'Quran verses', 'other']:
			#if entry[prefix][category]["spam_group_id"] != []:
				if "promotion" in category:
					labels.append("click bait")
				else:	
					labels.append(category)
				total = set([])
				for _id_ in entry[prefix][category]['spam_group_id']:
					user_to_add = set(group[group.keys()[_id_ - 1]]['spam_user'])
					total.update(user_to_add)
					print len(total)
				sizes.append(len(total))
		all_labels.append(labels)
		all_sizes.append(sizes)
	print all_labels
	print all_sizes
	print titles
	timeline_new.plot_pie_miniplot(labels = all_labels, sizes = all_sizes, titles = titles, filename = None)
	#timeline_new.plot_pie_miniplot(labels = all_labels, sizes = all_sizes, titles = titles, filename = 'spam_category/all_url_shorteners_spam_category_user_based')

# user based 
def spam_group_pie_chart_miniplot():
	convert = {'bit':2.40, 'ift':2.56, 'ow':3.15,'tinyurl':3.52,'dld':4.41,'viid':4.95,'goo':6.31,'dlvr':7.90, 'lnis':23.07}
	all_labels = []
	all_sizes = []
	titles = []
	dic = json.load(open('spam_category.json', 'r'))
	for entry in sorted(dic):
		labels = []
		sizes = []
		prefix = entry.keys()[0]
		titles.append(prefix+' ('+str(convert[prefix])+'%)')
		#titles.append(prefix)
		#for category in entry[prefix]:
		for category in ['malware', 'bot followers', 'porn', 'news bot', 'click bait', 'Quran verses', 'other']:
			#if entry[prefix][category]["spam_group_id"] != []:
				if "promotion" in category:
					labels.append("click bait")
				else:	
					labels.append(category)
				sizes.append(sum(entry[prefix][category]["total_user"]))
		all_labels.append(labels)
		all_sizes.append(sizes)
	print all_labels
	print all_sizes
	print titles
	timeline_new.plot_pie_miniplot(labels = all_labels, sizes = all_sizes, titles = titles, filename = None)
	#timeline_new.plot_pie_miniplot(labels = all_labels, sizes = all_sizes, titles = titles, filename = 'spam_category/all_url_shorteners_spam_category_user_based')

if __name__ == '__main__':
	PREFIX = 'hongkong/hongkong_tweet_'
	DATA_DIR = "/Users/zc/Documents/twitter_research/github_code/twitter_research/data/stream/"
	SOURCE_FILE = DATA_DIR + PREFIX[:PREFIX.index('/')] + '.txt'
	#spam_group_pie_chart_miniplot_new()
	#spam_group_num_tweet_pie_chart_miniplot()
	slice_and_store(2014, 11, 2, SOURCE_FILE)
	#compare_spam_users()
	#get_percent_porn_related(SOURCE_FILE)
	#url_analysis(SOURCE_FILE)
	"""
	for tweet in collection.find():
		if count % 1000 == 0:
			print count
		count += 1
		if 'created_at' in tweet:
			print tweet['created_at']
			dt = datetime.datetime.strptime(tweet[u'created_at'], '%a %b %d %H:%M:%S +0000 %Y')  # format the time
			if dt.year == end_time.year and dt.month == end_time.month and dt.day == end_time.day:
				print dt
				return
			if dt >= start_time and dt < end_time:
				yield(tweet)
	"""				
