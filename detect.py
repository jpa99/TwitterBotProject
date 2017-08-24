#!/usr/bin/python
# -*- coding: utf-8 -*-
import pprint
import os
import json
import util
import streamer
import dupefilter2 as dupefilter
import crawler
import urlparse
import timeline_new
import numpy as np
import sys


def url_detect(entry):
    # if the only url points to a link that looks like this
    
    # https://twitter.com/shadowandact/status/805840759308042240
    
    # https://twitter.com/i/web/status/805888039482339328
    # not suspicious (since it points to another Twitter user)
    
    # if there is no url at all, legitimate
    # if url is None, good
    # if url count is only one, good

    # if url is many, not sure, either news media url, or spam
    # 
    # if a user appear in multiple groups: very likely to be a bot!

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
    url = entry['url']
    if len(url.keys()) == 0:
        return False
    if len(url.keys()) == 1:
        if url.keys()[0] is None:
            return False
    
    total_url = 0
    verified_source = 0
    
    for each_url, count in url.iteritems():
        #if len(entry['user_ids']) > 400:
            #print len(entry['user_ids'])
            #print each_url, count
            #print urlparse.urlparse(each_url).netloc

        # In 2014, Twitter use \\/ in its json fields, we
        # need to remove them so urlparse can work properly
        
        each_url = each_url.replace('\\', '')
        
        if urlparse.urlparse(each_url).netloc in whitelist:
            verified_source += count
        total_url += count
    #print verified_source, total_url
    #print verified_source >= total_url * 0.80
    if verified_source >= total_url * 0.80:
        return False
    if total_url <= 10:
        return False
    else:
        # pprint.pprint(entry['user_ids'])
        # pprint.pprint(entry['text'])
        # pprint.pprint(url)
        # pprint.pprint(entry['status'])
        return True
        #return user_id_select(entry)

def all_groups(entry):
    return True

class SpamDetector(object):
    """SpamDetector is used to detect twitter bot, given a filename"""
    
    def __init__(self, prefix = None, sourcefile = None, url_based = False, collect_url_only = False):
        # prefix: a user defined prefix for the dataset
        # sourcefile: the absolute path to the sourcefile, which
        # can be a iterator of tweets (Python dictionary)
        print "start init..."
        self.prefix = prefix
        self.sourcefile = util.get_full_src_path(prefix)
        
        self.url_based = url_based
        self.collect_url_only = collect_url_only
        # if the directory self.prefix does not exist, create the directory 
        # find the second /, after processed_data/
        ind = self.prefix.index('/', 16)
        print self.prefix[:ind]
        if not os.path.exists(self.prefix[:ind]):
            print "making new directory"
            os.makedirs(self.prefix[:ind])
        else:
            print "directory already exists"
        print "finish init..."

    def get_suspicious_user_group(self, startover = False, filter_function = all_groups):
        duplicateFinder = dupefilter.DupInfo(prefix = self.prefix, startover = startover)   
        duplicateFinder.find_duplicate_tweet(collection = util.loadjson(self.sourcefile), collect_url_only = self.collect_url_only)
        botty_groups = duplicateFinder.get_suspicious_user_group(filter_function = filter_function, url_based = self.url_based)
        return botty_groups

    def analyze_user_group(self, startover = False):
        #self.get_top_embedd_url()
        if os.path.isfile(self.prefix + 'spam_group.json') and not startover:
            print 'File spam_group.json already exists ...'
            print 'Loading spam groups ...'
            spam_group = json.load(open(self.prefix + 'spam_group.json', 'r'))
            for group in spam_group.values():
                print '-------------------------------'
                print '         Top one website\n\n\n'
                pprint.pprint(group['top_one_website'])
                print '-------------------------------'
                print '         Spam URL\n'
                pprint.pprint(group['spam_url'])
                print '         \nscreen name\n'
                print "number users: %d" %(len(group['spam_user']))
                pprint.pprint(group['screen_name'][:10])
                print '         \nspam user id\n'
                pprint.pprint(group['spam_user'][:10])
        else:
            botty_groups = self.get_suspicious_user_group(filter_function = url_detect)
            print "===== get botty groups ======"
            print len(botty_groups)
            for g in botty_groups:
                myUserCrawler = crawler.UserCrawler(self.prefix, list(g['userlist']), g['filename'], startover = False)
                myUserCrawler.searchUser()
                """ uncomment get_user_stat() to get the printout of user info"""
                myUserCrawler.get_user_stat()

    def parameter_sweeping_plot(self, min_duplicate_factor = 3, percent_same = None, return_all = False):
        y = []
        if not percent_same:
            x = [xx * 0.1 for xx in range(1, 10)]
            for xx in x:
                result = self.parameter_sweeping(min_duplicate_factor = 3,percent_same = xx)
                y.append(result)
            #y = [2597, 1766, 1315, 999, 815, 696, 572, 421, 296]
            title = 'parameter_sweeping/' + self.prefix[:self.prefix.index('/')] + '_min_duplicate_factor_' + str(min_duplicate_factor)
            OX = [str(xx * 0.1) for xx in range(1, 10)]
            if return_all:
                return (range(1, 10), y, OX, np.arange(len(OX)) + 1)
            timeline_new.plot_xybar(x = range(1, 10), y = y, 
                                    OX = OX, ind = np.arange(len(OX)) + 1,
                                    xlabel = 'percent same', ylabel = 'number of spam user', title = title, filename = title)
        else:
            for xx in range(2, 11):
                result = self.parameter_sweeping(min_duplicate_factor = xx,percent_same = percent_same)
                y.append(result)
            #y = [2597, 1766, 1315, 999, 815, 696, 572, 421, 296]
            title = 'parameter_sweeping/' + self.prefix[:self.prefix.index('/')] + '_percent_same_' + str(percent_same)[0] + '_' + str(percent_same)[2]
            OX = [str(xx) for xx in range(2, 11)]
            if return_all:
                return (range(2, 11), y, OX, np.arange(len(OX)) + 2.5)
            timeline_new.plot_xybar(x = range(2, 11), y = y, 
                                    OX = OX, ind = np.arange(len(OX)) + 2.5,
                                    xlabel = 'min_duplicate_factor', 
                                    ylabel = 'number of spam user', 
                                    title = title, filename = title)

    def parameter_sweeping(self, min_duplicate_factor, percent_same, return_all = False):
        if self.url_based:
            botty_groups = self.get_suspicious_user_group()
        else:   
            botty_groups = self.get_suspicious_user_group(filter_function = url_detect)
        spam_group = {}
        print "number of spam group: ", len(botty_groups)
        for g in botty_groups:
            #pprint.pprint(g['filename'])
            myUserCrawler = crawler.UserCrawler(self.prefix, list(g['userlist']), g['filename'], startover = False)
            myUserCrawler.set_PERCENT_SAME(percent_same)
            myUserCrawler.set_MIN_DUPLICATE_FACTOR(min_duplicate_factor)
            myUserCrawler.searchUser()
            #result = myUserCrawler.get_user_stat(has_return = True, get_url = False)
            result = myUserCrawler.get_user_stat(has_return = True, get_url = False)
            
            if result:
                spam_group[g['filename']] = result
        
        if return_all:
            return spam_group

        spam_user = set([])
        for value in spam_group.values():
            spam_user = spam_user.union(set(value['spam_user']))
        print 'number of spam user is %d' %(len(spam_user))
        return len(spam_user)


    def save_spam_group(self):
        print "Check if user info has been saved..." 
        self.save_user_info()
        if os.path.isfile(self.prefix + 'spam_group.json'):
            print "File %s already exists." %(self.prefix + 'spam_group.json')
            return

        if self.url_based:
            botty_groups = self.get_suspicious_user_group()
        else:   
            botty_groups = self.get_suspicious_user_group(filter_function = url_detect)
        spam_group = {}
        print "number of spam group: ", len(botty_groups)
        for g in botty_groups:
            #pprint.pprint(g['filename'])
            myUserCrawler = crawler.UserCrawler(self.prefix, list(g['userlist']), g['filename'], startover = False)
            myUserCrawler.searchUser()
            result = myUserCrawler.get_user_stat(has_return = True)
            if result:
                spam_group[g['filename']] = result

        json.dump(spam_group, open(self.prefix + 'spam_group.json', 'w'))
        print 'spam_group SAVED...'

    def get_percent_of_spam(self):
        spam_user = self.get_spam_user_info(variable = 'spam_user')
        duplicateFinder = dupefilter.DupInfo(prefix = self.prefix)
        total_user = duplicateFinder.get_metadata(variable = 'num_user')
        
        print 'Start time is ', duplicateFinder.get_metadata(variable = 'start_time')
        print 'End time is ', duplicateFinder.get_metadata(variable = 'end_time')
        print 'Total number of account is %d' %(total_user)
        print 'Total number of spam account is %d' %(len(spam_user))
        print 'Percent of spam account is %f' %(float(len(spam_user))/float(total_user))
        
        total_tweet = duplicateFinder.get_metadata(variable = 'num_tweet')
        print 'Total number of tweets is %d' %(total_tweet)
        num_spam_tweet = duplicateFinder.get_tweet(collection = util.loadjson(self.sourcefile), userlist = spam_user, only_number = True)
        print 'Total number of spam tweets is %d' %(num_spam_tweet)
        print 'Percent of spam tweets is %f' %(float(num_spam_tweet)/float(total_tweet))

    # return the union of certain attribute of all spam groups
    def get_spam_user_info(self, variable = None):
        if not os.path.isfile(self.prefix + 'spam_group.json'):
            print 'File spam_group.json DOES NOT EXIST ...'
            print 'CALLING save_spam_group() ...'
            self.save_spam_group()
        spam_group = json.load(open(self.prefix + 'spam_group.json', 'r'))
        spam_user = set([])
        for value in spam_group.values():
            spam_user = spam_user.union(set(value[variable]))
        return spam_user

    # return spam_group as is
    def get_spam_group(self):
        if not os.path.isfile(self.prefix + 'spam_group.json'):
            print 'File spam_group.json DOES NOT EXIST ...'
            print 'CALL FAILED!!!'
        return json.load(open(self.prefix + 'spam_group.json', 'r'))

    def get_num_tweet(self):
        # return total number of tweets in one collection
        duplicateFinder = dupefilter.DupInfo(prefix = self.prefix)
        num_tweet = duplicateFinder.get_metadata(variable = 'num_tweet')
        return num_tweet

    # return dic of info of all users
    # def get_user_info(self):
    #   user_info = json.load(open(self.prefix + 'user_info.json', 'r'))
    #   return user_info

    def print_metadata(self):
        # return metadata of one collection
        # including total number of tweets, total
        duplicateFinder = dupefilter.DupInfo(prefix = self.prefix)
        data = duplicateFinder.get_metadata()
        print data['num_tweet']
        print data['end_time'] - data['start_time']
        print data['start_time']

    def get_top_embedd_url(self):
        # this is used to generate a white list
        url = util.get_top_embedd_url(self.prefix, util.loadjson(self.sourcefile))
        print url  # unsorted 
        #sorted_url = sorted(url.items(), key=operator.itemgetter(1), reverse = True)
        #pprint.pprint(sorted_url[:100])

    def get_tweet_from_user(self, userlist, field = 'id'):
        # return a list of tweets made by users in userlist
        duplicateFinder = dupefilter.DupInfo(prefix = self.prefix)
        return duplicateFinder.get_tweet(collection = util.loadjson(self.sourcefile), userlist = userlist, field = field)

    def get_tweet_per_user(self):
        duplicateFinder = dupefilter.DupInfo(prefix = self.prefix)
        return duplicateFinder.get_tweet_per_user(collection = util.loadjson(self.sourcefile))

    def get_url_per_user(self):
        duplicateFinder = dupefilter.DupInfo(prefix = self.prefix)
        return duplicateFinder.get_url_per_user(collection = util.loadjson(self.sourcefile))

    def save_user_info(self):
        duplicateFinder = dupefilter.DupInfo(prefix = self.prefix)
        duplicateFinder.save_user_info(collection = util.loadjson(self.sourcefile))

    def get_user_info(self):
        if not os.path.isfile(self.prefix + 'user_info.json'):
            print "file does not exist......"
            return 
        return json.load(open(self.prefix + 'user_info.json', 'r'))


    def get_trump_spam_group(self):
        if not os.path.isfile(self.prefix + 'spam_group.json'):
            print 'FILE spam_group.json does not exist!!!'
            exit(1)

        spam_group = json.load(open(self.prefix + 'spam_group.json', 'r'))
        for g in spam_group.values():
            #if 'www.breitbart.com' == g['top_one_website']:
            pprint.pprint(g)
            #print g['spam_user']
            #print g['screen_name']
        exit()
        

datasets = ["trump/trump_tweet_",
            "hillary/hillary_tweet_",
            "obama/obama_tweet_",
            "election/election_tweet_"]

datasets2 = [ "hongkong_10_9/hongkong_tweet_",
             "hongkong_10_10/hongkong_tweet_",
             #"turkey_6_6/turkey_tweet_",
             #"turkey_6_7/turkey_tweet_"
             ]

# get this data: spam_group: total_num_tweet
def get_spam_group_num_tweet():
    userdic = json.load(open('metadata/user_num_tweet_all_URL_shorteners.json','r'))    
    result = {}
    for prefix in sorted(['bit', 'tinyurl', 'lnis', 'viid', 'goo', 'dld', 'ift', 'dlvr', 'ow']):    
        temp = {}
        spam_group = json.load(open(prefix + '/' + prefix + '_tweet_spam_group.json', 'r'))
        for spam_group_id in range(len(spam_group)):
            total = 0
            for user in spam_group[spam_group.keys()[spam_group_id]]['spam_user']:
                total += userdic[prefix][str(user)]
            temp[spam_group_id+1] = total
        result[prefix] = temp
    json.dump(result, open('metadata/user_num_tweet_per_spam_group_all_URL_shorteners.json','w'))
    exit()

# store 9 datasets user: num_tweet data into one json
def store_num_tweet_per_user_json():
    #dic = json.load(open('spam_category.json', 'r'))
    dic = {}
    for key in sorted(['bit', 'tinyurl', 'lnis', 'viid', 'goo', 'dld', 'ift', 'dlvr', 'ow']):   
        PREFIX = util.get_full_prefix(key)
        detector = SpamDetector(prefix = PREFIX, url_based = True)
        dic[key] = detector.get_tweet_per_user()
    json.dump(dic, open('metadata/user_num_tweet_all_URL_shorteners.json','w'))
    exit()

def parameter_sweeping_plot_miniplot():
    all_range = []
    all_y = []
    all_OX = []
    all_np = []
    titles = []
    for key in sorted(['bit', 'tinyurl', 'lnis', 'viid', 'goo', 'dld', 'ift', 'dlvr', 'ow']):   
        PREFIX = util.get_full_prefix(key)
        detector = SpamDetector(prefix = PREFIX, url_based = True)
        #result = detector.parameter_sweeping_plot(min_duplicate_factor = 3, return_all = True)
        result = detector.parameter_sweeping_plot(percent_same = 0.6, return_all = True)
        titles.append(key)
        all_range.append(result[0])
        all_y.append(result[1])
        all_OX.append(result[2])
        all_np.append(result[3])
    
    timeline_new.plot_xybar_miniplot(all_range, all_y, 
                                    all_OX, all_np, titles,
                                    xlabel = 'percent same', ylabel = 'number of spam user', filename = 'parameter_sweeping/parameter_sweeping_plot_all_URL_shorteners_min_dup_factor')
    exit()

def helper_print_metadata():
    for key in ['viid', 'goo', 'bit', 'dld', 'ift', 'dlvr']:
        PREFIX = util.get_full_prefix(key)
        detector = SpamDetector(prefix = PREFIX, url_based = True)
        #detector.print_metadata()
        #pprint.pprint(detector.get_suspicious_user_group(startover = False, filter_function = url_detect))
        detector.save_user_info()
    exit()

def test_spam_group():
    spam_group = json.load(open('goo/goo_tweet_spam_group.json', 'r'))
    print len(spam_group)
    result = []
    
    for index, group in enumerate(spam_group.keys()):
        print type(spam_group[group]['top_one_website']) 
        if isinstance(spam_group[group]['top_one_website'], basestring):
            website = spam_group[group]['top_one_website']
        else:
            website = spam_group[group]['top_one_website'][0][0]
        result.append({'id': index, 
                       'total_user': len(spam_group[group]['spam_user']),
                       'top_one_website': website})
    print result
    exit()

def update_webapp(prefix):
    """Write new entry to config file of Monitor Web App"""
    with open('MonitorWebApp/config.txt', 'a') as f:
        f.write(prefix+'\n')


def user_info_nine_urls():
    y = []
    x = []
    for keyword, KEYWORD in [('bit', ['bit ly']), ('tinyurl', ['tinyurl']),
    ('goo', ['goo gl']), ('dld', ["dld bz"]), ('ift', ["ift tt"]), ('dlvr',
    ['dlvr it']), ('ow', ['ow ly']), ('lnis', ['ln is']), ('viid', ['viid'])]:
        # keyword = keyword + "_long"
        prefix = util.get_full_prefix(keyword)
        #streamer.collect(keyword=KEYWORD, filename=util.get_full_src_path(prefix), num_tweets=NUM_TWEETS, duration = 43200)
        detector = SpamDetector(prefix = prefix, url_based = True,
                            collect_url_only = False)
        # pprint.pprint(detector.get_user_info())
        group = detector.get_spam_group()
        user_info = detector.get_user_info()

        # pprint.pprint(group)

        # let's use two for now: top language, and tweet variability
        from collections import Counter

        for index, g in enumerate(group.keys()):
            user_infos = [user_info[str(u)] for u in group[g]['spam_user']]
            std = np.std([u["statuses_count"] for u in user_infos])
            mean = np.mean([u["statuses_count"] for u in user_infos])
            top_language = Counter([u["lang"] for u in user_infos]).most_common(1)[0][0]
            x.append([std/mean, top_language])
            #return group[g]['spam_user'], user_info
            y.append(keyword + str(index+1))
            
        print x, y

        
def run_long_experiment():
    for keyword, KEYWORD in [('bitly', ['bit ly']), ('tinyurl', ['tinyurl']),
    ('goo', ['goo gl']), ('dld', ["dld bz"]), ('ift', ["ift tt"]), ('dlvr',
    ['dlvr it']), ('ow', ['ow ly']), ('lnis', ['ln is']), ('viid', ['viid'])]:
        keyword = keyword + "_long"
        prefix = util.get_full_prefix(keyword)
        NUM_TWEETS = 500000
        #streamer.collect(keyword=KEYWORD, filename=util.get_full_src_path(prefix), num_tweets=NUM_TWEETS, duration = 43200)
        detector = SpamDetector(prefix = prefix, url_based = True,
                            collect_url_only = False)
        detector.get_percent_of_spam()


if __name__ == '__main__':
    """
        Be careful when calling crawler on existing duplifliers 
        because of update of filename from actual text to numerical
        number group_1, group_2, ..., ...

    """
    #helper_print_metadata()
    #parameter_sweeping_plot_miniplot()
    #get_spam_group_num_tweet()

    """
        input variables: keyword, DATA_DIR (defined at very top)
    """
    # default keyword
    keyword = 'git_test'

    prefix = util.get_full_prefix(keyword)
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
    #SOURCE_FILE = DATA_DIR + PREFIX[:PREFIX.index('/')] + '.txt'
    #SOURCE_FILE = util.slice_data(2014, 10, 10)
    """
            variables for streaming: (optional)
            KEYWORD: a list of keywords
            num_tweets: number of tweets to collect
    """
    KEYWORD = ['bit']
    NUM_TWEETS = 1000

    
    """
        start the streamer first (optional if the dataset already exists)
    """

    streamer.collect(keyword=KEYWORD, filename=util.get_full_src_path(prefix), num_tweets=NUM_TWEETS)

    
    """
        initialize spam detector
    """
    detector = SpamDetector(prefix = prefix, url_based = True, 
                            collect_url_only = False)

    """
        this step is first, and does not involve more API calls
        after this step, a .p file of suspicious_user_group is 
        generated
    """
    #pprint.pprint(detector.get_suspicious_user_group(startover = True, filter_function = url_detect))
    # for entry in detector.get_suspicious_user_group(startover = False, filter_function = url_detect):
    #   print entry['filename']
    #   print len(entry['userlist'])
    """
        this step requires revisiting users calling Twitter RestAPI, 
        and can take at most hours to finish
    """
    #detector.analyze_user_group()
    
    """
        returns a final result of percent of spams
    """
    detector.get_percent_of_spam()














