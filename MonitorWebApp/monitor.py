from flask import Flask, url_for, jsonify, send_from_directory
from flask import render_template
import json
from flask import request
from flask import Response
from jinja2 import Environment, FileSystemLoader
from werkzeug.contrib.fixers import ProxyFix
import sys
import os
import os.path
import subprocess
import random
import pprint
import datetime

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

directory = None
prefix = None 
spam_group = None
user_info = None 

def load_directory():
    # directory will be the first entry
    with open('config.txt', 'r') as f:
        for line in f:
            return line.strip()
directory = load_directory()
parent_directory = directory
directory += '/processed_data/'

def get_url_entry():
    with open('config.txt', 'r') as f:
        contents = []
        for line in f:
            contents.append(line.strip())
        return contents[1:]

@app.route('/')
def monitor():
    ## ['viid', 'goo', 'bit', 'dld', 'ift', 'dlvr']
    entries = get_url_entry()
    return render_template("index.html", 
            entries=entries)


@app.route('/socialnetwork/<path:filename>')
def base_static(filename):
    return send_from_directory(parent_directory + '/gephi/', filename, as_attachment=True)


@app.route('/urlinfo', methods = ['POST'])
def urlinfo():
    print '[monitor] return latest url info'
    url_info = json.load(open(parent_directory + '/twitter_stream_url_info.json', 'r'))
    
    barchart = []
    piechart = []
    num_entry = 0
    top_20_count = 0

    # define colors for Top URLs
    color_schema = {"good": "#71c100", "url_shorteners": "#ff9a00", "quran": "#ff0000", "news": "#6fa32e"}
    url_category = {"good": ["twitter.com", "fb.me", "youtu.be"],
                    "quran": ["du3a.org", "d3waapp.org", "7asnat.com", 
                              "zad-muslim.com", "ghared.com", "Quran.to", "7asnh.com"],
                    "url_shorteners": ["bit.ly", "dlvr.it", "ift.tt", "t.co", 
                                       "ow.ly", "ln.is", "goo.gl", "buff.ly", "viid.me",
                                       "tinyurl.com", "bnent.jp", "smarturl.it", "prt.nu"],
                    "news": ["wapo.st", "cnn.it"]}
    # default color
    
    for text, count in zip(url_info['url_text'], url_info['url_count']):
        color = "#5e9cf2"
        for category, urls in url_category.iteritems():
            if text in urls:
                color = color_schema[category]
                break
        barchart.append({'y': count, 'label': text, 'color': color, 'link':"http://"+text})
        if num_entry < 20:
            piechart.append({'y': count, 'indexLabel': text, 'legendText': text, 'color': color, 'link':"http://"+text})
            top_20_count += count
        num_entry += 1
    
    piechart.append({'y': url_info['total_url']-top_20_count, 'indexLabel': 'other', 'legendText': 'other', 'color': "#5e9cf2"})

    final_result = {'total_url':url_info['total_url'] ,'piechart':piechart, 'barchart': barchart}
    return Response(json.dumps(final_result), mimetype='application/json')

@app.route('/refresh', methods = ['POST'])
def refresh():
    jsonData = request.get_json()
    new_prefix = jsonData['prefix']
    spam_group_id = jsonData['spam_group_id']
    print new_prefix, spam_group_id
    final_result = {}
    if not prefix or new_prefix != prefix:
        global spam_group, user_info
        spam_group = json.load(open(directory + new_prefix + '/' + new_prefix + '_tweet_spam_group.json', 'r'))
        user_info = json.load(open(directory + new_prefix + '/' + new_prefix + '_tweet_user_info.json', 'r'))
        final_result['metatable'] = get_spam_group_metainfo()
    
    print "[monitor] length of spam group is %d", len(spam_group)
    print "[monitor] getting data for spam group %s" %(spam_group_id)
    final_result['usertable'] = get_userinfo_by_id(int(spam_group_id))
    
    final_result['socialnetwork'] = socialnetwork_file_exist(new_prefix, spam_group_id)

    print "[monitor] send back data"
    return Response(json.dumps(final_result), mimetype='application/json')
    


def get_userinfo_by_id(spam_group_id):
    result = []
    for user in spam_group[spam_group.keys()[spam_group_id - 1]]['spam_user']:
            create = datetime.datetime.strptime(user_info[str(user)]['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            s_name = user_info[str(user)]['screen_name']
            screen_name_url = "<a href='http://www.twitter.com/" + s_name + "'>" + s_name + "</a>"
            result.append({'id': user, 'screen_name': screen_name_url,
                           #'profile': user_info[str(user)]['profile'][:-10] + 'normal.jpg', 
                           'profile': user_info[str(user)]['profile'],
                           'created_at': str(create),
                           'statuses_count': user_info[str(user)]['statuses_count'],
                           'friends_count': user_info[str(user)]['friends_count'],
                           'followers_count': user_info[str(user)]['followers_count'],
                           'lang': user_info[str(user)]['lang'],
                           'verified': user_info[str(user)]['verified']})
    print "length of result: ", len(result)
    return result

def get_spam_group_metainfo():
    result = []
    for index, group in enumerate(spam_group.keys()):
        if isinstance(spam_group[group]['top_one_website'], basestring):
            website = spam_group[group]['top_one_website']
        else:
            try:
                website = spam_group[group]['top_one_website'][0][0]
            except Exception, e:
                print e
                website = 'N/A'
        
        id_url = str(index+1)
        top_one_website_html = "<a href='http://" + website + "'>" + website + "</a>"
        result.append({'spam_group_id': id_url, 
                       'total_user': len(spam_group[group]['spam_user']),
                       'top_one_website': top_one_website_html})
    return result

def socialnetwork_file_exist(prefix, spam_group_id):
    #return "socialnetwork/bit_bot_group_10.json"
    if os.path.isfile(parent_directory + '/gephi/' + prefix + "_bot_group_" + str(spam_group_id) + ".json"):
        return 'socialnetwork/' + prefix + "_bot_group_" + str(spam_group_id) + ".json"
    else:
        return '404'

@app.route('/loadnetwork')
def load_network():
    filename = request.args.get('filename')
    if "404" in filename:
        return render_template("social_network_404.html", 
            filename=filename)
    else:
        return render_template("social_network.html", 
            filename=filename)

# def get_all_prefix():
#     res = set()
#     for root, dirs, filenames in os.walk(LOG_DIR):
#         for fn in filenames:
#             if len(fn) > 16:
#                 res.add(fn[:16])
#     return sorted(list(res)) 


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=18000, debug = False)
