# -*- coding: utf-8 -*-
import requests
import detect
import crawler
import pickle
import os
import json

import util

# Feghouli14 is suspended 
#['WuerzRodrigo', 'reed_schepens'] are also suspended 
REVISIT_DIR = 'spam_account_status/'
datasets2 = ["trump/trump_tweet_",
            "hillary/hillary_tweet_",
            "obama/obama_tweet_",
            "election/election_tweet_",
            "hongkong_10_9/hongkong_tweet_",
            "hongkong_10_10/hongkong_tweet_",
             #"turkey_6_6/turkey_tweet_",
             #"turkey_6_7/turkey_tweet_"
             ]
COUNTER = 1

def check_status(user, screen_name = True):
    # find a protected user
    #user = ['erendiz87']
    global COUNTER

    deleted = set([])
    protected = set([])
    suspended = set([])
    normal = set([])
    
    for u in user:
        r = requests.get('https://twitter.com/'+str(u))
        print r.status_code
        if r.status_code == 404:
            deleted.add(u)
            print 'user is deleted'
        else:
            print 'user is alive'
    
    myUserCrawler = crawler.UserCrawler(simplecrawl = True) 
    
    for u in user:
        print 'Global COUNTER is: ', COUNTER
        COUNTER += 1
        if u not in deleted:
            print u
            try:
                crawler.APIUrl = 'https://api.twitter.com/1.1/users/lookup.json'
                code = myUserCrawler.get200(u, use_screen_name = screen_name, return_error_code = True)
                # use tokenindex in a cyclical way
                crawler.tokenindex += 1
                crawler.tokenindex = crawler.tokenindex % crawler.ROUND    
                if int(code) == 404:
                    print 'user is suspended'
                    suspended.add(u)
                else:
                    crawler.APIUrl = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
                    code = myUserCrawler.get200(u, use_screen_name = screen_name, return_error_code = True)
                    # use tokenindex in a cyclical way
                    crawler.tokenindex += 1
                    crawler.tokenindex = crawler.tokenindex % crawler.ROUND
                    if int(code) == 401:
                        print 'user is protected'
                        protected.add(u)
                    else:
                        print 'user is normal'
                        normal.add(u)
            except Exception, e:
                print 'Exception!!! status not sure'
                print e
                print 'user is perheps normal'
                normal.add(u)

    return {'deleted': list(deleted),
           'protected': list(protected),
           'suspended': list(suspended),
           'normal': list(normal)}

def get_and_store_status(filename):
    if os.path.isfile(filename):
        print 'file exists'
        return 
    dic = {}
    #['bit', 'tinyurl', 'lnis', 'viid', 'goo', 'dld', 'ift', 'dlvr', 'ow']
    for prefix in ['bit', 'tinyurl', 'lnis', 'viid', 'goo', 'dld', 'ift',
    'dlvr', 'ow']:
        print prefix
        full_prefix = util.get_full_prefix(prefix)
        detector = detect.SpamDetector(prefix = full_prefix)
        user = detector.get_spam_user_info(variable = 'screen_name')
        #user = ['WuerzRodrigo', 'reed_schepens']
        #user = ['InceZehraince3', 'noexistingasdf123', 'zhouhanchen', 'NBA76ersFans']
        #user = list(user)[:2]
        print len(user)
        dic[prefix] = check_status(user)
    json.dump(dic, open(filename, 'w'))
    #pickle.dump(dic, open(filename, 'wb'))

# date of collection: 2/5/2017, 4:50pm - 5:??pm EST
def load_status(filename):
    #status = pickle.load(open(filename, 'rb'))
    status = json.load(open(filename, 'r'))
    for k, v in status.iteritems():
        print k
        print 'deleted ', len(v['deleted'])
        print 'protected ', len(v['protected'])
        print 'suspended ', len(v['suspended'])
        print 'normal ', len(v['normal'])
        total = len(v['normal']) + len(v['suspended']) + \
                len(v['protected']) + len(v['deleted'])
        print 'percent Twitter suspended ', 1.0 * len(v['suspended']) / total

def get_changed_user(filename):
    status = pickle.load(open(filename, 'rb'))
    for k, v in status.iteritems():
        print 
        print k
        print 'deleted -->'
        print v['deleted']
        print 'suspended -->'
        print v['suspended']
        
def get_tweet_of_suspended_user(filename):
    status = pickle.load(open(filename, 'rb'))
    for k, v in status.iteritems():
        count = 0
        if 'trump' in k:
            suspended = v['suspended']
            detector = detect.SpamDetector(prefix = k)
            result = detector.get_tweet_from_user(suspended, field = 'screen_name')
            print len(result)
            for tweet in result:
                if 'StylishRentals' in tweet['text']:
                    count += 1
                    print tweet['text'].encode('utf-8', 'ignore')
                    #print tweet['user']['id']
                    #print tweet['user']['screen_name']
                    #print tweet['created_at']
            print count
            
    # count = 322
    # 322/357 = 90% tweets are about this one account

filename = REVISIT_DIR + 'spam_account_status_9_dataset_revisit_20170717.json'

if __name__ == '__main__':
    #get_tweet_of_suspended_user(filename)
    #get_changed_user(filename)
    #get_and_store_status(filename)
    load_status(filename)

