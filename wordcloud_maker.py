#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Generating a square wordcloud from the US constitution using default arguments.
"""

from os import path
from wordcloud import WordCloud, STOPWORDS
import crawler

stopwords = set(STOPWORDS)
stopwords.add("said")
stopwords.add("https")
stopwords.add("co")
stopwords.add("RT")

d = path.dirname(__file__)

def get_text():
	# promotion eviejohnson88 GET PAID FOR DOING THINGS
	# promotion JackieArcher66 FOLLOW US/RETWEET type bot
	# promotion adidasSG_ shoes NIKE, ADIDAS
	# promotion AnitaNita59 VERY GOOD EXAMPLE (free... stuff)
	# https://twitter.com/AnitaNita59
	# porn naughty_girl_96
	# promotion uber lyft sohexomyrody
	# promotion music PROMOBOYZ1
	# free ride wazenecidez
	# click bait free chip card read SocialInLoudoun
	myUserCrawler = crawler.UserCrawler(simplecrawl = True, only200 = True)
	result = myUserCrawler.get200('AnitaNita59', use_screen_name = True, return_error_code = False)
	text = ' '.join([t['text'] for t in result])
	return text

# Read the whole text.
#text = open(path.join(d, 'constitution.txt')).read()

def generate_cloud(text, filename):
	# Generate a word cloud image
	wordcloud = WordCloud().generate(text)

	# Display the generated image:
	# the matplotlib way:
	import matplotlib.pyplot as plt
	#plt.imshow(wordcloud, interpolation='bilinear')
	#plt.axis("off")

	# lower max_font_size
	wordcloud = WordCloud(background_color="white", width=1600, height=800, 
						  stopwords=stopwords).generate(text)
	#plt.figure()
	plt.figure(figsize=(20,10), facecolor='k')
	plt.axis("off")
	plt.imshow(wordcloud, interpolation="bilinear")
	plt.tight_layout(pad=0)
	if filename:
		#plt.savefig(filename)
		plt.savefig(filename, facecolor='k', bbox_inches='tight')
	plt.show()

generate_cloud(get_text(), 'wordcloud_plot/promotion2_account_wordcloud_white')

