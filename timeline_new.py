# -*- coding: utf-8 -*-
"""
	@
    @Description:   This script (new version) generates a graph that shows the
    @               distribution of tweets by date
    @               
    @               
    @Author:        Joe Chen
    @Last modified: 01/19/2016 
"""
import ujson as json
import time
import datetime 
import itertools
from pymongo import MongoClient
import numpy as np
import matplotlib
#matplotlib.use('Agg')
from matplotlib import rcParams
from matplotlib import pyplot as plt

def createListFromJson(filename):
	"""Every line is a json dictionary."""
	# inputJson=open(filename, "r").read()
	# jsonFields=json.loads(inputJson)
	print "start loading json data"
	count = 0

	with open(filename) as f:
		for line in f:
			tweet = json.loads(line)

			if count % 10000 == 0:
				print count
			count += 1
			if 'created_at' in tweet:
				created_at = tweet[u'created_at']
				yield(created_at)


def createList(collection):
	count = 0	             # count total number of tweets
	
	for tweet in collection.find():
			count += 1
			if (count % 5000 == 0):
				# keep track of how many tweets have been processed
				print count
			if 'created_at' not in tweet:
				print tweet
				continue
			created_at = tweet[u'created_at']
			yield(created_at)  					# use a generator 



def formatTime(creat_time, 
	start_time=datetime.datetime(1970, 1, 1), 
	end_time=datetime.datetime(2050, 1, 1),
	days_to_skip=[]):
	datelist = []                            	# store datetime objects into a list
	
	for everytime in creat_time:
		flag = False
		dt = datetime.datetime.strptime(everytime, '%a %b %d %H:%M:%S +0000 %Y')  # format the time
		if dt < end_time and start_time < dt:
			""" 
				Because the event dates are based on HK time,
				if you want to align the timezone to HongKong time, 
				you can change the argument to (hours = 8), 
				GMT/UTC + 08:00 hour
			"""
			for day in days_to_skip:
				
				if day[0] == dt.year and day[1] == dt.month and day[2] == dt.day:
					flag = True
					break
			if not flag:
				datelist.append(dt + datetime.timedelta(hours = 0))
	return datelist


def plotTimeFreq(datelist, title = 'Distribution of tweets by day', filename=None):	
	datelist = sorted(datelist)
	OY = []                # store y values (number of tweets)
	OX = []                # store x values (string of dates )

	newdate = [list(g) for k, g in itertools.groupby(datelist, key=datetime.datetime.toordinal)]
	for x in xrange(0, len(newdate)):
		# print len(newdate[x]), newdate[x][0].date()
		OY.append(len(newdate[x]))
		OX.append(str(newdate[x][0].date()))

	fig = plt.figure()
	matplotlib.rcParams.update({'font.size': 10})#28
	plt.ylabel('Number of tweets')                # add titles and label
	plt.xlabel('Date')
	plt.title(title)
	ind = np.arange(len(OY))

	plt.bar(ind, OY, width=0.80)
	plt.xticks(ind, OX, rotation=80)    		    # add date labels on x-axis

	# store a list of event days
	"""include event dates specified by Prof. Stoll"""
	# event_days = [[2014, 10, 6],[2014, 10, 9],[2014, 10, 13],[2014, 10, 14],[2014, 10, 15],   
	# 			[2014, 10, 17],[2014, 10, 21],[2014, 11, 13],[2014, 11, 15],[2014, 11, 18],
	# 			[2014, 11, 26],[2014, 11, 30],[2014, 12, 1],[2014, 12, 2]]

	# draw each event as a vertical line
	# for day in event_days:
	# 	event_day = datetime.date(day[0], day[1], day[2])
	# 	day_diff = event_day -  first_day       	# find the difference
	# 	plt.axvline(x = day_diff.days + 0.5 ,color=colors[color_index],ls='-', linewidth=4)
	# 	count += 1
	# 	color_index += 1
	
	fig.set_size_inches(55, 12)  # (34, 18)
	# if filename != None:
	plt.savefig(filename)
	plt.show()

# make a histogram
def plot_histogram_botornot_miniplot(x, myrange = None, title = None, filename = None):
	#rcParams.update({'font.size': 16})
	# This is  the colormap I'd like to use.
	cm = plt.cm.get_cmap('RdYlBu_r')
	num_bins = 50

	fig, axes = plt.subplots(3, 3, figsize=(12, 9)) 
	for i in range(0,9):
		ax = axes[i / 3, i % 3]
		n, bins, patches = ax.hist(x[i], num_bins, normed=False, facecolor='green', range = myrange[i], alpha=0.5)
		bin_centers = 0.5 * (bins[:-1] + bins[1:])
		# scale values to interval [0,1]
		col = bin_centers - min(bin_centers)
		col /= max(col)
		for c, p in zip(col, patches):
			plt.setp(p, 'facecolor', cm(c))
		# plot two vertical lines at 0.4 and 0.6
		ax.axvline(x=0.4, linewidth=4, ls='dashed')
		ax.axvline(x=0.6, linewidth=4, ls='dashed')
		ax.set_title(title[i])

	xlabel = 'BotOrNot score'
	ylabel = 'Number of Tweets'
	fig.text(0.5, 0.04, xlabel, ha='center')
	fig.text(0.04, 0.5, ylabel, va='center', rotation='vertical')

	#plt.subplots_adjust(left=0.15)
	if filename:
		plt.savefig(filename)
	print 'about to show plot...'
	plt.show()


# make a histogram
def plot_histogram_botornot(x, myrange = None, title = None, filename = None):
    num_bins = 50
    n, bins, patches = plt.hist(x, num_bins, normed=False, facecolor='green', range = myrange, alpha=0.5)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    rcParams.update({'font.size': 16})
    # This is  the colormap I'd like to use.
    cm = plt.cm.get_cmap('RdYlBu_r')
    # scale values to interval [0,1]
    col = bin_centers - min(bin_centers)
    col /= max(col)
    for c, p in zip(col, patches):
    	plt.setp(p, 'facecolor', cm(c))

    # plot two vertical lines at 0.4 and 0.6
    plt.axvline(x=0.4, linewidth=4, ls='dashed')
    plt.axvline(x=0.6, linewidth=4, ls='dashed')

    plt.xlabel('BotOrNot score')
    plt.ylabel('Number of Tweets')
    if title:
    	plt.title(title)
    #plt.subplots_adjust(left=0.15)
    if filename:
    	plt.savefig(filename)
    print 'about to show plot...'
    plt.show()

def plot_histogram(x, title = '', log = False, filename = None):
	if log:
		plt.hist(x, bins=np.logspace(0.0, 3.0, 25))
		plt.gca().set_xscale("log")
	else:
		plt.hist(x, bins=100, normed=False)
	plt.xlabel('Number of tweets')
	plt.ylabel('Number of Users')
	plt.title(title)
	plt.grid(True)
	if filename:
		plt.savefig(filename)
	plt.show()

def plot_xybar(x, y, OX = None, ind = None, xlabel = '', ylabel = '', title = '', filename = None):
	plt.bar(x, y, color = 'b', edgecolor = 'b')
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
	if OX:
		plt.xticks(ind, OX, rotation=80)
	#plt.grid(True)
	if filename:
		plt.savefig(filename)
	plt.show()

def plot_xybar_miniplot(x, y, OX, ind, title, xlabel='', ylabel='', filename = None):
	# xlabel = '', ylabel = ''
	print x 
	print y
	print OX
	print ind
	
	fig, axes = plt.subplots(3, 3, figsize=(16, 12)) 
	print title
	matplotlib.rcParams.update({'font.size': 16})
	for i in range(0,9):
		ax = axes[i / 3, i % 3]
		ax.bar(x[i], y[i], color = 'b', edgecolor = 'b') 
		#ax.xlabel(xlabel)
		#ax.ylabel(ylabel)
		print title[i]
		ax.set_title(title[i], fontsize=20)
		#print ind[i], 
		ax.set_xticks(ind[i])  # location
		ax.set_xticklabels(OX[i])  # lables

		#ax.set_xticks(np.array(OX[i]).astype(np.float))

	fig.text(0.5, 0.04, xlabel, ha='center', fontsize=24)
	fig.text(0.04, 0.5, ylabel, va='center', rotation='vertical', fontsize=24)
	fig.subplots_adjust(wspace=.2)
	#plt.grid(True)
	if filename:
		plt.savefig(filename)
	plt.show()

def plot_dot(x_list, y_list, title = '', filename = None, withtick = True):
	# x axis is the date
	base = datetime.datetime(2016, 7, 15)
	date_list = [base + datetime.timedelta(days=x) for x in range(0, 77)]
	matplotlib.rcParams.update({'font.size': 24})
	fig = plt.figure()
	plt.ylim(0, len(y_list) + 1)
	OX = []
	for x in xrange(0, len(date_list)):
		#OY.append(2)
		#OY2.append(20)
		OX.append(str(date_list[x].date()))

	ind = np.arange(len(OX))
	#plt.plot(ind, OY, 'bo')
	#plt.plot(ind, OY2, 'bo')
	#plt.plot([1,2,3], [3,5,6], 'bo')
	for X, Y in zip(x_list, y_list):
		plt.plot(X, Y, marker='o', linestyle='-', color='b')
	if withtick:
		plt.xticks(ind, OX, rotation=80)    		    # add date labels on x-axis
	
	plt.xlabel('time elapse since %s' %(datetime.datetime.utcnow()))
	plt.ylabel('sampled users')
	plt.title(title)
	fig.set_size_inches(34, 18)
	if filename:
		plt.savefig(filename)
	#plt.show()
	

def plot_pdf(x):
	print len(x)
	hist, bins = np.histogram(x, range = (1,1000), bins=5, normed=False)
	#bin_centers = (bins[1:]+bins[:-1])*0.5
	new_hist = []
	accu = 0
	print len(bins)
	print len(hist)
	for h in hist:
		accu += h
		new_hist.append(accu)
	new_hist.append(h)
	print len(bins)
	print len(new_hist)
	plt.plot(bins, new_hist)
	plt.show()

def plot_pie_miniplot(labels=[], sizes=[], titles=[], filename = None):
	fig, axes = plt.subplots(3, 3, figsize=(12, 10)) 
	#colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral', 'red', 'gray']
	matplotlib.rcParams.update({'font.size': 20})
	for i in range(0,9):
		ax = axes[i / 3, i % 3]    
		print "SIZE", sizes[i]
		print "LABEL", labels[i]
		patches, texts = ax.pie(sizes[i], startangle=30)
		if i == 3:
			ax.legend(patches, labels[3], frameon=True, loc=(-0.62, -0.5),prop={'size':18})
		ax.axis('equal')
		ax.set_title(titles[i])
	
	#plt.figlegend(lines, labels, loc = 'lower center', ncol=5, labelspacing=0.1 )
	#plt.legend(axes[2,2], labels, loc=(0.7, 0.008))  # loc = 'lower left'
	
	fig.subplots_adjust(wspace=.2)
	if filename:
		plt.savefig(filename)
	plt.show()	
	


def plot_pie(labels, sizes, filename = None):
	#labels = ['Cookies', 'Jellybean', 'Milkshake', 'Cheesecake']
	#sizes = [38.4, 40.6, 20.7, 10.3]
	#colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral']
	matplotlib.rcParams.update({'font.size': 18})
	patches, texts = plt.pie(sizes, shadow=False, startangle=90)
	plt.legend(patches, labels, loc=(0.7, 0.008))  # loc = 'lower left'
	plt.axis('equal')
	#plt.tight_layout()
	if filename:
		plt.savefig(filename)
	plt.show()

def makeplot(collection, filename):
	data = formatTime(createList(collection))
	plotTimeFreq(data, filename=filename)

# fast make, with data already loaded into memory
def make_parameter_sweeping_plot_all_URL_shorteners():
	x=[[1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9]]
	y=[[2597, 1766, 1315, 999, 815, 696, 572, 421, 296], [414, 381, 359, 345, 315, 304, 291, 253, 199], [3278, 2706, 2264, 1845, 1487, 1194, 988, 857, 707], [1781, 1380, 1132, 947, 837, 710, 577, 495, 391], [720, 567, 481, 425, 374, 321, 273, 233, 184], [7191, 6809, 6535, 6261, 6008, 5785, 5576, 5285, 4775], [1360, 1184, 1070, 982, 940, 894, 788, 670, 632], [1032, 892, 829, 807, 760, 705, 600, 531, 480], [419, 293, 211, 170, 147, 129, 110, 91, 67]]
	OX=[['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'], ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'], ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'], ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'], ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'], ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'], ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'], ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'], ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9']]
	ind=[np.arange(len(OX)) + 1.4 for _ in range(9)]
	#ind=[range([1, 2, 3, 4, 5, 6, 7, 8, 9]), array([1, 2, 3, 4, 5, 6, 7, 8, 9]), array([1, 2, 3, 4, 5, 6, 7, 8, 9]), array([1, 2, 3, 4, 5, 6, 7, 8, 9]), array([1, 2, 3, 4, 5, 6, 7, 8, 9]), array([1, 2, 3, 4, 5, 6, 7, 8, 9]), array([1, 2, 3, 4, 5, 6, 7, 8, 9]), array([1, 2, 3, 4, 5, 6, 7, 8, 9]), array([1, 2, 3, 4, 5, 6, 7, 8, 9])]
	title=['bit', 'dld', 'dlvr', 'goo', 'ift', 'lnis', 'ow', 'tinyurl', 'viid']

	plot_xybar_miniplot(x,y,OX,ind,title, xlabel = 'overlap ratio', ylabel = 'number of bot accounts', filename = 'parameter_sweeping/parameter_sweeping_plot_all_URL_shorteners')


def make_parameter_sweeping_plot_all_URL_shorteners_min_dup_factor():
	x = [[2, 3, 4, 5, 6, 7, 8, 9, 10], [2, 3, 4, 5, 6, 7, 8, 9, 10], [2, 3, 4, 5, 6, 7, 8, 9, 10], [2, 3, 4, 5, 6, 7, 8, 9, 10], [2, 3, 4, 5, 6, 7, 8, 9, 10], [2, 3, 4, 5, 6, 7, 8, 9, 10], [2, 3, 4, 5, 6, 7, 8, 9, 10], [2, 3, 4, 5, 6, 7, 8, 9, 10], [2, 3, 4, 5, 6, 7, 8, 9, 10]]
	y = [[834, 696, 608, 548, 514, 471, 437, 418, 409], [331, 304, 295, 254, 240, 226, 225, 224, 210], [1523, 1194, 1045, 942, 900, 852, 801, 742, 714], [837, 710, 605, 563, 550, 542, 538, 519, 515], [404, 321, 290, 269, 254, 238, 213, 204, 201], [5996, 5785, 5717, 5676, 5648, 5620, 5605, 5596, 5592], [941, 894, 773, 682, 674, 673, 673, 673, 673], [763, 705, 636, 585, 558, 543, 541, 535, 531], [161, 129, 110, 99, 89, 79, 73, 68, 61]]
	OX = [['2', '3', '4', '5', '6', '7', '8', '9', '10'], ['2', '3', '4', '5', '6', '7', '8', '9', '10'], ['2', '3', '4', '5', '6', '7', '8', '9', '10'], ['2', '3', '4', '5', '6', '7', '8', '9', '10'], ['2', '3', '4', '5', '6', '7', '8', '9', '10'], ['2', '3', '4', '5', '6', '7', '8', '9', '10'], ['2', '3', '4', '5', '6', '7', '8', '9', '10'], ['2', '3', '4', '5', '6', '7', '8', '9', '10'], ['2', '3', '4', '5', '6', '7', '8', '9', '10']]
	ind = [np.arange(len(OX)) + 2.5 for _ in range(9)]
	title = ['bit', 'dld', 'dlvr', 'goo', 'ift', 'lnis', 'ow', 'tinyurl', 'viid']
	plot_xybar_miniplot(x,y,OX,ind,title, xlabel = 'mininum duplicate factor', ylabel = 'number of bot accounts', filename = 'parameter_sweeping/parameter_sweeping_plot_all_URL_shorteners_min_dup_factor')


if __name__ == '__main__':
		make_parameter_sweeping_plot_all_URL_shorteners_min_dup_factor()
		#plot_histogram_botornot([0.35, 0.38, 0.53, 0.36, 0.81, 0.56, 0.34, 0.33, 0.61, 0.58, 0.16, 0.77, 0.21, 0.22, 0.37, 0.685, 0.23, 0.29, 0.33, 0.81, 0.59, 0.57, 0.4, 0.37, 0.4, 0.52, 0.56, 0.85, 0.31, 0.19, 0.38, 0.56, 0.38, 0.46, 0.32, 0.39, 0.38, 0.58, 0.37, 0.38, 0.2, 0.91, 0.72, 0.51, 0.31, 0.42, 0.42, 0.44, 0.45, 0.78, 0.35, 0.22, 0.52, 0.59, 0.43, 0.46, 0.88, 0.44, 0.23, 0.46, 0.61, 0.46, 0.43, 0.46, 0.47, 0.34, 0.33, 0.25, 0.69, 0.56, 0.69, 0.62, 0.42, 0.51, 0.48, 0.31, 0.74, 0.34, 0.32, 0.58, 0.22, 0.55, 0.35, 0.51, 0.58, 0.39, 0.44, 0.34, 0.48, 0.42, 0.53, 0.47, 0.3, 0.7, 0.69, 0.57, 0.52, 0.39, 0.31, 0.79, 0.45, 0.65, 0.4, 0.43, 0.67, 0.35, 0.34, 0.59, 0.68, 0.54, 0.61, 0.61, 0.27, 0.61, 0.34, 0.67, 0.24, 0.54, 0.39, 0.73, 0.4, 0.61, 0.42, 0.59, 0.45, 0.25, 0.68, 0.41, 0.38, 0.38, 0.67, 0.34, 0.09, 0.33, 0.31, 0.51, 0.61, 0.36, 0.47, 0.64, 0.38, 0.55, 0.64, 0.35, 0.39, 0.58, 0.42, 0.58, 0.49, 0.34, 0.4, 0.39, 0.36, 0.48, 0.45, 0.42, 0.56, 0.43, 0.39, 0.63, 0.62, 0.65, 0.36, 0.46, 0.33, 0.35, 0.28, 0.37, 0.23, 0.41, 0.26, 0.6, 0.27, 0.39, 0.21, 0.29, 0.36, 0.26, 0.65, 0.63, 0.38, 0.31, 0.69, 0.57, 0.43, 0.47, 0.23, 0.43, 0.22, 0.58, 0.34, 0.48, 0.42, 0.59, 0.81, 0.39, 0.29, 0.43, 0.48, 0.58, 0.4, 0.72, 0.23, 0.51, 0.66, 0.42, 0.35, 0.51, 0.57, 0.36, 0.29, 0.69, 0.73, 0.65, 0.29, 0.49, 0.28, 0.37, 0.8, 0.51, 0.21, 0.49, 0.5, 0.44, 0.61, 0.12, 0.16, 0.26, 0.5, 0.55, 0.35, 0.36, 0.38, 0.46, 0.45, 0.57, 0.41, 0.48, 0.34, 0.48, 0.24, 0.47, 0.55, 0.81, 0.35, 0.46, 0.63, 0.3, 0.61, 0.67, 0.49666666666666665, 0.34, 0.3, 0.64, 0.83, 0.41, 0.36, 0.29, 0.66, 0.46, 0.28, 0.52, 0.16, 0.45, 0.57, 0.48, 0.41, 0.41, 0.61, 0.76, 0.52, 0.27, 0.38, 0.65, 0.47, 0.53, 0.25, 0.11, 0.63, 0.58, 0.17, 0.5, 0.59, 0.34, 0.51, 0.26, 0.42, 0.88, 0.44, 0.37, 0.41, 0.57, 0.53, 0.76, 0.65, 0.52, 0.37, 0.37, 0.49, 0.34, 0.66, 0.36, 0.65, 0.6, 0.43, 0.35, 0.44, 0.69, 0.36, 0.88, 0.62, 0.73, 0.35, 0.23, 0.48, 0.45, 0.68, 0.7433333333333333, 0.25, 0.32, 0.72, 0.29, 0.34, 0.67, 0.38, 0.61, 0.47, 0.35, 0.28, 0.815, 0.29, 0.59, 0.41, 0.56, 0.45, 0.4, 0.46, 0.51, 0.22, 0.37, 0.55, 0.63, 0.29, 0.19, 0.32, 0.78, 0.54, 0.38, 0.67, 0.38, 0.73, 0.31, 0.45, 0.6, 0.19, 0.31, 0.52, 0.34, 0.59, 0.54, 0.29, 0.91, 0.46, 0.73, 0.62, 0.56, 0.59, 0.64, 0.64, 0.48, 0.63, 0.6, 0.28, 0.47, 0.62, 0.38, 0.35, 0.3, 0.56, 0.35, 0.54, 0.77, 0.4, 0.46, 0.804, 0.64, 0.49, 0.38, 0.37, 0.57, 0.38, 0.49, 0.29, 0.42, 0.19, 0.38, 0.65, 0.7, 0.42, 0.38, 0.14, 0.73, 0.29, 0.46, 0.37, 0.11, 0.62, 0.53, 0.73, 0.28, 0.33, 0.62, 0.49, 0.61, 0.33, 0.37, 0.09, 0.37, 0.56, 0.54, 0.29, 0.33, 0.29, 0.3, 0.3, 0.46, 0.59, 0.52, 0.34, 0.35, 0.32, 0.11, 0.76, 0.23, 0.56, 0.24, 0.38, 0.49, 0.37, 0.37, 0.41, 0.46, 0.73, 0.48, 0.32, 0.6, 0.53, 0.37, 0.59, 0.53, 0.42, 0.85, 0.28, 0.41, 0.42, 0.44, 0.59, 0.58, 0.45, 0.21, 0.63, 0.35, 0.55, 0.6, 0.47, 0.82, 0.24, 0.53, 0.47, 0.71, 0.84, 0.46, 0.42, 0.36, 0.62, 0.4, 0.42, 0.51, 0.32, 0.55, 0.23, 0.28, 0.52, 0.62, 0.36, 0.61, 0.7, 0.16, 0.36, 0.7, 0.39, 0.43, 0.42, 0.55, 0.38, 0.51, 0.59, 0.24, 0.32, 0.62, 0.25, 0.33, 0.42, 0.3, 0.67, 0.23, 0.68, 0.64, 0.5, 0.42, 0.33, 0.34, 0.23, 0.17, 0.33, 0.31, 0.45, 0.46, 0.39, 0.33, 0.37, 0.23, 0.88, 0.5, 0.6033333333333333, 0.72, 0.33, 0.34, 0.29, 0.16, 0.62, 0.55, 0.51, 0.39, 0.21, 0.39, 0.7, 0.57, 0.6, 0.4, 0.58, 0.4, 0.55, 0.48, 0.57, 0.48, 0.24, 0.43, 0.36, 0.31, 0.14, 0.39, 0.47, 0.43, 0.33, 0.57, 0.65, 0.49, 0.36, 0.64, 0.77, 0.5, 0.47, 0.72, 0.61, 0.83, 0.23, 0.64, 0.67, 0.53, 0.51, 0.57, 0.44, 0.26, 0.22, 0.33, 0.42, 0.21, 0.29, 0.38, 0.23, 0.62, 0.24, 0.5, 0.28, 0.49, 0.485, 0.41, 0.76, 0.54, 0.43, 0.35, 0.3, 0.29, 0.44, 0.6, 0.21, 0.55, 0.62, 0.32, 0.33, 0.77, 0.41, 0.36, 0.32, 0.7, 0.73, 0.49, 0.72, 0.65, 0.42, 0.7, 0.29, 0.77, 0.48, 0.37, 0.48, 0.42, 0.24, 0.58, 0.76, 0.26, 0.38, 0.36, 0.82, 0.52, 0.46, 0.29, 0.51, 0.38, 0.56, 0.65, 0.7533333333333333, 0.33, 0.54, 0.55, 0.47, 0.43, 0.44, 0.69, 0.55, 0.21, 0.49, 0.51, 0.85, 0.49, 0.61, 0.19, 0.24, 0.47, 0.36, 0.7, 0.25, 0.35, 0.88, 0.37, 0.48, 0.48, 0.44, 0.73, 0.39, 0.36, 0.55, 0.65, 0.42, 0.92, 0.33, 0.2, 0.58, 0.34, 0.35, 0.14, 0.22, 0.84, 0.27, 0.26, 0.72, 0.47, 0.56, 0.55, 0.51, 0.42, 0.49, 0.66, 0.34, 0.28, 0.6, 0.56, 0.44, 0.63, 0.88, 0.31, 0.38, 0.51, 0.44, 0.54, 0.36, 0.22, 0.37, 0.37, 0.8, 0.22, 0.6, 0.84, 0.62, 0.3, 0.53, 0.56, 0.3, 0.66, 0.76, 0.59, 0.5, 0.55, 0.36, 0.42, 0.53, 0.45, 0.6, 0.31, 0.3, 0.53, 0.13, 0.85, 0.5, 0.74, 0.75, 0.28, 0.13, 0.46, 0.38, 0.23, 0.44, 0.52, 0.55, 0.45, 0.13, 0.42, 0.42, 0.42, 0.79, 0.14, 0.25, 0.24, 0.41, 0.42, 0.17, 0.43, 0.42, 0.55, 0.5, 0.29, 0.1, 0.35, 0.75, 0.42, 0.66, 0.36, 0.21, 0.34, 0.63, 0.42, 0.4, 0.39, 0.7, 0.42, 0.78, 0.76, 0.33, 0.35, 0.29, 0.42, 0.36, 0.5, 0.73, 0.24, 0.71, 0.5, 0.22, 0.8, 0.64, 0.82, 0.41, 0.36, 0.73, 0.39, 0.62, 0.36, 0.67, 0.46, 0.53, 0.54, 0.33, 0.42, 0.48, 0.44, 0.46, 0.36, 0.24, 0.38, 0.35, 0.2, 0.31, 0.42, 0.34, 0.63, 0.65, 0.49, 0.4, 0.43, 0.68, 0.28, 0.59, 0.21, 0.39, 0.52, 0.3, 0.61, 0.58, 0.62, 0.47, 0.4, 0.59, 0.48, 0.63, 0.46, 0.12, 0.62, 0.58, 0.39, 0.31, 0.62, 0.42, 0.54, 0.36, 0.28, 0.45, 0.44, 0.28, 0.4, 0.22, 0.35, 0.39, 0.42, 0.5, 0.61, 0.34, 0.44, 0.24, 0.39, 0.57, 0.42, 0.65, 0.61, 0.27, 0.4, 0.54, 0.56, 0.54, 0.63, 0.3, 0.54, 0.48, 0.69, 0.12, 0.34, 0.2, 0.8, 0.37, 0.25, 0.31, 0.33, 0.73, 0.49, 0.42, 0.34, 0.43, 0.81, 0.61, 0.33, 0.33, 0.44, 0.3, 0.23, 0.3, 0.29, 0.46, 0.39, 0.35, 0.39, 0.37, 0.38, 0.33, 0.8, 0.73, 0.86, 0.53, 0.67, 0.27, 0.41, 0.36, 0.31, 0.44, 0.86, 0.17, 0.46, 0.81, 0.51, 0.54, 0.52, 0.32, 0.66, 0.62, 0.35, 0.42, 0.13, 0.53, 0.68, 0.39, 0.47, 0.48, 0.44, 0.42, 0.37, 0.45, 0.34, 0.42, 0.26, 0.75, 0.39, 0.27, 0.65, 0.69, 0.66, 0.27, 0.32, 0.46, 0.33, 0.43, 0.19, 0.54, 0.45, 0.65, 0.81, 0.81, 0.33, 0.7, 0.35, 0.33, 0.57, 0.38, 0.35, 0.34, 0.66, 0.36, 0.29, 0.29, 0.22, 0.41, 0.64, 0.7, 0.66, 0.39, 0.55, 0.45, 0.6, 0.32, 0.52, 0.38, 0.36, 0.26, 0.6, 0.36, 0.16, 0.67, 0.36, 0.81, 0.37, 0.43, 0.51, 0.64, 0.39, 0.57, 0.68, 0.56, 0.4, 0.43, 0.4, 0.35, 0.29, 0.36, 0.77, 0.3, 0.33, 0.43, 0.37, 0.35, 0.46, 0.41, 0.15, 0.47, 0.19, 0.55, 0.46, 0.61, 0.35, 0.39, 0.33, 0.35, 0.49, 0.25, 0.41, 0.36, 0.42, 0.52, 0.4, 0.22, 0.64, 0.41, 0.26, 0.62, 0.2, 0.64, 0.7, 0.51, 0.38, 0.4, 0.6, 0.53, 0.49, 0.51, 0.3, 0.5, 0.39, 0.7, 0.33, 0.63, 0.52, 0.37, 0.61, 0.67, 0.58, 0.31, 0.41, 0.21, 0.35, 0.34, 0.38, 0.64, 0.36, 0.39, 0.59, 0.5, 0.64, 0.59, 0.3, 0.52, 0.42, 0.33, 0.26, 0.38, 0.53, 0.31, 0.21, 0.69, 0.41, 0.47, 0.51, 0.37, 0.76, 0.4, 0.34, 0.52, 0.62, 0.47, 0.39, 0.3, 0.59, 0.43, 0.31, 0.37, 0.22, 0.33, 0.26, 0.42, 0.35, 0.28, 0.37, 0.47, 0.35, 0.57, 0.63, 0.2, 0.68, 0.3, 0.72, 0.57, 0.4, 0.37, 0.47, 0.37, 0.79, 0.47, 0.38, 0.29, 0.5, 0.51, 0.82, 0.69, 0.43, 0.47, 0.37, 0.36, 0.42, 0.33, 0.74, 0.33, 0.34, 0.31, 0.56, 0.62, 0.57, 0.64, 0.79, 0.39, 0.75, 0.36, 0.48, 0.31, 0.37, 0.28, 0.51, 0.63, 0.32, 0.3, 0.35, 0.58, 0.38, 0.52, 0.27, 0.66, 0.31, 0.31, 0.82, 0.26, 0.55, 0.69, 0.75, 0.63, 0.35, 0.65, 0.28, 0.72, 0.13, 0.32, 0.16, 0.56, 0.56, 0.52, 0.835, 0.18, 0.42, 0.45, 0.28, 0.44, 0.16, 0.52, 0.43, 0.74, 0.89, 0.71, 0.34, 0.83, 0.57, 0.82, 0.34, 0.43, 0.56, 0.23, 0.38, 0.27, 0.36, 0.49, 0.51, 0.35, 0.46, 0.34, 0.41, 0.61, 0.17, 0.49, 0.5, 0.46, 0.42, 0.82, 0.53, 0.57, 0.21, 0.43, 0.73, 0.23, 0.33, 0.41, 0.8, 0.78, 0.27, 0.58, 0.4, 0.55, 0.54, 0.47, 0.8, 0.43, 0.53, 0.23, 0.57, 0.6, 0.78, 0.44, 0.8, 0.21, 0.36, 0.74, 0.47, 0.61, 0.46, 0.5, 0.57, 0.47, 0.62, 0.22, 0.37, 0.32, 0.62, 0.59, 0.3, 0.39, 0.71, 0.32, 0.38, 0.47, 0.32, 0.54, 0.67, 0.52, 0.32, 0.22, 0.51, 0.54, 0.32, 0.29, 0.45, 0.54, 0.49, 0.45, 0.57, 0.72, 0.4, 0.83, 0.44, 0.59, 0.36, 0.68, 0.35, 0.33, 0.65, 0.42, 0.42, 0.26, 0.46, 0.35, 0.3, 0.28, 0.36, 0.32, 0.58, 0.31, 0.52, 0.53, 0.25, 0.89, 0.58, 0.3, 0.37, 0.47, 0.32, 0.52, 0.14, 0.45, 0.44, 0.5, 0.31, 0.37, 0.3, 0.51, 0.18, 0.46, 0.43, 0.32, 0.25, 0.78, 0.24, 0.77, 0.45, 0.49, 0.2, 0.21, 0.36, 0.37, 0.43, 0.37, 0.39, 0.24, 0.62, 0.35, 0.4, 0.23, 0.54, 0.28, 0.49, 0.57, 0.36, 0.33, 0.62, 0.5, 0.55, 0.45, 0.38, 0.37, 0.39, 0.64, 0.6, 0.76, 0.61, 0.3, 0.44, 0.43, 0.58, 0.27, 0.58, 0.82, 0.81, 0.79, 0.4, 0.55, 0.22, 0.28, 0.48, 0.23, 0.4, 0.36, 0.34, 0.28, 0.59, 0.41, 0.64, 0.61, 0.4, 0.58, 0.5, 0.31, 0.32, 0.56, 0.43, 0.36, 0.78, 0.32, 0.62, 0.61, 0.39, 0.22, 0.53, 0.59, 0.43, 0.36, 0.76, 0.35, 0.31, 0.4, 0.81, 0.2, 0.27, 0.67, 0.29, 0.35, 0.6, 0.52, 0.49, 0.35, 0.75, 0.36, 0.54, 0.73, 0.34, 0.54, 0.34, 0.55, 0.26, 0.26, 0.67, 0.36, 0.84, 0.34, 0.47, 0.6, 0.14, 0.66, 0.64, 0.41, 0.44, 0.35, 0.58, 0.43, 0.32, 0.29, 0.33, 0.46, 0.55, 0.54, 0.29, 0.69, 0.35, 0.56, 0.58, 0.54, 0.25, 0.32, 0.5, 0.59, 0.17, 0.43, 0.52, 0.24, 0.39, 0.41, 0.47, 0.54, 0.27, 0.23, 0.23, 0.58, 0.6, 0.7, 0.39, 0.45, 0.35, 0.15, 0.65, 0.62, 0.78, 0.69, 0.74, 0.22, 0.45, 0.51, 0.39, 0.5, 0.2, 0.3, 0.46, 0.52, 0.73, 0.26, 0.12, 0.35, 0.24, 0.8, 0.67, 0.48, 0.25, 0.46, 0.52, 0.7, 0.48, 0.19, 0.58, 0.32, 0.27, 0.25, 0.65, 0.34, 0.64, 0.74, 0.21, 0.32, 0.5, 0.38, 0.45, 0.27, 0.35, 0.5, 0.4, 0.31, 0.29, 0.3, 0.52, 0.55, 0.24, 0.4, 0.79, 0.43, 0.19, 0.59, 0.22, 0.5, 0.38, 0.38, 0.21, 0.33, 0.8933333333333333, 0.3, 0.68, 0.88, 0.64, 0.48, 0.65, 0.43, 0.71, 0.21, 0.36, 0.3, 0.77, 0.37, 0.32, 0.3, 0.42, 0.34, 0.35, 0.49, 0.43, 0.54, 0.32, 0.72, 0.63, 0.47, 0.71, 0.18, 0.755, 0.51, 0.62, 0.7, 0.57, 0.29, 0.32, 0.44, 0.21, 0.54, 0.62, 0.48, 0.25, 0.45, 0.82, 0.27, 0.32, 0.39, 0.29, 0.35, 0.35, 0.25, 0.38, 0.28, 0.4, 0.71, 0.41, 0.79, 0.35, 0.29, 0.37, 0.22, 0.35, 0.25, 0.2, 0.77, 0.39, 0.54, 0.53, 0.56, 0.67, 0.45, 0.38, 0.24, 0.29, 0.44, 0.54, 0.3, 0.16, 0.37, 0.26, 0.58, 0.3, 0.53, 0.7, 0.36, 0.39, 0.41, 0.59, 0.69, 0.22, 0.54, 0.68, 0.24, 0.21, 0.35, 0.66, 0.46, 0.41, 0.35, 0.48, 0.76, 0.31, 0.44, 0.41, 0.84, 0.31, 0.47, 0.36, 0.66, 0.83, 0.46, 0.57, 0.73, 0.48, 0.33, 0.47, 0.6, 0.24, 0.39, 0.38, 0.52, 0.68, 0.64, 0.73, 0.18, 0.64, 0.63, 0.36, 0.34, 0.32, 0.33, 0.31, 0.32, 0.36, 0.46, 0.35, 0.36, 0.36, 0.47, 0.19, 0.31, 0.57, 0.43, 0.45, 0.53, 0.24, 0.25, 0.23, 0.37, 0.38, 0.78, 0.22, 0.09, 0.7, 0.29, 0.29, 0.52, 0.44, 0.41, 0.24, 0.42, 0.57, 0.34, 0.29, 0.4, 0.26, 0.29, 0.59, 0.43, 0.27, 0.32, 0.28, 0.4, 0.53])
		exit()
		""" 
			1. CHANGE db, name to the one you want
		"""
		name = 'suspended'
		client = MongoClient()
		db = client.turkishCoup
		collection = getattr(db, name)

		"""
			2. CHANGE the start_time, end_time to whenever you want, 
			   or leave it empty.

		"""
		#end_time = datetime.datetime(2020, 10, 1)
		#start_time = datetime.datetime(2010, 1, 1)

		"""
			3. a list of tuples, indicating the day(s) to skip (optional)

			use createList() to read data from mongo, 
			use createListFromJson() to read data from a json file

		"""
		days_to_skip = [(2016, 8, 8),(2016, 8, 9),(2016, 8, 10)]
		data = formatTime(createList(collection), days_to_skip = days_to_skip)
		
		"""
			4. Give a resonable file new
		"""
		filename = "turkish_coup_suspended"
		plotTimeFreq(data, title = 'Distribution of Tweets' ,filename=filename)


#data = formatTime(createListFromJson('../../../rawdata/coup/5_coup_original_user.txt'), start_time, end_time)
