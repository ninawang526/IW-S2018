import twitter
import time
from apps import lenapis, getAPI

# handles setting up new apis
def rate_limit(api, apc, app_only=False):
	rl = api.CheckRateLimit("/friends/ids.json")
	print "current time:", time.strftime("%H:%M:%S", time.gmtime()) 
	print "api", apc % lenapis, "will resume at", time.strftime("%H:%M:%S", time.gmtime(rl[2])), "\n"

	time.sleep(30)

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


