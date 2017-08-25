from .. import crawler
from .. import detect
from .. import util
import numpy as np
import os
TwitterBotProjectPath = os.environ['TwitterBotProjectPath']

def two_features_nine_urls():
    y = []
    x = []
    for keyword in ['bit', 'tinyurl', 'goo', 'dld', 'ift', 'dlvr', 'ow', 'lnis', 'viid']:
        prefix = util.get_full_prefix(keyword)
        detector = detect.SpamDetector(prefix = TwitterBotProjectPath + '/' + prefix, url_based = True,
                            collect_url_only = False)
        
        group = detector.get_spam_group()
        user_info = detector.get_user_info()

        # let's get two features for now: top used language, and tweet variability
        from collections import Counter

        for index, g in enumerate(group.keys()):
            user_infos = [user_info[str(u)] for u in group[g]['spam_user']]
            std = np.std([u["statuses_count"] for u in user_infos])
            mean = np.mean([u["statuses_count"] for u in user_infos])
            top_language = Counter([u["lang"] for u in user_infos]).most_common(1)[0][0]
            x.append([std/mean, top_language])
            y.append(keyword + str(index+1))
            
        print x, y
    return x, y

def most_frequent_tweet_word():
    y = []
    x = []
    keyword = "dld"
    interest_group = 1
    PREFIX = TwitterBotProjectPath + "/feature/feature_rawdata/"
    FILE_NAME = keyword + str(interest_group) 
    # example: 
    prefix = util.get_full_prefix(keyword)
    detector = detect.SpamDetector(prefix = TwitterBotProjectPath + '/' + prefix, 
                                    url_based = True, 
                                    collect_url_only = False)
    group = detector.get_spam_group()
    user_info = detector.get_user_info()
    for index, g in enumerate(group.keys()):
        if index+1 == interest_group:
            user_infos = [user_info[str(u)] for u in group[g]['spam_user']]
            userlist = [u["id"] for u in user_infos]
            break

    myUserCrawler = crawler.UserCrawler(
        prefix = PREFIX, userlist = userlist[:2], filename = FILE_NAME, startover = True, 
        save_raw_data = True, only200 = True)
    myUserCrawler.searchUser()
    crawler.loaded_json(PREFIX + FILE_NAME + ".json")

# user_info_nine_urls()
most_frequent_tweet_word()
