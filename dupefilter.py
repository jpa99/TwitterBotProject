# -*- coding: utf-8 -*-
import datetime 
import pickle
import collections
from collections import defaultdict
import operator
import pprint
import string
import os
import json
import re
import random
import urlparse
import crawler

def clean_text(text):
	if "RT @" == text[:4]:
		# replace the first occurrance
		text = re.sub(r'@[^ \t\n\r\f\v]*', " ", text, 1)
		# remove RT symbol
		text = text.replace("RT", "", 1)
	# remove new lines
	text = text.replace("\n", " ")
	# remove tabs
	text = text.replace("\t", " ")
	# remove &gt symbol
	text = text.replace("&gt", " ")
	# remove &lt symbol
	text = text.replace("&lt", " ")
	# remove punctuation
	for punc in string.punctuation:
		text = text.replace(punc,"")
	# remove url
	text = re.sub(r'http\S+', " ", text)
	text = re.sub(r'https\S+', " ", text)
	text = text.strip()
	return text.lower()

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



class DupInfo(object):
	"""Find and store duplicate tweets from a dataset"""

	def __init__(self, prefix, startover = False):
		self.source = defaultdict(int)
		self.url = defaultdict(int)
		self.user = set([])
		self.result = []
		self.PREFIX = prefix
		self.startover = startover

	def find_duplicate_tweet(self, collection, cutoff = 20, collect_url_only = False):
		# if the complete file already exists, do nothing here.
		if os.path.isfile(self.PREFIX + 'dupfilter_suspicious_group_info.p') and (not self.startover):
			return 
		
		########## for record keeping
		for tweet in collection:
			dt = datetime.datetime.strptime(tweet[u'created_at'], '%a %b %d %H:%M:%S +0000 %Y')  # format the time
			start_time = dt
			break

		month = dt.month
		day = dt.day
		hour = dt.hour
		tweet_count = 0
		user_count = set([])
		##############

		text_hashtable = {}
		user_hashtable = {}
		url_hashable = {}
		status_hashable = {}

		# collection is an iterator
		for tweet in collection:
			if tweet_count % 1000 == 0:
				print "%d tweets processed" %(tweet_count)
			tweet_count += 1
			user_count.add(tweet[u'user'][u'id'])

			if collect_url_only:
				if not (len(tweet['entities']['urls']) > 0 or 
				   ('retweeted_status' in tweet and len(tweet['retweeted_status']['entities']['urls']) > 0)):
					continue
				else:
					flag = False
					url_list = get_embedded_url(tweet)
					if not url_list:
						continue
					for word in ['viid.', 'goo.', 'bit.', 'dld.', 'ift.', 'dlvr.']:
						for url in url_list:
							if word in url:
								flag = True
					if not flag:
						continue
			

			text = clean_text(tweet[u'text'])
			if text in text_hashtable:
				text_hashtable[text] += 1
				user_hashtable[text].add(tweet[u'user'][u'id'])
			else:
				text_hashtable[text] = 1
				user_hashtable[text] = set([])
				user_hashtable[text].add(tweet[u'user'][u'id'])
				url_hashable[text] = defaultdict(int)
				status_hashable[text] = {'retweet':0, 'original':0}


			# if 862809709 == tweet['user']['id']:
			# #if 'lyftuber experts share 3 favorite' in tweet[u'text']:
			# 	pprint.pprint(tweet)
			# 	exit()
			urlcount = 0
			# update embedded url
			if len(tweet['entities']['urls']) > 0:
				for entry in tweet['entities']['urls']:
					url = entry['expanded_url']
					if url is not None:
						url = url.replace('\\', '')
						urlcount += 1
						url_hashable[text][url] += 1

			if urlcount == 0 and \
				'retweeted_status' in tweet and \
				len(tweet['retweeted_status']['entities']['urls']) > 0:  # ['extended_tweet']
				for entry in tweet['retweeted_status']['entities']['urls']:
					url = entry['expanded_url']
					if url is not None:
						url = url.replace('\\', '')
						urlcount += 1
						url_hashable[text][url] += 1

			if urlcount == 0:
				# use regular expression to manually extract urls
				# from the text
				searchObj = re.search(r'http\S+', tweet['text'], re.M | re.I)
				if searchObj:
					url = searchObj.group()
					url_hashable[text][url] += 1
				#pprint.pprint(tweet)
			# print url
			# update original/retweet status
			if 'retweeted_status' in tweet:
				status_hashable[text]['retweet'] += 1
			else:
				status_hashable[text]['original'] += 1

		# record the end time
		end_time = datetime.datetime.strptime(tweet[u'created_at'], '%a %b %d %H:%M:%S +0000 %Y')
		# update the result
		sorted_text = sorted(text_hashtable.items(), key=operator.itemgetter(1), reverse=True)
		sorted_text = [s for s in sorted_text if s[1] > cutoff]
		print "duplicate text"
		pprint.pprint(sorted_text)
		_id_ = 1
		for text, count in sorted_text:
			# In turkish collection, many tweets have no texts at all,
			# and they are usually random in nature
			if text != '':
				self.result.append({'month': month, 'day':day, 'hour':hour,
								'url':url_hashable[text], 'status': status_hashable[text], 
								'user_ids':user_hashtable[text], 'text':text, 'count':count, 
								'id': _id_})
			_id_ += 1

		pickle.dump(self.result, open(self.PREFIX + 'dupfilter_suspicious_group_info.p','wb'))
		
		metadata = {'num_tweet': tweet_count, 'num_user': len(user_count), 
		'start_time':start_time, 'end_time':end_time}

		pickle.dump(metadata, open(self.PREFIX + 'metadata.p','wb'))
		
	def get_metadata(self, variable = None):
		dic = pickle.load(open(self.PREFIX + 'metadata.p','rb'))
		if not variable:
			return dic
		return dic[variable]

	def get_tweet(self, collection, userlist, only_number = False, field = 'id'):
		userlist = set(userlist)
		count = 0
		result = []
		tweet_count = 0
		
		for tweet in collection:
			if tweet_count % 1000 == 0:
				print "%d tweets processed" %(tweet_count)
			tweet_count += 1
			if 'user' in tweet and tweet['user'][field] in userlist:
				count += 1
				result.append(tweet)
		if only_number:
			return count
		else:
			return result

	def get_user_id(self, date, rank):
		month, day, hour = date
		dic = pickle.load(open(self.PREFIX + 'dupfilter_suspicious_group_info.p','rb'))
		result = {}
		for entry in dic:
			if entry['month'] == month and entry['hour'] == hour and entry['day'] == day:
				result[(tuple(entry['user_ids']), entry['text'])] = entry['count']
		
		sorted_result = sorted(result.items(), key=operator.itemgetter(1), reverse=True)
		print rank
		print sorted_result
		if rank > len(sorted_result):
			rank = len(sorted_result)
		print sorted_result[rank - 1][0][1]
		return sorted_result[rank - 1][0][0]


	def filter_duplicate_group(self):
		result = []
		dic = pickle.load(open(self.PREFIX + 'dupfilter_suspicious_group_info.p','rb'))
		print "num of duplicate groups: ", len(dic)
		if not os.path.isfile(self.PREFIX + 'duplicate_spam_group.json') or (self.startover):
			# no need to use timeline API, we can start to infer
			# do more on large group (change to a dic)
			# get their urls, expand them, choose top
			# auto classify
			large_group = []
			# user timeline API
			small_group = []
			group_include = set([])
			### 
			for i in range(0, len(dic) -1):
				if i in group_include:
					continue
				first_create = True
				for j in range(i+1, len(dic)):
					if j not in group_include:
						if first_create:
							result = dic[i]['user_ids'].intersection(dic[j]['user_ids'])
						else:
							result1 = dic[i]['user_ids'].intersection(dic[j]['user_ids'])
							result = large_group[-1]['user_ids'].intersection(dic[j]['user_ids'])
							assert(len(result1) <= len(result))

						ratio = len(result) * 1.0 / len(dic[j]['user_ids'])
						#if ratio >= 0.5:
						if len(result) > 5 or ratio >= 0.5:
							if first_create:
								group_info = {'user_ids': dic[i]['user_ids'].union(dic[j]['user_ids']),
											  'subgroup': [i,j],
											  'ratio': [ratio],
											  'text': [dic[i]['text'], dic[j]['text']],
											  'url': dict(dic[i]['url'].items() + dic[j]['url'].items())}
								large_group.append(group_info)
								group_include.add(i)
								first_create = False
							else:
								large_group[-1]['user_ids'] = large_group[-1]['user_ids'].union(dic[j]['user_ids'])
								large_group[-1]['text'].append(dic[j]['text'])
								large_group[-1]['subgroup'].append(j)
								large_group[-1]['url'] = dict(large_group[-1]['url'].items() + dic[j]['url'].items())
								large_group[-1]['ratio'].append(ratio)
							group_include.add(j)

				if first_create:
					# If a few users create most number of tweets, 
					# 
					if len(dic[i]['user_ids']) < 10 and dic[i]['count'] * 1.0 / len(dic[i]['user_ids']) > 3.0:
						group_info = {'user_ids': dic[i]['user_ids'],
											  'subgroup': [i],
											  'ratio': [1],
											  'text': [dic[i]['text']],
											  'url': dict(dic[i]['url'].items())}
						large_group.append(group_info)
						group_include.add(i)
					else:
						small_group.append(dic[i])

			# the last group is left un-examined, let's check
			# its status here
			if len(dic) -1 not in group_include and len(dic) > 0:
				small_group.append(dic[-1])				
			
			print "len large_group: ", len(large_group)
			print "len small_group: ", len(small_group)
			print [len(i['user_ids']) for i in large_group]
			
			# TODO: need to figure out the url behind each group
			print "Now let's get top url ...\n..."
			for i in large_group:
				print len(i['user_ids'])
				#print [len(dic[gg]['user_ids'].intersection(set.union(*[dic[g]['user_ids'] for g in i['subgroup'] if g != gg]))) * 1.0 / len(dic[gg]['user_ids']) for gg in i['subgroup']]
			 	#print [1.0] + i['ratio']
			 	
				# extract expanded url
				top_one_expanded = []
				all_url = list(i['url'])[:]
				random.shuffle(all_url)
				for url in all_url:
					if len(top_one_expanded) < 5:
						try:
							new_url_list = crawler.unshorten_url(url, 1, {})
							top_one_expanded.append(new_url_list)
						except Exception, e:
							print e
							print "Cannot expand url"
				url_list = []
				for entry in top_one_expanded:
					if entry != {}:
						full_link = entry[max(entry.keys())]
						url_list.append(urlparse.urlparse(full_link).netloc)
				
				if url_list != []:
					#website = collections.Counter(url_list).most_common(1)[0][0]
					website = collections.Counter(url_list).most_common()
				else:
					if len(i['url']) > 2:
						website = random.sample(i['url'], 2)
					else:
						website = i['url']
				i['top_one_website'] = website
				print "..... top url ....."
				pprint.pprint(website)
				
			large_all = sum([len(i['user_ids']) for i in large_group])  # + sum([len(i) for i in small_group])
			try:
				large_unique = len(set.union(*[i['user_ids'] for i in large_group]))
			except Exception,e:
				print e
				large_unique = 0
				print 'large_all is %d, large_unique is %d' %(large_all, large_unique)
				print self.get_metadata('num_user')
				print "% user from large group..."
				print large_unique * 1.0 / self.get_metadata('num_user')
				print 
			
			"""
				Save duplicate group, if duplicate_group.json does not exist
			"""
			duplicate_group = {}
			k = 1
			for g in large_group:
				info = {}
				info['spam_user'] = list(g['user_ids'])
				info['screen_name'] = ['\nscreen_name is NOT AVAILABLE \n for duplicate group\n\n']
				info['spam_url'] = g['url'] 
				info['top_one_website'] = g['top_one_website'] 
				info['subgroup'] = g['subgroup'] 
				duplicate_group['duplicate_group_' + str(k)] = info
				k += 1
			json.dump(duplicate_group, open(self.PREFIX + 'duplicate_spam_group.json', 'w'))
			print "finish dumping json ..."
		########### return none-duplicate groups #########
		duplicate_group = json.load(open(self.PREFIX + 'duplicate_spam_group.json', 'r'))
		print "loading duplicate_group..."
		id_exclude = set([item for i in duplicate_group.values() for item in i['subgroup']])
		result = []
		
		for i in range(0, len(dic) -1):
			if i not in id_exclude:
					entry = dic[i]
					name = '_'.join([str(entry['month']), str(entry['day']), str(entry['hour'])]) + "_" + self.clean_filename(entry['text'][:40]) + '_'
					result.append({'userlist': entry['user_ids'], 'url': entry['url'],
							   'filename': name, 'count': entry['count']})
		return result


	def get_suspicious_user_group(self, filter_function = None, url_based = False):
		if url_based:
			return self.filter_duplicate_group()
		dic = pickle.load(open(self.PREFIX + 'dupfilter_suspicious_group_info.p','rb'))
		print len(dic)
		result = []
		for entry in dic:
			if filter_function(entry):
					name = '_'.join([str(entry['month']), str(entry['day']), str(entry['hour'])]) + "_" + self.clean_filename(entry['text'][:40]) + '_'
					result.append({'userlist': entry['user_ids'], 'url': entry['url'],
							   'filename': name, 'count': entry['count']})
		print len(result)
		return result

	def clean_filename(self, name):
		for c in string.punctuation:
			name = name.replace(c,"")
		name = name.replace(" ","_")
		return name
		
	def save_user_info(self, collection):
		if os.path.isfile(self.PREFIX + 'user_info.json'):
			print "file already exists......"
			#return 

		user_info = defaultdict(lambda: {})
		tweet_count = 0
		
		for tweet in collection:
			if tweet_count % 1000 == 0:
				print "%d tweets processed" %(tweet_count)
			tweet_count += 1
			if int(tweet['user']['id']) not in user_info:
				user = int(tweet['user']['id'])
				user_info[user]['id'] = tweet['user']['id']
				user_info[user]['screen_name'] = tweet['user']['screen_name']
				user_info[user]['created_at'] = tweet['user']['created_at']
				user_info[user]['lang'] = tweet['user']['lang']
				user_info[user]['verified'] = tweet['user']['verified']
				user_info[user]['statuses_count'] = tweet['user']['statuses_count']
				user_info[user]['friends_count'] = tweet['user']['friends_count']
				user_info[user]['followers_count'] = tweet['user']['followers_count']
				user_info[user]['profile'] = tweet['user']['profile_image_url']  # [:-10] + 'bigger.jpg'
				
		json.dump(user_info, open(self.PREFIX + 'user_info.json', 'w'))

if __name__ == '__main__':
	pass


