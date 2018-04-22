import twitter, botometer
import requests
import json, gzip, os.path
import csv
import time
from apps import getAPI, lenapis

import urllib2
import re


# scrape for likes of a status
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
		if e[0][0]["code"] == 88 or e[0][0]["code"] == 88:
			return False
		else:
			return True
	except:
		return True


# botometer intialization
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


# get friends & followers of a particular user; return {"count":,"ids":}
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

		if scores["scores"]["english"] >= 0.6:
			return None

	followers = api.GetFollowerIDs(user_id=uid,count=250,total_count=250)
	friends = api.GetFriendIDs(user_id=uid,count=250,total_count=250)
	return (num_friends, friends, num_followers, followers)


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


# get friends & follower network of a particular status
def getfriendsfollowers(status_id):
	api_count = 0
	api = getAPI(api_count)
	api.InitializeRateLimit()

	f = gzip.open("retweetdata.txt.gz", 'wb')
	save_path = "/Users/ninawang/iw/rters/" + str(status_id)
	if not os.path.exists(save_path):
		os.makedirs(save_path)
	
	ignore = [x.split(".")[0] for x in os.listdir(save_path)]

	s = api.GetStatus(int(status_id))
	source = s.retweeted_status #fix fix fix -- if it's your own post?

	if source is None:
		return None 

	#Get info
	author = source.user.id 
	created_at = source.created_at
	urls = [url.expanded_url for url in source.urls]
	print "source created at", created_at

	# print retweeters & likers
	likes = get_user_ids_of_post_likes(source.id)

	rt_statuses = api.GetRetweets(source.id, count=1000) 
	rts = [author]
	times = {author:created_at}
	for s in rt_statuses:
		uid = str(s.user.id)
		rts.append(uid)
		times[uid] = s.created_at

	
	# entry for each status, indexed by status_id
	status_entry = {"TIME":created_at,"AUTHOR": author, 
					"URL":urls, "RTS":{}, "LIKES":likes} # if this is a rt'd url


	# just look at who each one follows (friends)
	rter_i = 0
	while rter_i < len(rts): # primary = retweeters

		# if rter_i == 5:
		# 	break

		uid = rts[rter_i]
		print "at rter", rter_i, "/", len(rts), "uid =", uid, "created_at", times[uid]
		
		if uid in ignore:
			rter_i += 1
			print "ignored", uid
			continue

		try:
			res = ffuser(uid, api)
			if res is not None:
				num_friends, friends, num_followers, followers = res
			else:
				rter_i += 1
				continue
			
			sec_data = {}
			sec_i = 0
			while sec_i < len(followers):  # secondary = followers of retweeters
				
				# if sec_i == 5:
				# 	break

				sec_id = followers[sec_i]

				if sec_id in ignore:
					sec_i += 1
					print "ignored", sec_id
					continue

				try:
					sec_res = ffuser(sec_id, api)
					if sec_res is not None:
						sec_num_friends, sec_friends, sec_num_followers, sec_followers = sec_res
					else:
						sec_i += 1
						continue
					
					# ~~~ ONLY FIVE!!!! ~~~
					sec_data[sec_id] = {"FRIENDS":{"count":sec_num_friends, "ids":sec_friends}, 
								"FOLLOWERS":{"count":sec_num_followers,"ids":sec_followers}}
				
					print "sec", sec_i, "/", len(followers), "has", sec_num_friends, "friends"
					sec_i += 1

				except twitter.error.TwitterError as e:
					if continue_user(e):
						sec_i += 1
					else:
						api_count += 1
						new_api = rate_limit(api, api_count)
						api = new_api

				except requests.exceptions.ConnectionError:
					time.sleep(60)
					api_count += 1
					new_api = rate_limit(api, api_count)
					api = new_api

			status_entry["RTS"][uid] = {"RT_AT":times[uid], "FRIENDS":{"count":num_friends, "ids":friends}, 
										"FOLLOWERS":{"count":num_followers, "ids":sec_data}}
			rter_i += 1

			complete_name = os.path.join(save_path, str(uid)+".txt.gz")
			inter = gzip.open(complete_name, 'wb')
			inter.write(json.dumps(status_entry["RTS"][uid])) # writing for each rter
			inter.close()

		except twitter.error.TwitterError as e:
			if continue_user(e):
				rter_i += 1
			else:
				api_count += 1
				new_api = rate_limit(api, api_count)
				api = new_api
		
		except requests.exceptions.ConnectionError:
			time.sleep(60)
			api_count += 1
			new_api = rate_limit(api, api_count)
			api = new_api
		
	f.write(json.dumps(status_entry)) # writing for each status	
	f.close()

	return status_entry


# for one status, find network-specific relations
def specific_relationships(status):
	api_count = 0
	api = getAPI(api_count)
	api.InitializeRateLimit()

	f = open("specific_relationship_data.txt", "w")
	  
	# first, for each status, get set of all associated with that status
	status_network = set([status["AUTHOR"]])
	rters = status["RTS"] 
	
	for uid in rters:
		user = rters[uid] 
		# add rter's followers and rter
		network = user["FOLLOWERS"]["ids"].keys() + [uid]
		status_network.update(set(network))

	print "network:", status_network


	# next, for each status, find interrelations of people associated with it
	relations = {}
	users = list(status_network)
	
	# 0 = no relationship
	# 1 = ui following uj
	# 2 = uj following ui
	# 3 = mutual

	ui = 0 
	while ui < len(users):

		print "finding", ui, "/", len(users)

		uj = ui + 1
		while uj < len(users):
			try:
				rel = api.ShowFriendship(source_user_id=users[ui], target_user_id=users[uj])["relationship"]
				
				val = 0
				if rel["source"]["following"] and rel["source"]["followed_by"]: 
					val = 3
				elif rel["source"]["followed_by"]:
					val = 2
				elif rel["source"]["following"]:
					val = 1

				# store only if an edge exists
				if val != 0: 
					if users[ui] in relations:
						relations[users[ui]][users[uj]] = val
					else:
						relations[users[ui]] = {users[uj]:val}

				# print users[ui], users[uj], val
				uj += 1

			except twitter.error.TwitterError as e:
				if continue_user(e):
					uj += 1
				else:
					api_count += 1
					new_api = rate_limit(api, api_count, app_only=False)
					api = new_api

			except requests.exceptions.ConnectionError:
				time.sleep(60)
				api_count += 1
				new_api = rate_limit(api, api_count)
				api = new_api

		ui += 1

	f.write(json.dumps(relations))
	return relations


def relations_check(root, subtree):
	api_count = 0
	api = getAPI(api_count)
	api.InitializeRateLimit()

	relations = {}
	# 0 = no relationship
	# 1 = ui following uj
	# 2 = uj following ui
	# 3 = mutual
	
	i = 0
	while i < len(subtree):
		source = root 
		dest = subtree[i]

		try:
			rel = api.ShowFriendship(source_user_id=source, target_user_id=dest)["relationship"]
			
			val = 0
			if rel["source"]["following"] and rel["source"]["followed_by"]: 
				val = 3
			elif rel["source"]["followed_by"]:
				val = 2
			elif rel["source"]["following"]:
				val = 1

			# store only if an edge exists
			if val != 0: 
				if source in relations:
					relations[source][dest] = val
				else:
					relations[source] = {dest:val}

			print source, dest, i, val
			i += 1

		except twitter.error.TwitterError as e:
			if continue_user(e):
				i += 1
			else:
				api_count += 1
				new_api = rate_limit(api, api_count, app_only=False)
				api = new_api

		except requests.exceptions.ConnectionError:
			time.sleep(60)
			api_count += 1
			new_api = rate_limit(api, api_count)
			api = new_api

	return relations


# for one status, find general relations of each user exposed to status
def general_relationships(status):
	api_count = 0
	api = getAPI(api_count)
	api.InitializeRateLimit()

	f = open("general_relationship_data.txt", "w")
	  
	# for each exposed user, get all those who follow them, see if mutual
	relations = {}
	rters = status["RTS"] 
	
	# author does NOT count as a secondary. only rters (primary = author)
	# and followers of rters (primary = rter)
	for uid in rters:
		rter = rters[uid]

		secondaries = rter["FOLLOWERS"]["ids"]
		sec_relations = relations_check(uid, secondaries.keys())
		relations.update(sec_relations)

		for sec in secondaries:
			tertiaries = secondaries[sec]["FRIENDS"]["ids"]
			tert_relations = relations_check(sec, tertiaries)
			relations.update(tert_relations)

	f.write(json.dumps(relations))
	return relations


if __name__ == '__main__':
	rtdata = open("retweetdata.txt", "r").read()
	retweet_data = json.loads(rtdata)

	for s_id in retweet_data:
		status_network = retweet_data[s_id]
		
		relations = general_relationships(status_network)
		print relations




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