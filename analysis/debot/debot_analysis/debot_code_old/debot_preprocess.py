import util

def generate_output_file(output_file_name, sourcefile):
	output_file = open(output_file_name,'w')
	for tweet in util.loadjson(sourcefile):
		output_file.write(str(tweet['created_at']) + "," + str(tweet['user']['screen_name']) + "," + str(tweet['user']['id'])+ "\n")
	output_file.close()
	
if __name__ == '__main__':
	output_file_name = 'debot_hillary.txt'
	DATA_DIR = "/Users/zc/Documents/twitter_research/github_code/twitter_research/data/stream/"
	sourcefile = DATA_DIR + 'tweets_hillary_json.txt'
	generate_output_file(output_file_name, sourcefile)
