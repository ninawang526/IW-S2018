# import requests

import twitter, botometer
import json
import csv
import time
from apps import getAPI, lenapis

import urllib2
import re



#users = api.GetFriends(screen_name="MeghanSumz12")

#print "num statuses: ", (statuses[-1].created_at)

#https://stackoverflow.com/questions/28982850/twitter-api-getting-list-of-users-who-favorited-a-status
def get_user_ids_of_post_likes(post_id):
    try:
        json_data = urllib2.urlopen('https://twitter.com/i/activity/favorited_popup?id=' + str(post_id)).read()
        found_ids = re.findall(r'data-user-id=\\"+\d+', json_data)
        unique_ids = list(set([re.findall(r'\d+', match)[0] for match in found_ids]))
        ints = []
        for u in unique_ids:
        	ints.append(int(u))
        return ints
    except urllib2.HTTPError:
        return False


def rate_limit(api, apc, app_only=False):
	rl = api.CheckRateLimit("/friends/ids.json")
	print "current time:", time.strftime("%H:%M:%S", time.gmtime()) 
	print "api", apc % lenapis, "will resume at", time.strftime("%H:%M:%S", time.gmtime(rl[2])), "\n"

	time.sleep(20)

	new_api = getAPI(apc, app_only=app_only) 
	new_api.InitializeRateLimit()

	return new_api


def get_bom():
	bom_auth = { #api0
		"consumer_key": "WpLGb1jAHgxQw41AKAsNHGlOb",
		"consumer_secret": "lsFEN47IB9ZwGRvb2qXXXGw4KpPnl33vljycvh6B69GcikNnU0",
		"access_token_key": "173325385-KHvIPEzVNA0VYwBXt68xZ7dcPqS1gVBNAzXWrfix",
		"access_token_secret": "HY7en1wg75nAj1RVTVRfSAKkBDZKcoQC3gLoX92GjZmWi"
	}
	mashape_key = "cAhbRwLXRwmshEklALGsYExCYhVtp1DIqe6jsnrhGTz5LjPy4c"
	return botometer.Botometer(wait_on_ratelimit=True,
                          mashape_key=mashape_key,
                          **bom_auth)


# return {"count":,"ids":}
def ffuser(uid, api, use_bom=False):
	user = api.GetUser(user_id=uid)
	num_friends = user.friends_count
	num_followers = user.followers_count

	if use_bom:
		bom = get_bom()
		try:
			scores = bom.check_account(int(uid))
		except:
			return None

		if scores["scores"]["english"] < 0.6:
			# friends = api.GetFriendIDs(user_id=uid,count=1000,total_count=1000)
			followers = api.GetFollowerIDs(user_id=uid,count=1000,total_count=1000)
			return (num_friends, num_followers, followers)
		else:
			return None
	else:
		followers = api.GetFollowerIDs(user_id=uid,count=1000,total_count=1000)
		return (num_friends, num_followers, followers)



def getfriendsfollowers():
	api_count = 0
	api = getAPI(api_count)

	api.InitializeRateLimit()


	# all_news_sites = []
	# fake_news_sites = [] 

	# with open('fake_news_sites.csv', 'rb') as f:
	#     reader = csv.reader(f)
	#     data = list(reader)
	#     for line in data:
	#     	name = line[0].split(".")[0].lower()
	#     	fake_news_sites.append({"name":name, "type":line[1], "reg":line[2]})

	#for item in fake_news_sites:
		#print item

	statuses = api.GetUserTimeline(screen_name="ninawang526",count=200)


	f = open("retweetdata.txt", 'a')
	inter = open("interrtdata.txt", 'a')

	data = {}

	#for s in statuses:
	for i in range(0, 1):

		if i >= len(statuses):
			continue

		s = statuses[i]	

		source = s.retweeted_status #fix fix fix -- if it's your own post?
		if source is not None:
			for url in source.urls:

				author = source.user.id 

				# print retweeters & likers
				rts = api.GetRetweeters(source.id, count=1000) + [author]
				likes = get_user_ids_of_post_likes(source.id)

				entry = {"TWEET_ID": source.id, "AUTHOR": author, 
						"URL": url.expanded_url, "RTS":{}, "LIKES":likes} # if this is a rt'd url

				# for sake of computation, also include author in the rts

				# are any of them connected? what's the specific relationship 
				# just look at who each one follows (friends)
				rter_i = 0
				while rter_i < len(rts): # primary = retweeters

					uid = rts[rter_i]
					print "at user", rter_i, "/", len(rts), "uid =", uid

					try:
						res = ffuser(uid, api, use_bom=True)
						if res is not None:
							num_friends, num_followers, followers = res
						else:
							rter_i += 1
							continue
						
						sec_data = {}
						sec_i = 0
						while sec_i < len(followers):  # secondary = followers of retweeters
							
							sec_id = followers[sec_i]

							try:
								sec_res = ffuser(sec_id, api)
								if sec_res is not None:
									sec_num_friends, sec_num_followers, sec_followers = sec_res
								else:
									sec_i += 1
									continue
								
								sec_data[sec_id] = {"FRIENDS":{"count":sec_num_friends}, 
											"FOLLOWERS":{"count":sec_num_followers, "ids":sec_followers}}
							
								print "sec", sec_i, "/", len(followers), "has", sec_num_friends, "friends"
								sec_i += 1

							except twitter.error.TwitterError as e:
								print e
								try:
									l = e[0][0]["message"]
								except:
									print "NOTAUTH"
									sec_i += 1
								api_count += 1
								new_api = rate_limit(api, api_count)
								api = new_api

						entry["RTS"][uid] = {"FRIENDS":{"count":num_friends}, 
											"FOLLOWERS":{"count":num_followers, "ids":sec_data}}
						inter.write(json.dumps(entry["RTS"][uid]))

						rter_i += 1

					except twitter.error.TwitterError as e:
						print e
						try:
							l = e[0][0]["message"]
						except:
							print "NOTAUTH"
							rter_i += 1
						api_count += 1
						new_api = rate_limit(api, api_count)
						api = new_api

				f.write(json.dumps(entry))


def find_relations(networks):
	# next, for each status & each rt_network, find interrelations of people associated with it
	
	matrices = {}
	# 0 = no relationship
	# 1 = ui following uj
	# 2 = uj following ui
	# 3 = mutual

	i_network = 0
	network_keys = networks.keys()

	while i_network < len(network_keys): # for every status_network
		
		matrix = {}

		status_id = network_keys[i_network]
		users = list(networks[status_id])
		
		ui = 0 
		while ui < len(users): # for rter_network

			print "finding", ui, "/", len(users)

			uj = ui + 1
			while uj < len(users):
				# find dual relationship

				try:
					rel = api.ShowFriendship(source_user_id=users[ui], target_user_id=users[uj])["relationship"]
					
					val = 0
					if rel["source"]["following"] and rel["source"]["followed_by"]: 
						val = 3
					elif rel["source"]["followed_by"]:
						val = 2
					elif rel["source"]["following"]:
						val = 1

					if users[ui] in matrix:
						matrix[users[ui]][users[uj]] = val
					else:
						matrix[users[ui]] = {users[uj]:val}

					print users[ui], users[uj], val

					uj += 1

				except twitter.error.TwitterError as e:
					api_count += 1
					new_api = rate_limit(api, e, api_count, app_only=False)
					api = new_api

			ui += 1

		inter_relations.write(json.dumps(matrix))
		matrices[status_id] = matrix
		i_network += 1


def interrelationships(data):
	api_count = 0
	api = getAPI(api_count)
	api.InitializeRateLimit()

	relations = open("relationship_data.txt", "w")
	inter_relations = open("inter_relationship_data.txt", "w")
	  
	# first, for each status, get set of rters of that status
	networks = {} # dict of dicts, indexed by status id
	for status in data: #data is a list of dictionary entries
		
		status_network = {} #dict of rter_networks
		rters = status["RTS"] + status["LIKES"] 
		
		# for every rter-centered branch
		for uid in rters:
			rter_network = rters[uid]["FOLLOWERS"]["ids"] + [uid]
			status_network[uid] = rter_network # per rter 

		networks[status["TWEET_ID"]] = status_network  #dict of status_networks

	print "all networks:", networks

	
	print "DONE"
	relations.write(json.dumps(matrices))






if __name__ == '__main__':
	api_count = 0
	api = getAPI(api_count)
	api.InitializeRateLimit()

	uid = "940304486026940417"

	try:
		user = api.GetUser(user_id=uid)
	
		followers = api.GetFollowerIDs(user_id=uid,count=1000,total_count=1000)
		print "len", len(followers)	

	except twitter.error.TwitterError as e:
		try:
			print e[0][0]["message"]
		except:
			print "NOTAUTH"	



#postprocessing
#sitename = (url.expanded_url).split(".") 	#urls[0] type = URL
# if (sitename[0][:11] == "https://www" or sitename[0][:10] == "http://www" 
# 	or sitename[0][:13] == "https://on"):
# 	print sitename[1]
# else:
# 	print sitename[0][8:]

#print([(s.urls, s.text) for s in statuses])

"""
graph-based features

plan of action:
	for each tweet in dataset (200 c.):
		check metadata -- store if there is a [fake] news link involved. 
			- if retweeted, go to source.
			- if not, check who retweeted it.
		
		tweet data:
			tweet timestamp
			everyone who retweeted it
		
		user data: # of friends

		crawl BFS: GET statuses/retweeters/ids

		user data:


# should probably start with the fake tweet as the origin.--> 
#then go through users who rt.


scp -i ~/iw/iw2.pem ~/iw  ec2-user@ec2-18-188-192-246.us-east-2.compute.amazonaws.com:~/data/

"""














#