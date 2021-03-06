import twitter, botometer
import requests
import json, gzip, os.path
import csv
import time
from apps import getAPI, lenapis

import urllib2
import re
import utils

# get rid of repeat statuses
def get_source(filename):
	api_count = 0
	api = getAPI(api_count)

	bins = {}

	with open(filename, "r") as f:
		l = json.loads(f.read())
	
	i = 0
	keys = l.keys()
	while i < len(keys):
		status_id = int(keys[i])
		print i
		try:
			s = api.GetStatus(status_id)

			# getting to the source status
			source = s.retweeted_status
			if source is None:
				source = s

			if source.id not in bins:
				url = l[str(status_id)]
				bins[source.id] = url

			i += 1

		except twitter.error.TwitterError as e:
			if utils.continue_user(e):
				i += 1
			else:
				api_count += 1
				new_api = utils.rate_limit(api, api_count, app_only=False)
				api = new_api	
	return bins


def get_relevant_statuses():
	api_count = 0
	api = getAPI(api_count)

	with open("election-filter1.txt") as f:

		real_dict = {}
		real_count = 0
		fake_count = 0

		real = {}
		fake = {}

		for line in f:
			status_id = int(line)
			
			try:
				s = api.GetStatus(status_id)

				if fake_count >= 100 and real_count >= 100:
					break

				if len(s.urls) == 0:
					continue
				
				url = s.urls[0].expanded_url

				if utils.is_fake(url) and fake_count < 100:
					fake[status_id] = url
					fake_count += 1

				elif utils.is_real(url, real_dict) and real_count < 100:
					real[status_id] = url
					real_count += 1


			except twitter.error.TwitterError as e:
				if utils.continue_user(e):
					continue
				else:
					api_count += 1
					new_api = utils.rate_limit(api, api_count, app_only=False)
					api = new_api	

	print "DONE"
	# with open("fakeids.txt", "w") as f:
	# 	f.write(json.dumps(fake))
	# with open("realids.txt", "w") as f:
	# 	f.write(json.dumps(real))
	return real, fake


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
        return []


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

	followers = api.GetFollowerIDs(user_id=uid,count=50,total_count=50)
	friends = api.GetFriendIDs(user_id=uid,count=50,total_count=50)
	return (num_friends, friends, num_followers, followers)


# get friends & follower network of a particular status
def getfriendsfollowers(status_id):
	api_count = 0
	api = getAPI(api_count, sleep_on_rate_limit=True)

	save_path = "./rters/" + str(status_id) #CHANGE THIS! IDS CHANGE..???
	if not os.path.exists(save_path):
		os.makedirs(save_path)
	
	ignore = [int(x.split(".")[0]) for x in os.listdir(save_path)]

	source = api.GetStatus(int(status_id))

	# getting info
	author = source.user.id 
	created_at = source.created_at
	urls = [url.expanded_url for url in source.urls]
	print "text:", source.text
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


	api_count = 1
	api = getAPI(api_count)

	# just look at who each one follows (friends)
	rter_i = 0
	while rter_i < len(rts): # primary = retweeters

		# if rter_i == 5:
		# 	break

		uid = rts[rter_i]
		print "at rter", rter_i, "/", len(rts), "uid =", uid, "created_at", times[uid]
		
		if int(uid) in ignore:
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

				if int(sec_id) in ignore:
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
					if utils.continue_user(e):
						sec_i += 1
					else:
						api_count += 1
						new_api = utils.rate_limit(api, api_count)
						api = new_api

				except requests.exceptions.ConnectionError:
					time.sleep(60)
					api_count += 1
					new_api = utils.rate_limit(api, api_count)
					api = new_api

			status_entry["RTS"][uid] = {"RT_AT":times[uid], "FRIENDS":{"count":num_friends, "ids":friends}, 
										"FOLLOWERS":{"count":num_followers, "ids":sec_data}}
			
			rter_i += 1
	
			complete_name = os.path.join(save_path, str(uid)+".txt.gz")
			inter = gzip.open(complete_name, 'wb')
			inter.write(json.dumps(status_entry["RTS"][uid])) # writing for each rter
			inter.close()
			print "WROTE", str(uid)+".txt.gz"

		except twitter.error.TwitterError as e:
			if utils.continue_user(e):
				rter_i += 1
			else:
				api_count += 1
				new_api = utils.rate_limit(api, api_count)
				api = new_api
		
		except requests.exceptions.ConnectionError:
			time.sleep(60)
			api_count += 1
			new_api = utils.rate_limit(api, api_count)
			api = new_api
		
	f = gzip.open("retweetdata.txt.gz", 'wb')
	f.write(json.dumps(status_entry)) # writing for each status	
	f.close()

	return status_entry


# for one status, find network-specific relations
def specific_relationships(status, api_count):
	api = getAPI(api_count)

	# first, get set of all associated with that status
	status_network = set([status["AUTHOR"]])
	rters = status["RTS"]

	start = time.time()

	secs = []

	for uid in rters.keys():
		user = rters[uid] 
		s = user["FOLLOWERS"]["ids"].keys()[:5]
		secs += s
		network = s + [uid]
		status_network.update(set(network))

	# next,find interrelations of people associated with it
	users = list(status_network)
	relations, api_count = relations_check(users, api_count)

	#print "time elapsed:", 1.5 mins
	
	data = {"relations":relations, "secs":secs}
	return data, api_count


def relations_check(users, api_count):
	api = getAPI(api_count)
	api.InitializeRateLimit()

	relations = {}
	# 0 = no relationship
	# 1 = ui following uj
	# 2 = uj following ui
	# 3 = mutual

	ui = 0 
	while ui < len(users):
		print "ui=", ui, "/", len(users)

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

				if (uj % 5 == 0):
					print "\tui=",ui,"uj=",uj,"val=", val

				# store only if an edge exists
				if val != 0: 
					if users[ui] in relations:
						relations[users[ui]][users[uj]] = val
					else:
						relations[users[ui]] = {users[uj]:val}
				uj += 1

			except twitter.error.TwitterError as e:
				if utils.continue_user(e):
					uj += 1
				else:
					api_count += 1
					new_api = utils.rate_limit(api, api_count, app_only=False)
					api = new_api

			except requests.exceptions.ConnectionError:
				time.sleep(60)
				api_count += 1
				new_api = utils.rate_limit(api, api_count)
				api = new_api

		ui += 1

	return relations, api_count



# for one status, find general relations of each user exposed to status
def general_relationships(uid, rter_data, api_count):
	# for each exposed user, get all those who follow them, see if mutual
	relations = {}
	
	# author does NOT count as a secondary. only rters (primary = author)
	# and followers of rters (primary = rter)

	secondaries = rter_data["FOLLOWERS"]["ids"]

	sec_users = [uid] + secondaries.keys()[:5] + rter_data["FRIENDS"]["ids"][:5]
	sec_relations, api_count = relations_check(sec_users, api_count)

	relations.update(sec_relations)

	secs = []
	for sec in secondaries.keys()[:1]:
		secs.append(sec)

		tertiaries = secondaries[sec]["FRIENDS"]["ids"][:5] + secondaries[sec]["FOLLOWERS"]["ids"][:5]

		tert_users = tertiaries + [sec]
		tert_relations, api_count = relations_check(tert_users, api_count)

		relations.update(tert_relations)
	
	data = {"relations":relations, "secs":secs}
	return data, api_count



def recover_status(sid):
	api = getAPI(0, sleep_on_rate_limit=True)
	try:
		s = api.GetStatus(int(sid))
	except twitter.error.TwitterError as e:
		return None

	return {"RTS":{}, "LIKES":{}, "AUTHOR":s.user.id , "TIME":s.created_at}






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


sudo scp -i ~/iw/iw2.pem ~/iw/fake.tar.gz  ec2-user@ec2-52-14-133-230.us-east-2.compute.amazonaws.com:~/IW-S2018/RTER-FILES

sudo scp -i ~/iw/iw2.pem  ec2-user@ec2-18-188-68-9.us-east-2.compute.amazonaws.com:~/IW-S2018/rters/fake.tar.gz ~/iw/

tar -zcvf fake.tar.gz ~/iw/RTER-FILES/FAKE

"""
# ['144265513', '859403739253407744', '853341295', '2971940812', '899115298997055491', '957146205825437696', '97212964', '1623513960', '1935424308', '22296700', '842871807770152964', '834485300143456256']







#