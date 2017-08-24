"""
    @
    @Description:   This python script retrieves all followers (up tp 75000) from a
    @               list of users
    @               and stores those tweets into a txt file.
    @Author:        Joe Chen
    @Last modified: 10/01/2015
"""

import time
import json
import urllib2
import oauth2
import pickle
import os
#1) stream_2017_rice_research_3
consumer1 = oauth2.Consumer(key="DTuoGABTnFlDoYAXyF3EMOkHt", secret="nzfvURfghCOPwvl4J5IVOR3GNoyhJXEJNxDhy7seLclnTnlkKV")
token1 = oauth2.Token(key="1979279791-lryQcPzr1iru4UxF3USWKpexLYW38qcxhTFdnfZ", secret="xZjeY4hUsaAYpE2MkdPFqmJhFvUzFxCjMaMKg9rgX86z7")

#2)from Joe Chen
consumer2 = oauth2.Consumer(key="CuyDAqUbCTF6y6k6mcoGF8owZ", secret="OucJJMnHbYCVNKNgyEJSNBMWBXapwSGuwy1Xc28mXR5vLixrNQ")
token2 = oauth2.Token(key="1979279791-8qRguXNd21mgHR8khU9hg8rcyXkHHSE65tkwFlv", secret="HIR4DQEyHVPrvXm2XNsTToVcgIgxWM2WR2eOoaY1iJV6R")

#3)from Joe Chen, another one
consumer3 = oauth2.Consumer(key="z4k1E4pOj8ncQ4MAdjY1r1Ty9", secret="92mLHrYChG5sHRdZsUc90JG7RRh8cewrl5Hjf2IoPunCAL8HRz")
token3 = oauth2.Token(key="1979279791-tSDamC8WUIxU9Z8uFnkWe5eLNSUlGYhGu8l5zZ1", secret="FNMSlsqgcIRmjeCf0BqD9TamwAD1ZfMC77n0x0cOpsICZ")

#4) name: summer research project
#resource https://dev.twitter.com/rest/reference/get/statuses/user_timeline 
consumer4 = oauth2.Consumer(key="Vsj9hKjxGPk4JxBj4al3i7JHX", secret="TbPwe5ltq7U4GtaeMtUhyMxxYb6jNvgyXWZsGsjKqcxbZCFhbD")
token4 = oauth2.Token(key="1979279791-c9yR5GJlLrg78jTIifIckvllZf8NBRl8K5aU8OZ", secret="FHuPvdPcbU3Xu77I44pqc64FmLGh82Bkftgq0xwqmRHhR")

#5) stream_2017_rice_research
consumer5 = oauth2.Consumer(key="Kx4Qm05mBRI6Gznx7utPoI4hg", secret="RMRe3oN5Ks2LaoGULaQCMQjRw8l0iQ7FkYPPCdJRylJwyzpSyq")
token5 = oauth2.Token(key="1979279791-xiCAC2SGmQamAuFuG4CsSaVrFzF2848LgK1FHF7", secret="CwIGJKPk3v95aZCapbKQhyFgSl3XbfHIC2dgO7X6S0WnA")

#6) stream_2017_rice_research_2
consumer6 = oauth2.Consumer(key="mtn5SFSU5nSefxi0NTU0cuHDv", secret="IAIi3RraqvDlKoSadZ08N13SAaL7SXNz7As97f85VgOVIJg3mZ")
token6 = oauth2.Token(key="1979279791-xVMRTM2e8cPUFwmUeg8pYX5bPvznW9WPqyjIMbS", secret="kuIIo3pwpHNh9tFzJwE63CF9lL0lKRdlTVeUVxTIKjdzv")

#7) version2_2
consumer7 = oauth2.Consumer(key="BkzUSqw8Odz3PfK7GOhzLqxY0", secret="LRqiunkDEgBgRsYy8NV0l4BpyoOZT37y9lHuc51WxwtB4QfKMu")
token7 = oauth2.Token(key="1979279791-bz66kMYt28h9Kbrlhr1GIFiFkyUKEr1lqoXYix2", secret="tM2bV8m73oMJig7GmUwEPRyUpC09xw5ZQDELI3YlQ4RIO")

#8) version2_3
consumer8 = oauth2.Consumer(key="bJ2YoqBL7TQwbq0M0IxNoOuwO", secret="iRL9F1nrGX8CE4ivjMW7AVsDugDFj6PszLi3NyDVE64MKAbFNC")
token8 = oauth2.Token(key="1979279791-vdibNWYKuk2BTAn76rapNYtM1GdwpmqBxdQ6ml6", secret="A8qukDTSkZvc7yYCHf2isVzpkbvdBpxo9mHYX8qqqJmYX")

#9) name: streaming api bot detection
consumer9 = oauth2.Consumer(key="Nc5XxItLtpHBzJ7zTVIw0DMRf", secret="Bmr5NjiYWUiTs3eVtyG7yNL2S8XptnGUtvSWNw0RejfPVP7y6A")
token9 = oauth2.Token(key="1979279791-9X79gO6FsKqkIBK2ct73h101GZZgyTyEpWkLd09", secret="kT5JdOeybgmScy74qeDU2a3OBywvJJ0bGAfF72IDHHZJc")

#10) name: streaming api bot detection2
consumer10 = oauth2.Consumer(key="mrJtsTABCL8bhCiST3oF0xYuN", secret="dan23zYDbXc9oIGjXAMU3WbyKqeqYdRj4pWIG0So9fvqhTsuGi")
token10 = oauth2.Token(key="1979279791-aJUxu8Rd2SK3X7XFxcjN14gyL75x1ZQpSfoV6H8", secret="oUf9AdomderMawIi5td3d2sRr6MSpvI27mSdKsTvwZAUj")

tokenpool = [(consumer1, token1), (consumer2, token2), (consumer3, token3), (consumer4, token4), 
(consumer5, token5), (consumer6, token6), (consumer7, token7), (consumer8, token8), (consumer9, token9), (consumer10, token10)]

# tokenindex keeps track of which pair of consumer, token should be used from the pool
ROUND = len(tokenpool)
TIME_INTERVAL = 60.0/ROUND
tokenindex = 0

APIUrl = 'https://api.twitter.com/1.1/followers/ids.json'

# because json.dump can be called only once, ALL_data is a list that stores all tweets
withheld_flag = False


class FollowerFinder(object):
    """Class for finding followers for user"""

    def __init__(self, prefix):
        self.prefix = prefix

    def getFollowers(self, user_ids, filename = None):
        """The function gets followers from a list of users"""
        global tokenindex
        counter = 1
        user_follower_dic = {}
        for user in user_ids:
            # updating cursor each time, retrieve up to 75,000 followers
            # store all followers
            followers = []
            # default cursor value
            cursor = -1
            try:
                while (cursor != 0):
                    if cursor != -1:
                        # follow rate limitation, wait for 6s
                        time.sleep(TIME_INTERVAL)
                        # use tokenindex in a cyclical way
                        tokenindex += 1
                        tokenindex = tokenindex % ROUND
                    
                    url = APIUrl
                    params = {"oauth_version": "1.0", "oauth_nonce": oauth2.generate_nonce(), "oauth_timestamp": int(time.time())}
                    params["oauth_consumer_key"] = (tokenpool[tokenindex][0]).key
                    params["oauth_token"] = (tokenpool[tokenindex][1]).key
                    params["user_id"] = int(user)
                    params["cursor"] = cursor
                    params["stringify_ids"] = ""  # optional
                    params["count"] = 5000
                    
                    req = oauth2.Request(method="GET", url=url, parameters=params)
                    signature_method = oauth2.SignatureMethod_HMAC_SHA1()  # HMAC, twitter use sha-1 160 bit encryption
                    req.sign_request(signature_method, tokenpool[tokenindex][0], tokenpool[tokenindex][1])
                    # headers = req.to_header()
                    url = req.to_url()
                    response = urllib2.Request(url)
                    data = json.load(urllib2.urlopen(response))  # format results as json
                    cursor = data['next_cursor']

                    print "current cursor is ", cursor
                    print 'this cursor returns ', len(data["ids"]), ' number of followers'

                    """
                        ATTENTION: in case we are interested in all users

                    """
                    followers += data["ids"]

                # outside the while loop
                print user, ' has ', len(followers), ' number of followers'
                # print user, ' has followers: ', followers
                # print followers[0]
                # print type(followers[0])
                # print user_ids[0]
                # print type(user_ids[0])
                related_followers = [f for f in followers if f in userlist]
                print user, ' has ', len(related_followers), ' number of related followers'
                user_follower_dic[user] = related_followers
                # f.write(str(user) + ':')
                # for item in followers:
                #     f.write("," + str(item))
                # f.write('\n')
            except Exception, ex:
                print ""
                print "User id %d probably does not exist any more or is protected." %(user)
                print 'Exception: ' + str(ex)

            finally:
                print "this is " + str(counter) + " user"
                counter += 1
                print "take %fs rest....." %(TIME_INTERVAL)
                time.sleep(TIME_INTERVAL)
                # use tokenindex in a cyclical way
                tokenindex += 1
                tokenindex = tokenindex % ROUND

        # dump the whole dictionary into a pickle file
        if not filename:
            filename = self.prefix + "_user_followers_dic.json"
        else:
            filename += "_user_followers_dic.json"
        #print user_follower_dic
        with open(filename, 'w') as outfile:
            json.dump(user_follower_dic, outfile)


    def check_common_user(self, filename = None):
        if not filename:
                filename = self.prefix + "_user_followers_dic.json"
        else:
            filename += "_user_followers_dic.json"
        dic = json.load(open(filename,"r"))
        for k, v in dic.iteritems():
            if len(v) > 2:
                print k, " has %d common followers" % (len(v))
                #print v



    def get_common_user(self, filename = None):
        if not filename:
                filename = self.prefix + "user_followers_dic.p"
        else:
            filename += "user_followers_dic.p"
        dic = pickle.load(open(filename,"rb"))
        return dic


    def hasfile(self, filename):
        if not filename:
                filename = self.prefix + "user_followers_dic.p"
        else:
            filename += "user_followers_dic.p"
        return os.path.isfile(filename)


def load_file(filename):
    """
    A helper function that returns an iterable object

    """
    inputjson = open(filename, "r").read()
    jsonfields = json.loads(inputjson)
    # tweets_count=+len(jsonFields)
    
    return jsonfields


def loaduserlist(filename):
    res = set([])
    count = 1
    with open(filename, 'r') as f:
        for line in f:
            if count % 10000 == 0:
                print count
                #return res
            count += 1
            t = json.loads(line)
            res.add(t['id'])
                
    return res


if __name__ == '__main__':
    #myFollowerFinder = FollowerFinder(prefix = 'zhouhan_test')
    #myFollowerFinder.getFollowers([1979279791])
    
    """ IMPORTANT !!! """
    filename = 'du3a_all_user_info'
    #filename = 'savingzev_all_user_info'
    userlist = loaduserlist(filename + '.json')
    myFollowerFinder = FollowerFinder(prefix = filename)
    #myFollowerFinder.getFollowers(list(userlist)[:20])
    myFollowerFinder.check_common_user()


