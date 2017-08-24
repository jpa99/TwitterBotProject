"""
    @
    @Description:   This python script queries data from Debot
    @               and compare results with our spam monitor
    @
    @Author:        Joe Chen
"""
import detect
#import debot
import time
import urllib2, urllib
import json
import crawler
import pprint
import streamer
import util

#API_KEY = 'bkl10683fKe4SiQ861ttLdP44JQQ9DaaOm1EiZxn'
#db = debot.DeBot(API_KEY)
path='http://www.cs.unm.edu/~chavoshi/debot/check_user.php'
DEBOT_DIR = 'debot_analysis/'

def load_user_screenname(prefix):
    detector = detect.SpamDetector(prefix = prefix)
    return detector.get_spam_user_info('screen_name')

def load_user_screenname_custom(prefix,percent_same=0.2):
    detector = detect.SpamDetector(prefix = prefix, url_based = True, sourcefile = None, 
                            collect_url_only = False)
    spam_group = detector.parameter_sweeping(min_duplicate_factor=3, 
                                      percent_same=percent_same, 
                                      return_all = True)
    spam_user = set([])
    for value in spam_group.values():
        spam_user = spam_user.union(set(value['screen_name']))
    print len(spam_user)
    return spam_user

def load_user(prefix):
    detector = detect.SpamDetector(prefix = prefix)
    return detector.get_spam_group()

def load_user_all(prefix):
    detector = detect.SpamDetector(prefix = prefix)
    count = 0
    for name, group in detector.get_user_info().iteritems():
        count += 1
        if group['screen_name'] == 'LuskRoyster':
            print count
            exit()
    return detector.get_user_info()

# query debot api and write results to json
def check_debot_api(prefix):
    full_prefix = util.get_full_prefix(prefix)
    spam_group = load_user_all(full_prefix)
    debot_result = {}
    count = 0
    unique_user = set([])
    for name, group in spam_group.iteritems():
        print name
        print 
        user = group['screen_name']
        print user
        count += 1
        if user in unique_user:
            continue
        else:
            unique_user.add(user)
        mydata=[('screen_name','@'+user)] 
        mydata=urllib.urlencode(mydata)
        req=urllib2.Request(path, mydata)
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        page=urllib2.urlopen(req).read()
        if 'This account has not been detected by DeBot' in page:
            print 'nobot'
            debot_result[user] = 'nobot'
        else:
            print 'isbot'
            debot_result[user] = 'isbot'

    json.dump(debot_result, open(DEBOT_DIR + 'debot_' + prefix + '_all_user_score.json', 'w'))

def check_debot_api_hongkong():
    #full_prefix = util.get_full_prefix(prefix)
    #spam_group = load_user_all(full_prefix)
    #unique_user = set([])
    debot_result = {}
    count = 0
    import csv
    all_user = []
    with open('hongkong/query_result.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            all_user += row

    all_user = all_user[1:]
    for user in all_user:
        if count < 174825:
            count += 1
            continue
        print user
        count += 1
        # if user in unique_user:
        #   continue
        # else:
        #   unique_user.add(user)
        mydata=[('screen_name','@'+user)] 
        mydata=urllib.urlencode(mydata)
        req=urllib2.Request(path, mydata)
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        page=urllib2.urlopen(req).read()
        if 'This account has not been detected by DeBot' in page:
            print 'nobot'
            debot_result[user] = 'nobot'
        else:
            print 'isbot'
            debot_result[user] = 'isbot'
        print count

    json.dump(debot_result, open(DEBOT_DIR + 'debot_' + 'hongkong' + '_all_user_score.json', 'w'))

# compare percent bots debot find relative to all users
def compare_score(prefix):
    debot_result = json.load(open(DEBOT_DIR + 'debot_' + prefix + '_all_user_score.json', 'r')) 
    all_user = len(debot_result.keys())
    bot_user = len([v for k,v in debot_result.iteritems() if v == 'isbot'])
    print prefix
    print all_user
    print bot_user
    print bot_user * 1.0 / all_user

# find percent of bots that debot find, and we also find
# or we did not find
def compare_score_all_user(prefix, return_debot_only = False, return_mybot_only = False):
    debot_result = json.load(open(DEBOT_DIR + 'debot_' + prefix + '_all_user_score.json', 'r'))
    debot_bot = set([user for user, status in debot_result.iteritems() if status == 'isbot'])
    full_prefix = util.get_full_prefix(prefix)
    my_bot = load_user_screenname(full_prefix)
    print 'num bots for debot %d' %(len(debot_bot))
    print 'num bots for our method %d' %(len(my_bot))
    print 'intersection is %d' %(len(debot_bot.intersection(my_bot)))
    print 'percent our bot in the intersection is %f' %(1.0 * len(debot_bot.intersection(my_bot)) / len(my_bot))
    print
    print 'num bots in debot,not in ours %d' %(len(debot_bot.difference(my_bot)))
    print 'num bots in ours,not in debot %d' %(len(my_bot.difference(debot_bot)))

    print 'Closer analysis of bots identified by debot...'
    debot_only = debot_bot.difference(my_bot)
    if return_debot_only:
        return debot_only
    if return_mybot_only:
        return my_bot.difference(debot_bot)

    user_info = json.load(open(full_prefix + 'user_info.json', 'r'))
    user_info_dic = {}
    for u,v in user_info.iteritems():
        user_info_dic[v['screen_name']] = v

    count = 0
    for u in debot_only:
        #pprint.pprint(user_info_dic[u]['screen_name'])
        if user_info_dic[u]['verified']:
            count += 1
            #print user_info_dic[u]['screen_name']
    print 'debot num verified ', count
    #print len(my_bot.intersection(user_info_dic.keys()))
    print 

    count = 0
    for u in my_bot:
        if u in user_info_dic:
            if user_info_dic[u]['verified']:
                count += 1
                #print user_info_dic[u]
    print 'mybot num verified ', count
    print

# we queried most 200 tweets for each debot user, and check
# how many of them have tweeted news URLs
def sample_user():
    # sample of debot only [u'melanieviveros9', u'RatanSharda55', u'KevinMcshea', u'imchrismva', u'Phaedrus08']
    import random
    import urlparse
    #debot_only = compare_score_all_user('bit', return_mybot_only = True)
    #samples = random.sample(list(debot_only), 5)
    #print samples
    prefix = 'bit'
    full_prefix = util.get_full_prefix(prefix)
    myUserCrawler = crawler.UserCrawler(simplecrawl = True)
    debot_result = json.load(open(DEBOT_DIR + 'debot_' + prefix + '_all_user_score.json', 'r'))
    debot_bot = set([user for user, status in debot_result.iteritems() if status == 'isbot'])
    my_bot = load_user_screenname_custom(full_prefix)

    data = {'debot': list(debot_bot), 'mybot': list(my_bot)}
    final_result = {'debot': {}, 'mybot': {}}
    for name, userlist in data.iteritems():
        print name
        for u in userlist:
            final_result[name][u] = []
            try:
                result = myUserCrawler.get200(u, use_screen_name = True, return_error_code = False)
                crawler.tokenindex += 1
                crawler.tokenindex = crawler.tokenindex % crawler.ROUND
                time.sleep(0.2)
                for t in result:
                    final_result[name][u] += streamer.get_embedded_url(t)
            except Exception, e:
                print e
                myUserCrawler = crawler.UserCrawler(simplecrawl = True)
                time.sleep(20)

    json.dump(final_result, open(DEBOT_DIR + 'debot_mybot_total_news_url.json', 'w'))

def load_sample_user(group = 'mybot'):
    import urlparse
    dic = json.load(open(DEBOT_DIR + 'debot_mybot_total_news_url.json', 'r'))
    prefix = 'bit'
    full_prefix = util.get_full_prefix(prefix)
    my_bot = load_user_screenname(full_prefix)
    print '%s news result' %(group)
    # those four URLs are not part of news bots, but generic URLs
    exclude = ['twitter.com', 'fb.me', 'www.youtube.com', 'youtu.be']
    count = 0
    total = 0
    precents = []
    for u, v in dic[group].iteritems():
        if u not in my_bot and group == 'mybot':
            continue
        total += 1
        have_news = False
        num_news = 0
        for url in v:
            if urlparse.urlparse(url).netloc in crawler.whitelist and urlparse.urlparse(url).netloc not in exclude:
                num_news += 1
                have_news = True    
        if have_news:
            count += 1
            precents.append(num_news * 1.0 / len(v))
    print 'total num accounts %d' %(total)
    print 'num news accounts %d' %(count)
    print 'avg percent of news tweets %f' %(sum(precents) / len(precents))

# a helper routine to compare results of debot with
# results of our spam monitor
# @tested
def score_comparison():
    for key in ['bit', 'tinyurl', 'lnis', 'viid', 'goo', 'dld', 'ift', 'dlvr', 'ow']:
        #compare_score(key)
        compare_score_all_user(key)
        #check_debot_api(key)

if __name__ == '__main__':
    check_debot_api_hongkong()
    #load_sample_user(group = 'mybot')
    #score_comparison()
    #sample_user()
    
