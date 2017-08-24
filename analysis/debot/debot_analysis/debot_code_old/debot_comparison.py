import detect
trump_spam_name = [u'CarlBullock16', u'Trump_Ameri16', u'TheTrump_Party', u'FastPolicy', u'Informationtopp', u'CuperAlfredt', u'PoliticcssTop', u'TEEITHIGH', u'News_Daily_24', u'BreitbartRSS1', u'CNoodleNews', u'LoveStephanysco', u'Trump_Commander', u'RightnewsNews', u'The_Reporter24', u'DailyNewUSA', u'TrumpWinner_16', u'DeplorableMarys', u'DNoticie', u'NewsTodayUSA', u'conservamother', u'The_Last_NewsPa', u'elhapp', u'RayWarnerShow', u'william36945299', u'manager_politic', u'Dpoliticmanager', u'WorldnewsPoli']
#trump_spam_name = [str(entry) for entry in trump_spam_name]
filename = '/Users/zc/Documents/twitter_research/github_code/twitter_research/paper/reference/debot_src/Code/Data/susp_user_name_trump_spam.txt'
debot_spam_name = []
with open(filename, 'rb') as f:
	for line in f:
		debot_spam_name.append(line.strip())

print len(trump_spam_name)
print len(debot_spam_name)
print len(set(trump_spam_name).intersection(set(debot_spam_name)))
print len(set(trump_spam_name).intersection(set(debot_spam_name))) / float(len(trump_spam_name))
# result
# 28
# 33
# 25
