import json
import urlparse
import pickle
import collections
import datetime
import time
import os
from collections import Counter
import numpy as np
#import matplotlib
#from matplotlib import pyplot as plt
import sys
sys.path += ['/Users/zc/Documents/twitter_research/github_code/twitter_research/src/plot/', '../']
#import timeline_new
import find_suspended 
import pprint
#name = 'du3a_all_user_info'
name = 'savingzev_all_user_info'


def load_info(filename, field = None, inpair = False):
    res = []
    count = 1
    with open(filename, 'r') as f:
        for line in f:
            if count % 10000 == 0:
            	print count
            	#return res
            count += 1
            t = json.loads(line)
            if field:
            	if inpair:
            		res.append((t['screen_name'], t[field]))
            	else:	
            		res.append(t[field])
            else:
            	res.append(t)
    return res

def find_nullable_field(filename, field = None):
    res = []
    count = 1
    c = Counter()
    with open(filename, 'r') as f:
        for line in f:
            if count % 10000 == 0:
            	print count
            	#return res
            count += 1
            t = json.loads(line)
            if field in t and t[field] is not None:
            	#print t[field]
            	c[t[field]] += 1
            	res.append((t['screen_name'], t[field]))
    
    pprint.pprint(c.most_common(100))
    return res

def plot_histogram(x, title = '', xlabel = '', ylabel = '', log = False, filename = None):
	if log:
		plt.hist(x, bins=np.logspace(0.0, 3.0, 25))
		plt.gca().set_xscale("log")
	else:
		plt.hist(x, bins=200, normed=False)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
	plt.grid(True)
	if filename:
		plt.savefig(filename)
	plt.show()


def plot_created_time(filename):
	count = 1
	date = []
	with open(filename, 'r') as f:
		for line in f:
			if count % 1000 == 0:
				print count
			count += 1
			t = json.loads(line)
			date.append(datetime.datetime.strptime(t['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))

	timeline_new.plotTimeFreq(date, title = name + '_created_time', filename = name + '_created_time')

def plot_location():
	attribute = 'location'
	location_info = load_info(name + '.json', attribute, inpair = True)
	
	c = Counter()
	for i in location_info:
		c[i[1]] += 1 

	for entry in c.most_common(50):
		print entry[0], entry[1]

def find_withheld_user():
	attribute = 'screen_name'
	user_info = load_info(name + '.json', attribute, inpair = False)
	#print user_info
	result = find_suspended.check_status(user_info, screen_name = True)
	result_serializable = {'deleted': list(result['deleted']),
		   'protected': list(result['protected']),
		   'suspended': list(result['suspended']),
		   'normal': list(result['normal'])}
	json.dump(result_serializable, open(name + '_user_status.json', 'w'))

def get_user_status():
	dic = json.load(open(name + '_user_status.json', 'r'))
	print 'deleted ', len(dic['deleted'])
	print 'protected', len(dic['protected'])
	print 'suspended', len(dic['suspended'])
	print 'normal', len(dic['normal'])
	pprint.pprint(dic['normal'])

def status_histogram():
	attribute = 'friends_count'
	statuses_count = load_info(name + '.json', attribute, inpair = True)
	sorted_list = sorted(statuses_count, key=lambda x: x[1], reverse = True)
	print sorted_list[:40]
	values = [i[1] for i in statuses_count]
	mean = sum(values) * 1.0 / len(values)
	std = np.std(values)
	print 'total users %d' %(len(values))
	print 'mean is %f' %(mean)
	print 'std is %f' %(std)


	threshold = 0.5
	second_arg = '_below_' + str(threshold).replace('.', '') + '_std'
	print second_arg

	# + '_below_1_std'

	plot_histogram(values, title = 'Distribution of ' + attribute, 
					xlabel = attribute, ylabel = 'Number of accounts',
					log = False, filename = name + '_' + attribute)

	plot_histogram([i for i in values if i < mean+std*threshold], title = 'Distribution of ' + attribute + second_arg, 
					xlabel = attribute, ylabel = 'Number of accounts',
					log = False, filename = name + '_' + attribute + second_arg)

#status_histogram()
#find_nullable_field(filename = name + '.json', field = 'url')
#plot_created_time(filename = name + '.json')
#plot_location()
#find_withheld_user()
get_user_status()
