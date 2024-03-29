#!/usr/bin/python
# -*- coding: utf-8 -*-
"""	@
    @Description:   This python script crawls live tweets 
    @				from Twitter Streaming API             
    @
    @Author:        Joe Chen
"""
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import time
import os.path
import pprint
import urlparse
import re
from collections import Counter
# Go to http://apps.twitter.com and create an app.
# streaming api bot detection 2
# consumer_key="mrJtsTABCL8bhCiST3oF0xYuN"
# consumer_secret="dan23zYDbXc9oIGjXAMU3WbyKqeqYdRj4pWIG0So9fvqhTsuGi"

# # After the step above, you will be redirected to your app's page.
# # Create an access token under the the "Your access token" section
# access_token="1979279791-aJUxu8Rd2SK3X7XFxcjN14gyL75x1ZQpSfoV6H8"
# access_token_secret="oUf9AdomderMawIi5td3d2sRr6MSpvI27mSdKsTvwZAUj"

# consumer_key="CuyDAqUbCTF6y6k6mcoGF8owZ"
# consumer_secret="OucJJMnHbYCVNKNgyEJSNBMWBXapwSGuwy1Xc28mXR5vLixrNQ"
# access_token="1979279791-8qRguXNd21mgHR8khU9hg8rcyXkHHSE65tkwFlv"
# access_token_secret="HIR4DQEyHVPrvXm2XNsTToVcgIgxWM2WR2eOoaY1iJV6R"

# name: stream_2017_geo1 (used on CLEAR)
consumer_key="FzqHfORQgNzFI2ZYg3DnhAER8"
consumer_secret="duYRDKAzYyARvyJJTizxDF1bEN2OhkpmOPo0JuHEqLWMaZ1meX"
access_token="1979279791-zGMRoSVd5p2rxUsDwyxItG9aoAh3yoU5zcAnhOE"
access_token_secret="RwjonXpKZioaGBFCj4vgswb631Q64CuTpQyhcS21NK1zA"

# same token as streamer.py
# consumer_key="jQ06JZVLqhDF46pE0vGBSMVgz"
# consumer_secret="I6vrbD7l8Bsyn2kvdEu9zucKdHneWohuXbtn05xkkuobw2feV4"
# access_token="1979279791-avbiikBP5Lyowhd6y2QnJeVywAsRPdM7RIf77m8"
# access_token_secret="emsphrKEJru7MrsGqjiY4ShTNq1AZRRUEEFVaqr9JXLdq"


def load_directory():
    # directory will be the first entry
    with open('config.txt', 'r') as f:
        for line in f:
            return line.strip()
DATA_DIR = load_directory()

def get_embedded_url(tweet):
	urlcount = 0
	url_list = []
	if len(tweet['entities']['urls']) > 0:
		for entry in tweet['entities']['urls']:
			url = entry['expanded_url']
			if url is not None:
				url = url.replace('\\', '')
				url_list.append(url)
				urlcount += 1
				
	if urlcount == 0 and \
		'retweeted_status' in tweet and \
		len(tweet['retweeted_status']['entities']['urls']) > 0:  # ['extended_tweet']
		for entry in tweet['retweeted_status']['entities']['urls']:
			url = entry['expanded_url']
			if url is not None:
				url = url.replace('\\', '')
				url_list.append(url)
				urlcount += 1

	if urlcount == 0:
		# use regular expression to manually extract urls
		# from the text
		searchObj = re.search(r'http\S+', tweet['text'], re.M | re.I)
		if searchObj:
			url = searchObj.group()
			url_list.append(url)
		#pprint.pprint(tweet)
	#print url_list
	return url_list

class StdOutListener(StreamListener):
	"""A listener handles tweets are the received from the stream.
	This is a basic listener that just prints received tweets to stdout.
	"""

	def __init__(self, api=None, total_num_tweets = 10, save_file = True, print_info = True, save_common = False):
		super(StdOutListener, self).__init__()
		self.num_tweets = 0
		self.total_num_tweets = total_num_tweets
		self.counter = Counter()
		self.save_file = save_file
		self.print_info = print_info
		self.save_common = save_common
		if os.path.isfile(filename):
			print "load user from disk..."
			self.unique_user = get_unique_user()
		else:
			self.unique_user = set([])
	def on_data(self, data):
		global f
		data_string = json.loads(data)     # convert unicode type to a dict type

		""" 
			Write each tweet as a new line of json into
			file f

		"""
		try:
			self.num_tweets += 1
			if "text" in data_string:
				if self.print_info:
					print self.num_tweets
					#print data_string["text"].encode('utf-8', 'ignore')  # extract the text
					print data_string['user']['screen_name']
					#print data_string["source"]
					print
					if len(data_string['entities']['urls']) > 0:
						for entry in data_string['entities']['urls']:
							print entry['expanded_url']
				
					
					if 'retweeted_status' in data_string and len(data_string['retweeted_status']['entities']['urls']) > 0: #['extended_tweet']
						print ">>>> RETWEET >>>>>"
						for entry in data_string['retweeted_status']['entities']['urls']:
							print entry['expanded_url']
				
					if "coordinates" in data_string:# and data_string['coordinates'] is not None:
						pprint.pprint(data_string['coordinates'])	
				# for url in get_embedded_url(data_string):
				# 	self.counter[urlparse.urlparse(url).netloc] += 1

				#print data_string["source"]
				if self.save_file:
					#json.dumps(r)
					if data_string['user']['id'] not in self.unique_user:
						self.unique_user.add(data_string['user']['id'])
						json.dump(data_string['user'], f)
						f.write('\n')
						f.flush()

				if self.num_tweets % 1000 == 0:
					print "number of users collected: %d" %(len(self.unique_user))
		
		except Exception, e:
			print e
			print "REACH LIMIT !!!" 
			print
			print
			#self.num_tweets = 9999999
			pass

		if self.num_tweets < self.total_num_tweets:
			return True
		else:
			return False

	def on_error(self, status):
		print(status)
		time.sleep(10)
		print ("try again")
		return True

   	def on_timeout(self):
   		print ('Timeout...')
   		time.sleep(10)
   		return True  # continue listening


human = 0
human_source = [ "Twitter for iPhone", "Twitter for Android", "Twitter for Websites", "Twitter for iPad", "TweetDeck", "Facebook", "Google", "publicize.wp.com", "Twitter for Android Tablets", "www.apple.com", "BlackBerry", "Windows Phone", "Mobile Web", "Twitter for Mac", "tumblr", "instagram", "linkedin"]
bot_source = ["ifttt", "twitterfeed", "dlvr.it", "hootsuite", "tweetadder", "roundteam", "linkis", 
					"bufferapp", "www.forcetweet", "Twitter Web Client"]

def checksource(source):
	global count, human
	print (count)
	print (human)
	count += 1
	# if count % 100 == 0:
	# 	print ("total tweet is " + str(count))
	# 	print ("human tweet is " + str(human))
	for src in human_source:
		if src in source:
			human += 1
			return True
	return False


def collect(keyword = None, filename = None, num_tweets = 10, save_file = True, print_info = True, save_common = False):
	global f
	if os.path.isfile(filename):
		print('file already exist!')
		
		#return
	f = open(filename, 'a+')
	l = StdOutListener(total_num_tweets = num_tweets, save_file = save_file, print_info = print_info, save_common = save_common)
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)

	stream = Stream(auth, l)

	#GEOBOX_WORLD = [-29.1535754,-105.4302716,28.9615055,-90.8843738]
	#keyword = ["CNN,BBC,NBC,FOX,update"]
	#keyword = ["java", "python", "mongodb", "matlab", "json", "c++", "jquery", "css", "Ruby", "Rail"]
	kw = keyword

	# other option: locations track=keyword
	stream.filter(track=kw)
	#stream.filter(track=kw, languages=['en'])       

def get_filename(keyword):
	prefix = "_".join(keyword)
	return DATA_DIR + prefix + '_tweet.json' 
	
def load_user():
	with open(filename, 'r') as f:
		for line in f:
			#print line
			t = json.loads(line)
			#t = json.loads(t)
			#pprint.pprint(t)
			print t['screen_name']

def get_unique_user():
	userset = set([])
	with open(filename, 'r') as f:
		for line in f:
			t = json.loads(line)
			userset.add(t['id'])
	print len(userset)
	return userset

if __name__ == '__main__':
	#DATA_DIR = 'raw_data/'
	# 
	# goo is VERY SPAMMY, porn,
	# viid is Trump!!
	# bit a lot of stuff, mixed
	# ift also a lot (collecting on clear now... )
	# dlvr.it also mixed (next one on CLEAR after ift)
	# ow maybe good, worth trying
	# dld maybe, worth trying, mixed too (update: very good, lots of uber stuff, collected from local computer)
	# etsy good ads, volume kinda low
	# 
	###
	# update: 2/19, try some new urls
	# tiny url (running on CLEAR now)
	# ow ly
	# fb me (next on CLEAR..)
	# youtu be (too many)
	# fllwrs (spam followers service)
	# buff.ly
	# rover ebay com (ebay selling stuff)
	# hyperurl.co
	# ln is (should try it on CLEAR!!!)
	# amzn to (did not finish collecting, low volume...)
	# sproutbuy

	"""
		This script is special purpose, it finds and stores all
		users who are tweeting from one URL
	"""
	keyword = ["du3a org", "d3waapp org", "zad-muslim com", "7asnat com", "ghared com"]

	prefix = "_".join(keyword)
	prefix = prefix.replace('//', '')
	prefix = "du3a"
	filename = DATA_DIR + prefix + '_all_user_info.json'
	collect(keyword = keyword, filename = filename, num_tweets = 1000000000, save_file = True, print_info = False, save_common = False)
	#load_user()


