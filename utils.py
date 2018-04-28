import twitter
import time, csv
from apps import lenapis, getAPI


real_news = ["nyti.ms", "washingtonpost", "thehill", "huff.to", "cnn",
			"thenation.com", "n.pr", "nationalreview", "wsj", "bbc", "economist",
			"politico.com", "foxnews", "reut.rs", "fxn.ws"]

def fake_news():
	fake_news_sites = []
	with open('fake_news_sites.csv', 'rb') as f:
	    reader = csv.reader(f)
	    data = list(reader)
	    for line in data:
	    	name = line[0].split(".")[0].lower()
	    	if line[1] == "Fake news" or line[1]=="Some fake stories":
	    		fake_news_sites.append(name)
	return fake_news_sites


def is_fake(url):
	for fake_url in fake_news():
		if fake_url in url:
			print "FAKE", fake_url, url
			return True

	return False


def is_real(url, count):
	for real_url in real_news:
		if real_url in url:
			
			# keep track of what websites we've seen
			if real_url in count:
				
				if count[real_url] < 10:
					count[real_url] += 1
					print "REAL", url, count[real_url]
					return True

			else:
				count[real_url] = 1
				print "REAL", url, count[real_url]
				return True

	print url
	return False


def rate_limit(api, apc, app_only=False):
	rl = api.CheckRateLimit("/friends/ids.json")
	print "current time:", time.strftime("%H:%M:%S", time.gmtime()) 
	print "api", apc % lenapis, "will resume at", time.strftime("%H:%M:%S", time.gmtime(rl[2])), "\n"

	time.sleep(15)

	new_api = getAPI(apc, app_only=app_only) 
	new_api.InitializeRateLimit()

	return new_api


# error handling		
def continue_user(e):
	print e
	try:
		if e[0][0]["code"] == 88 or e[0][0]["code"] == 32: 
			return False
		else:
			return True
	except:
		return True


# def error_handle(f, loop_end):
# 	api_count = 0
# 	api = apps.getAPI(api_count)

# 	i = 0

# 	while i < 
# 	try:
# 		f(i)
# 		i += 1

# 	except twitter.error.TwitterError as e:
# 		if continue_user(e):
# 			counter += 1
# 		else:
# 			api_count += 1
# 			new_api = rate_limit(api, api_count)
# 			api = new_api
		
# 	except requests.exceptions.ConnectionError:
# 		time.sleep(60)
# 		api_count += 1
# 		new_api = rate_limit(api, api_count)
# 		api = new_api


