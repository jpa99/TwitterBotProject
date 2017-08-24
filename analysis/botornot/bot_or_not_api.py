"""	@
    @Description:   This python script queries data from BotOrNot
    @				API and compare results with ours, and make plots
    @
    @Author:        Joe Chen
"""
import botornot
import detect
import random
import timeline_new
import pickle
import simplejson as json
import time
twitter_app_auth = {
    'consumer_key': 'iuOy561xqEwz7hzsfn6emsKsh',
    'consumer_secret': '5jDf1retOpeWNOxF6dP9Dbvh3ITmzf2h4DK44w5UDo8s0N7QxX',
    'access_token': '1979279791-EV3BflLRIZ1lpSdsEbrSMBTaVPwJPQxVcMtSq2z',
    'access_token_secret': 'nS2NRNgqCDflbtvSVqlLMtEdanJxzs3U8VpHcweD3LHOQ',
}
bon = botornot.BotOrNot(**twitter_app_auth)
BOTORNOT_DIR = 'botornot_analysis/'

prefix_list = ["trump_joe/trump_tweet_",
			   "election/election_tweet_",
			   "obama/obama_tweet_",
			   "hillary/hillary_tweet_"]

# helper function to load users
def load_user(prefix):
	full_prefix = prefix + '/' + prefix + '_tweet_'
	detector = detect.SpamDetector(prefix = full_prefix)
	return detector.get_spam_user_info(variable = 'screen_name')

# a routine to query bot or not score given a list of users
def main(spam_user):
	scores = {}
	for user in spam_user:
		print 'current user is %s' %(str(user))
		start = time.time()
		try:
			result = bon.check_account('@' + str(user))
			print 'score is: ', result['score']
			scores[user] = result['score']
		except Exception as e:
			print e
		print 'time elapsed: ', time.time() - start
	return scores

# This function is called once (at the beginning) to calculate
# and store the score.
def store_score():
	dic = {}
	for prefix in ['viid', 'bit', 'tinyurl', 'lnis', 'goo', 'dld', 'ift', 'dlvr', 'ow']:
		print 'current prefix is: ', prefix
		dic[prefix] = main(prefix, load_user(prefix))
	json.dump(dic, open(BOTORNOT_DIR + 'bot_or_not_api_score.json', 'w'))

# This function is called after store_score() finished executing
# It prints stats of BotOrNot score, and plots the distribution 
# of all scores in histograms
def load_score():
	score = json.load(open(BOTORNOT_DIR + 'bot_or_not_api_score.json', 'r'))
	for prefix in ['viid', 'bit', 'tinyurl', 'lnis', 'goo', 'dld', 'ift', 'dlvr', 'ow']:
		print 'Dataset is: %s' %(prefix)
		print 'Average score: ', sum(score[prefix].values()) / len(score[prefix].values())
		#print 'Misclassification rate: ', 1.0 * len([v for v in score[prefix].values() if v <= 0.5]) / len(score[prefix].values())
		print 'Uncertain rate: ', 1.0 * len([v for v in score[prefix].values() if v >= 0.4 and v <= 0.6]) / len(score[prefix].values())
		#print 'Sample of Misclassified Users: ', [v for v in score[prefix].items() if v[1] <= 0.5]
		title = "Histogram of BotOrNot score keyword '" + prefix + "'"
		if prefix == 'trump_joe/trump_tweet_':
			title = "Histogram of tweeting behavior keyword 'Trump'"
		timeline_new.plot_histogram_botornot(score[prefix].values(), 
							filename = BOTORNOT_DIR + 'bot_or_not_api_score_' + prefix, 
							myrange = (0,1),
							title = title)

# This function is called after store_score() finished executing
# It prints stats of BotOrNot score, and plots the distribution 
# of all scores in histograms in one plot, with 9 mini plots
def load_score_miniplot():
	scores = []
	titles = []
	ranges = []
	score = json.load(open(BOTORNOT_DIR + 'bot_or_not_api_score.json', 'r'))
	for prefix in sorted(['viid', 'bit', 'tinyurl', 'lnis', 'goo', 'dld', 'ift', 'dlvr', 'ow']):
		print 'Dataset is: %s' %(prefix)
		print 'Average score: ', sum(score[prefix].values()) / len(score[prefix].values())
		#print 'Misclassification rate: ', 1.0 * len([v for v in score[prefix].values() if v <= 0.5]) / len(score[prefix].values())
		print 'Uncertain rate: ', 1.0 * len([v for v in score[prefix].values() if v >= 0.4 and v <= 0.6]) / len(score[prefix].values())
		scores.append(score[prefix].values())
		titles.append(prefix)
		ranges.append((0,1))
	
	exit(0)
	timeline_new.plot_histogram_botornot_miniplot(scores, 
							myrange = ranges,
							title = titles,
							filename = BOTORNOT_DIR + 'bot_or_not_api_score_all_URL_shorteners')

# special routine for quering scores of bots identified by debot 
# @tested
def store_score_debot():
	dic = {}
	prefix = 'bit'
	debot_result = json.load(open('debot_analysis/debot_' + prefix + '_all_user_score.json', 'r'))
	debot_bot = set([user for user, status in debot_result.iteritems() if status == 'isbot'])
	dic['debot_bit'] = main(debot_bot)
	json.dump(dic, open(BOTORNOT_DIR + 'bot_or_not_api_score_debot.json', 'w'))

# this one is unused, for hongkong dataset, use debot one
def store_score_hongkong():
	dic = {}
	debot_bot = []
	import csv
	with open('/Users/zc/Desktop/query_result.csv', 'rb') as f:
		reader = csv.reader(f)
		for row in reader:
			debot_bot += row
	
	debot_bot = debot_bot[1:]
	print len(debot_bot)
	dic['hongkong'] = main(debot_bot)
	json.dump(dic, open(BOTORNOT_DIR + 'bot_or_not_api_score_debot_hongkong.json', 'w'))


if __name__ == '__main__':
	#store_score()
	#load_score()
	store_score_hongkong()
	#load_score_miniplot()
	
