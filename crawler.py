# -*- coding: utf-8 -*-

import time
import ujson as json
import sys
import urllib2
import oauth2
import traceback
import pickle
import datetime
import pprint
import csv
import random
import collections
import re
import string
from os import path
import urlparse
import operator
import httplib
import nltk
from collections import Counter
import twitter_credential
import gevent
import gevent.monkey  # $ pip install gevent
gevent.monkey.patch_all()

tokenpool = twitter_credential.tokenpool()
ROUND = len(tokenpool)
TIME_INTERVAL = (15*60.0)/(1500 * ROUND)
last_update_time = time.time()
stopwords = nltk.corpus.stopwords.words('english')

APIUrl = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
SHORT_URL = ['bit.ly', 'ift.tt','dlvr.it', 'ow.ly', 'goo.gl', 'fb.me', 'www.facebook.com', 'dld.bz', 't.co', 'qtr.so', 'viid.me', 'hill.cm']
whitelist = set(['twitter.com', 'usat', 'www.nbcnews.com', 'ti.me', 
        'newyorker.com', 'time.com', 'www.wired.com', 
        'wapo.st', 'www.washingtonpost.com', 'bzfd.it', 'www.nytimes.com','nyti.ms',
        'huff.to', 'www.huffingtonpost.com', 'www.theguardian.com', 'www.newyorker.com', 'hill.cm', 'www.buzzfeed.com', 'www.usatoday.com',
        'www.forbes.com', 'bloom.bg', 'apple.news', 'www.yahoo.com',
        'mobile.nytimes.com', 'cnn.it', 'econ.st', 'fb.me', 'www.esquire.com',
        'thehill.com', 'www.nationalmemo.com', 'on.mash.to', 'mashable.com', 'crooksandliars.com',
        'peoplem.ag', 'www.politicususa.com', 'usat.ly', 'politi.co', 'www.theatlantic.com',
        'www.bbc.co.uk', 'nypost.com', 'bbc.co.uk', 'theatln.tc', 'www.youtube.com', 'www.reddit.com',
        'www.telegraph.co.uk', 'www.independent.co.uk', 'money.cnn.com', 'www.dailywire.com',
        'lat.ms', 'www.aclu.org', 'youtu.be', 'www.cnn.com', 'www.nydailynews.com',
        'www.billboard.com', 'www.cnbc.com', 'theconservativetreehouse.com', 'www.bloomberg.com',
        'tmblr.co', 'vine.co', 'nbcnews.to', 'cnb.cx', 'www.change.org',
        'www.factcheck.org', 'slate.me', 'www.facebook.com', 'm.youtube.com', 'snpy.tv',
        'jwatch.us', 'www.judicialwatch.org','variety.com', 'vogue.cm', 'sacredstonecamp.org',
        'www.swarmapp.com', 'apne.ws', 'edition.cnn.com', 'abcn.ws', 'atfp.co', 'bbc.in',
        'fxn.ws', 'on.wsj.com', 'reut.rs', 'n.pr', 'www.npr.org'])
# tokenindex keeps track of which pair of consumer, token should be used from the pool
tokenindex = 0

start_time = datetime.datetime(2016, 7, 15)
def check_time(tweet):
    if 'created_at' in tweet:
        dt = datetime.datetime.strptime(tweet[u'created_at'], '%a %b %d %H:%M:%S +0000 %Y')  # format the time
        print dt
        if start_time <= dt:
            return True
        else:
            return False
    else:
        return True

def unshorten_url(url, retry, results):
    #print url
    if len(results) > 0:
        if results[max(results.keys())] == url:
            return results
    #print "results is: "
    results[retry] = url
    if retry > 4:
        return results
    parsed = urlparse.urlparse(url)
    h = httplib.HTTPConnection(parsed.netloc, timeout=2)
    resource = parsed.path
    if parsed.query != "":
        resource += "?" + parsed.query
    try:
        h.request('HEAD', resource)
        response = h.getresponse()    
    except Exception, e:
        print e
        return results 

    if response.status/100 == 3 and response.getheader('Location'):
        return unshorten_url(response.getheader('Location'), retry+1, results)  # changed to process chains of short urls
    else:
        return results


class UserCrawler(object):
    """A crawler to collect Twitter user info from RestAPI"""

    def __init__(self, prefix = None, userlist = None, filename = None, 
                 startover = False, simplecrawl = False, only200 = True,
                 save_raw_data = False, raw_data = {}):
        self.only200 = only200
        if simplecrawl:
            print 'Simple Crawler init...'
            print '[Ready to use]'
            return
        self.prefix = prefix
        userlist = [int(u) for u in userlist]
        self.userlist = list(userlist)
        self.filename = filename
        self.data = {}
        self.save_raw_data = save_raw_data
        self.raw_data = raw_data
        # for u in self.userlist:
        #     self.data[u] = set([])
        self.hf = []
        self.avg = []
        self.screen_name = {}
        self.retweet = []
        self.source = collections.Counter()
        self.startover = startover
        self.url = {}

        self.MIN_DUPLICATE_FACTOR = 3
        self.PERCENT_SAME = 0.6
        self.MIN_NUM_BOT_PER_GROUP = 10

    def set_MIN_DUPLICATE_FACTOR(self, n):
        self.MIN_DUPLICATE_FACTOR = n
    
    def set_PERCENT_SAME(self, n):
        self.PERCENT_SAME = n
    
    def set_MIN_NUM_BOT_PER_GROUP(self, n):
        self.MIN_NUM_BOT_PER_GROUP = n

    def repeat200(self, first_id, user, mydata, use_screen_name):
        """
        repeat200 repeatedly searches for next 200 tweets of a certain user
        by updating params["max_id"] in timeline API
        
        @inputs: beginning tweet ID, or string "stop" if no ID is required
        @outputs: None
        """
        global tokenindex, last_update_time
        prev_id = first_id
        while True:
            url = APIUrl
            params = {"oauth_version":"1.0","oauth_nonce": oauth2.generate_nonce(),"oauth_timestamp":int(time.time())}
            if use_screen_name:
                params["screen_name"] = user    
            else:
                params["user_id"] = int(user)
            params["count"] = 200
            #params["exclude_replies"] = "true"
            params["max_id"] = str(prev_id)
            params["oauth_consumer_key"] = (tokenpool[tokenindex][0]).key
            params["oauth_token"] = (tokenpool[tokenindex][1]).key

            req = oauth2.Request(method="GET", url=url, parameters=params)
            signature_method = oauth2.SignatureMethod_HMAC_SHA1()  # HMAC, twitter use sha-1 160 bit encryption
            req.sign_request(signature_method, tokenpool[tokenindex][0], tokenpool[tokenindex][1])
            url = req.to_url()
            #print "repear200 url: ", url 
            response = urllib2.Request(url)
            try:
                data = json.load(urllib2.urlopen(response, timeout = 10))  # format results as json
                print "length of data of current repeat200 is --> ", len(data)
                mydata += data


                if time.time() - last_update_time < TIME_INTERVAL:
                    print "sleep"
                    time.sleep(TIME_INTERVAL)
                last_update_time = time.time()
                # use tokenindex in a cyclical way
                tokenindex += 1
                tokenindex = tokenindex % ROUND

                if len(data) < 100:
                    return mydata
                else:
                    prev_id = int(data[len(data)-1][u'id']) - 1
    
            except Exception as e:
                time.sleep(1)
                print "Get an URLError!"
                print e
                return mydata
            

    def get200(self, user, use_screen_name = False, return_error_code = False):
        """
        The function gets the first 200 tweets (or 3200 if self.only200 == False)
        from a user 
        
        @inputs: None
        @outputs: string "stop" if the user has less than 200 tweets, 
                  otherwise return the last tweet ID
        """
        global tokenindex

        url = APIUrl
        params = {"oauth_version":"1.0","oauth_nonce": oauth2.generate_nonce(),"oauth_timestamp":int(time.time())}
        if use_screen_name:
            params["screen_name"] = user    
        else:
            params["user_id"] = int(user)
        params["count"] = 200
        #params["exclude_replies"] = "true"
        params["include_entities"]="true"
        params["oauth_consumer_key"] = (tokenpool[tokenindex][0]).key
        params["oauth_token"] = (tokenpool[tokenindex][1]).key

        req = oauth2.Request(method="GET", url=url, parameters=params)
        signature_method = oauth2.SignatureMethod_HMAC_SHA1()  # HMAC, twitter use sha-1 160 bit encryption
        req.sign_request(signature_method, tokenpool[tokenindex][0], tokenpool[tokenindex][1])
        #headers = req.to_header()
        url = req.to_url() 
        #print "get200 url: ", url
        response = urllib2.Request(url)
        try:
            data = json.load(urllib2.urlopen(response, timeout = 10))  # format results as json
            print "length of data of get200 is --> ", len(data)
            if return_error_code:
                return 200
            else:
                if (len(data) < 100 or self.only200):
                    return data
                else:
                    return self.repeat200(data[len(data)-1][u'id'] - 1, user, data, use_screen_name = use_screen_name)

        except urllib2.URLError, e:
            time.sleep(1)
            #print (traceback.format_exc())
            #print(sys.exc_info()[0])
            print "Get an URLError!"
            print e
            if return_error_code:
                return e.code
            return []

    def update_user(self, user):
        data = self.get200(user)
        if self.save_raw_data:
            self.raw_data[user] = data
            return
        if data == []:
            return
        # get avg_tweet_interval, percent of high frequency tweets
        avg, hf = get_tweet_interval(data)
        url, source, retweet, unique_tweet = self.get_tweet_info(data)
        screen_name = get_screenname(data)
        self.data[user] = unique_tweet
        self.url[user] = url
        self.source += source
        self.screen_name[user] = screen_name
        self.hf.append(hf)
        self.avg.append(avg)
        self.retweet.append(retweet)

        print 'screen name is...'
        print screen_name
        print 'tweeting pattern is...'
        print {'avg': avg, 'hf': hf}
        print 'source info is...'
        print source
        print 'retweet info is...'
        print retweet


    def saveUserInfo(self):
        # maybe write it to a json file, so it's more extensible
        dic = {"user":self.userlist, "source":self.source,
               "data": self.data, "hf": self.hf ,"avg": self.avg,
               "screen_name": self.screen_name, "retweet": self.retweet,
               "url": self.url}
        #pickle.dump(dic, open(self.prefix + , 'w'))
        json.dump(dic, open(self.prefix + self.filename + '.json', 'w'))

    def loadUserInfo(self):
        dic = json.load(open(self.prefix + self.filename + '.json', 'r'))
        
        self.userlist = [int(u) for u in dic['user']]
        self.source = dic['source']

        for k,v in dic['data'].iteritems():
            self.data[int(k)] = v
        
        self.hf = dic['hf']
        self.avg = dic['avg']
        self.retweet = dic['retweet']

        for k,v in dic['screen_name'].iteritems():
            self.screen_name[int(k)] = v
        
        for k,v in dic['url'].iteritems():
            self.url[int(k)] = v

    def UserInfoExist(self):
        return path.isfile(self.prefix + self.filename + '.json')

    def searchUser(self):
        """
        The function gets all tweets from all users in userlist
        """
        global tokenindex, last_update_time
        count = 1

        print self.filename
        print self.prefix + self.filename + '.json'
        if self.filename and path.isfile(self.prefix + self.filename + '.json') and not self.startover:
            print "========== START searchUser =========="
            print "===== file already exists, no need to search...  ====="
            if not self.save_raw_data:
                print "===== load user info...."
                self.loadUserInfo()
                print "===== load finished!"
            return

        print "TOTAL NUM user is %d" %(len(self.userlist))
        for user in self.userlist:
            #print "current user id is ", user
            print "user " + str(user) + " is the " + str(count) + "th user----++++++" 
            count += 1
            try:
                self.update_user(user)
            except Exception, e:
                print "got an Exception"
                print (traceback.format_exc())            
                print(sys.exc_info()[0])
                print e
                print str(user), " is a protected user ###########"
                
            finally:
                print "finish searching user ", user
                
                if time.time() - last_update_time < TIME_INTERVAL:
                    print "sleep"
                    time.sleep(TIME_INTERVAL)
                last_update_time = time.time()
                # use tokenindex in a cyclical way
                tokenindex += 1
                tokenindex = tokenindex % ROUND                
                print "============================================="
        
        print "finish searching all users"
        print "===================================================="
        
        if self.save_raw_data:
            json.dump(self.raw_data, open(self.prefix + self.filename + '.json', "w"))

        elif self.filename:
            print "=== save to json ===="
            self.saveUserInfo()

    def hasBotUser(self):
        potential_bot, _ = self.get_potential_bot()
        if len(potential_bot) > 10:
            return True

    def getBotUser(self):
        potential_bot, _ = self.get_potential_bot()
        return potential_bot

    def get_retweet_user(self):
        index = 0
        retweet_user = []
        for user in self.userlist:
            if int(user) in self.screen_name:
                if self.retweet[index] < 1.0 and self.retweet[index] > 0.9:
                    retweet_user.append((user, self.screen_name[int(user)]))
                    #print user, self.screen_name[int(user)]
                    #pprint.pprint(collections.Counter(self.url[int(user)]).most_common(10))
                index += 1
        print "retweet user is:...."
        print len(retweet_user)
        pprint.pprint(retweet_user[:10])


    def get_user_stat(self, has_return = False, get_url = True):
        print "===== START to find bot..."
        common_user, bot_index = self.get_potential_bot()
        print "Number of potential bots: %d" %(len(common_user))
        if len(common_user) <= self.MIN_NUM_BOT_PER_GROUP:
            #print "Number bot is %d " %(len(common_user))
            print "[[NOT ENOUGH BOT FOUND]]"
            print "******** END ********"
            print
            return None
        
        print "[[FOUND BOT GROUPS]]"
        if get_url:
            print ">>>>>>>>>>>>>[Getting expanded top 1 url]"
            try:
                to_continue, common_url, top_url_expand, top_one_website = self.get_common_url(common_user)
                pprint.pprint(top_url_expand)
            except Exception as e:
                to_continue, common_url, top_url_expand, top_one_website = True,[],'',''          
        else:
            # "url information is BLANK"
            to_continue, common_url, top_url_expand, top_one_website = True, [],'',''
        
        if not to_continue:
            print "******** END ********"
            print
            return None
        
        if has_return:
            return {'spam_user': common_user,
            		'screen_name': [self.screen_name[name] for name in self.screen_name if name in common_user],
            		'spam_url': common_url, 'top_one_website': top_one_website}

        print ">>>>>>>>>>>>>[Top 10 urls]"
        print
        pprint.pprint(common_url)
        print ">>>>>>>>>>>>>[bot user account] (only 10 sample)"
        print
        if len(common_user) > 10:
            sample_user = random.sample(common_user, 10)
            sample_index = random.sample(bot_index, 10)
        else:
            sample_user = common_user
            sample_index = bot_index
        #pprint.pprint(sorted(sample_user))
        # only print things about the bot group

        #print ">>>>>>>>>>>>>[screen name] (10 sample)"
        pprint.pprint([(name, self.screen_name[name]) for name in self.screen_name if name in sample_user])
        
        #print ">>>>>>>>>>>>>[hf] (30 sample)"
        #print(sorted([self.hf[i] for i in sample_index]))
        #print(sorted(self.hf))
        #print ">>>>>>>>>>>>>[avg] (30 sample)"
        #print(sorted([self.avg[i] for i in sample_index]))
        # print(sorted(self.avg))
        #print ">>>>>>>>>>>>>[retweet] (30 sample)"
        #print(sorted([self.retweet[i] for i in sample_index]))

        print ">>>>>>>>>>>>>[duplicate tweets] (only 5 sample)"
        print
        common_tweet = self.get_common_tweet(common_user)
        if len(common_tweet) > 5:
            pprint.pprint(random.sample(common_tweet, 5))
        else:
            pprint.pprint(common_tweet)
        
        # generate graph
        # self.plot_distribution(self.hf, (0,1))

        # print ">>>>>>>>>>>>>content of No.1 URL"
        # #html_to_text(common_url[0][0])
        print "******** END ********"
        return 


    def get_potential_bot(self):
        # let's be more clever heres
        #
        # check common url first: if No.1 it's twitter.com, rank all twitter.com/user
        # links, and find user who are tweeting those links
        #
        # if No.1 is not twitter.com, it's a more interesting/sophisticated bot group
        # then we do duplicate tweet search

        potential_bot = []
        bot_index = []
        duplicate_tweet = collections.Counter()

        for entry in self.data.values():
            for tweet in entry:
                duplicate_tweet[tweet] += 1

        duplicate_tweet = set([t for t in duplicate_tweet if duplicate_tweet[t] >= self.MIN_DUPLICATE_FACTOR])
        #print len(duplicate_tweet)
        index = 0
        for user in self.userlist:
            if int(user) in self.data:
                v = self.data[int(user)]
                #print user
                num_intersect = len(set(v).intersection(duplicate_tweet))
                if num_intersect > len(v) * self.PERCENT_SAME:
                    #if self.has_suspicious_url(int(user)):
                        potential_bot.append(int(user))
                        bot_index.append(index)
                index += 1
        return potential_bot, bot_index

    def has_suspicious_url(self, user):
        # let's remove news accounts here
        #total_num_url = len(self.url[user])
        news_url = 0
        for url in self.url[user]:
            if urlparse.urlparse(url).netloc in whitelist:
                news_url += 1
        if news_url > 10:
            return False
        return True

    def get_common_url(self, common_user):
        c = collections.Counter()
        # too many urls, let's do a sample here
        all_url = [url for user in self.url if user in common_user for url in self.url[user]]
        # all_url = [sub_v for v in self.url.values() for sub_v in v]
        #for url in random.sample(all_url, 10):
        #r = requests.get(url)
        for url in all_url:
            c[urlparse.urlparse(url).netloc] += 1
        sorted_c = sorted(c.items(), key=operator.itemgetter(1), reverse = True)
        
        # let's expand the top 1 url and see what's actually there
        
        top_one_expanded = []
        if sorted_c[0][0] == 'twitter.com':
            c2 = collections.Counter()
            for url in all_url:
                if urlparse.urlparse(url).netloc == 'twitter.com':
                    index = url.find('/status/')
                    c2[url[:index].lower()] += 1
                    #c2[url] += 1
            sorted_c = sorted(c2.items(), key=operator.itemgetter(1), reverse = True)
            top_one_expanded = sorted_c[:10]

            prompt = """
                        !! NOTE !!
                        It seems that this group are just heavy retweeters
                        Here are users being retweeted the most

                    """

            print prompt
            printmore = False

        else:
            random.shuffle(all_url)
            for url in all_url:
                if len(top_one_expanded) < 10:
                    if urlparse.urlparse(url).netloc == sorted_c[0][0]:
                            #with gevent.Timeout(5):  # enforce total timeout
                                try:
                                    new_url_list = unshorten_url(url, 1, {})
                                    top_one_expanded.append(new_url_list)
                                except Exception, e:
                                    print e
                                    print "Cannot expand url"
            # extract expanded url
            url_list = []
            for dic in top_one_expanded:
                if dic != {}:
                    full_link = dic[max(dic.keys())]
                    url_list.append(urlparse.urlparse(full_link).netloc)
            if url_list != []:
                website = collections.Counter(url_list).most_common(1)[0][0]
            else:
                website = sorted_c[0][0]
            prompt = """
                          !!! WARNING !!!
                          This group redirects url to %s, which might be 
                          a news agency or phishing website.

                          Here is how urls get redirected

                        """ % (website)
            print prompt
            printmore = True
 
        sorted_c = sorted_c[:10]
        return printmore, sorted_c, top_one_expanded, website


    def get_common_tweet(self, common_user):
        duplicate_tweet = collections.Counter([t for user in self.data if int(user) in common_user for t in self.data[user]])
        duplicate_list = [t for t in duplicate_tweet if duplicate_tweet[t] > 3]
        sensitive_words = set(['sex', 'porn', 'nude', 'naked', 'photo', 'photos', 'women'])
        allWords = nltk.tokenize.word_tokenize(" ".join(duplicate_list))
        allWordExceptStopDist = nltk.FreqDist(w.lower() for w in allWords if w.lower() not in stopwords)
        if len(sensitive_words.intersection(set([entry[0] for entry in allWordExceptStopDist.most_common(50)]))) >= 5:
            return ["[[Porn Content Detected]]"]
        else:
            return duplicate_tweet.most_common(5)


    def get_tweet_info(self, data):
        c = collections.Counter()
        retweet = 0.0
        unique_tweet = set([])
        unique_url = []
        for t in data:
            #pprint.pprint(t)
            #url = 'https://t.co/FeoFGukBYE'
            #r = requests.get('http://www.linkexpander.com/?url='+url)
            if len(t['entities']['urls']) > 0:
            	# print 
            	# print t['text'].encode('utf-8', 'ignore')
             	embedded_url = t['entities']['urls'][0]['expanded_url']
             	if urlparse.urlparse(embedded_url).netloc != 'twitter.com':
                	unique_url.append(embedded_url)

            text = t['text']
            # remove @username structure
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
            text = text.strip()
            unique_tweet.add(text)
            #pprint.pprint(t)
            
            # check url
            c[t['source']] += 1
            # check retweet
            if 'retweeted_status' in t:
                retweet += 1
        
        return unique_url, c, retweet / len(data), list(unique_tweet)


    def plot_distribution(self, x, myrange):
        num_bins = 50
        n, bins, patches = plt.hist(x, num_bins, normed=True, facecolor='green', range = myrange, alpha=0.5)
        # add a 'best fit' line
        #y = mlab.normpdf(bins, mu, sigma)
        #plt.plot(bins, y, 'r--')
        plt.xlabel('avg tweeting interval (in seconds)')
        plt.ylabel('Probability')
        plt.title('Histogram of tweeting behavior')
        #plt.subplots_adjust(left=0.15)
        plt.savefig(self.prefix + self.filename)
        #plt.show()

def get_screenname(data):
    if 'user' in data[0]:
        return data[0]['user']['screen_name']

def get_tweet_interval(data):
    if len(data) == 1:
        return None
    total_seconds = 0
    high_frequency = 0
    for i in range(0, len(data)-1):
        dt = datetime.datetime.strptime(data[i][u'created_at'], '%a %b %d %H:%M:%S +0000 %Y')  # format the time
        dt2 = datetime.datetime.strptime(data[i+1][u'created_at'], '%a %b %d %H:%M:%S +0000 %Y')  
        diff = dt - dt2
        
        if diff.total_seconds() < 3600*2:
            high_frequency += 1
        total_seconds += diff.total_seconds()
        #print total_seconds
    
    return total_seconds / (len(data) - 1), high_frequency / (len(data) - 1.0)


def loaded_json(filename):
    user_tweets = json.load(open(filename, "r"))
    print "total number of users is ", len(user_tweets)
    for user, tweets in user_tweets.iteritems():
        print
        print user
        for t in tweets:
            print t["created_at"]
    print "================================================="


def readcsv(filename):
    # read csv file line by line
    users = []
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            users.append(int(row[0]))
    return users


def readfile(filename):
	user = []
	with open(filename, "r") as f:
		for line in f:
			user.append(int(line))
	return user

def compare(l1, l2):
	print len(l1)	
	print len(l2)

	new = set(l1).difference(set(l2))
	#inters =  new.intersection(set(l2))
	#print len(inters)
	#new.remove(inters)
	print len(new)	
	return list(new)

if __name__ == '__main__':
    """ =================================================================================
        |        IMPORTANT !!!         Choose a resonable FILE_NAME                     |
        =================================================================================
    """
    #########################
    FILE_NAME = "test_user_top_200"
    #########################
    """
        To use myUserCrawler on a group of ids all at once:
        call searchUser()
    
    e.g.:
    myUserCrawler = UserCrawler('test_timeline', userlist, 'test_filename', startover = True)
    myUserCrawler.searchUser()
    myUserCrawler.get_user_stat()
    
    
        To use myUserCrawler on individual id/screen_name:
        init UserCrawler with simplecrawl = True
    """

    myUserCrawler = UserCrawler(
        prefix = "./", userlist = [12, 1979279791, 246601433], filename = FILE_NAME, startover = True, 
        save_raw_data = True, only200 = True)
    myUserCrawler.searchUser()
    loaded_json(FILE_NAME+".json")




    ##############################
    # myUserCrawler = UserCrawler(simplecrawl = True, only200 = False)
    # result = myUserCrawler.get200('zhouhanchen', use_screen_name = True, return_error_code = False)
    # import streamer
    
    # for t in result:
    #     for url in streamer.get_embedded_url(t):
    #         if 'savingzev' in url:
    #             print url
        


