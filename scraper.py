# import requests

import twitter
import json
import csv
import time
from apps import getAPI

import urllib2
import re

api_count = 6
api = getAPI(api_count)

api.InitializeRateLimit()


all_news_sites = []
fake_news_sites = [] 

with open('fake_news_sites.csv', 'rb') as f:
    reader = csv.reader(f)
    data = list(reader)
    for line in data:
    	name = line[0].split(".")[0].lower()
    	fake_news_sites.append({"name":name, "type":line[1], "reg":line[2]})

#for item in fake_news_sites:
	#print item



statuses = api.GetUserTimeline(screen_name="ninawang526",count=200)


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

def rate_limit(e, apc):
	if e is not None:
		if e[0][0]["code"] != 88:
			print e

	rl = api.CheckRateLimit("/friends/ids.json")
	print "current time:", time.strftime("%H:%M:%S", time.gmtime()) 
	print "api", apc % 18, "will resume at", time.strftime("%H:%M:%S", time.gmtime(rl[2])), "\n"

	time.sleep(60)

	new_api = getAPI(apc) 
	new_api.InitializeRateLimit()

	return new_api


f = open("retweetdata.txt", 'a')
inter = open("interrtdata.txt", 'a')

data = {}

#for s in statuses:
for i in range(0, 1):

	if i >= len(statuses):
		continue

	s = statuses[i]	

	source = s.retweeted_status
	if source is not None:
		for url in source.urls:

			# print retweeters
			rts = api.GetRetweeters(source.id, count=1000)
			likes = get_user_ids_of_post_likes(source.id)

			# my_id = api.GetUser(screen_name="ninawang526").id
			# myid = 173325385

			entry = {"TWEET_ID": source.id, "AUTHOR": source.id, 
					"URL": url.expanded_url, "RTS":{}, "LIKES":{}} # if this is a rt'd url

			# are any of them connected? what's the specific relationship 
			# just look at who each one follows (friends)
			rter_i = 0
			while rter_i < len(rts): # primary

				uid = rts[rter_i]
				# username = api.GetUser(user_id=uid).name
				print "at user", uid

				# frlt = folt = api.CheckRateLimit("/friends/ids")
				# folt = api.CheckRateLimit("/followers/ids")
				# print "friend limit t:", frlt
				# print "follower limit t:", folt

				try:
					user = api.GetUser(user_id=uid)
					num_friends = user.friends_count
					num_followers = user.followers_count

					friends = api.GetFriendIDs(user_id=uid,count=1000,total_count=1000)
					followers = api.GetFollowerIDs(user_id=uid,count=1000,total_count=1000)

					entry["RTS"][uid] = {"FRIENDS":{"count":num_friends, "ids":friends}, 
										"FOLLOWERS":{"count":num_followers, "ids":followers}}
					inter.write(json.dumps(entry["RTS"][uid]))

					rter_i += 1 #only when successful do you move on

					# network_rt = list(set(friends+followers).intersection(set(rts+[source.user.id])))
					# network_like = list(set(friends+followers).intersection(set(likes+[source.user.id])))
					# print "network rt", network_rt
					# print "network like", network_like

					#only do secondary on those who follow you.
					# check their relationship to everyone else

					# sec_data = {}
					# sec = 0
					# while sec < len(followers):  #secondary; friends of the retweeter
						
					# 	try:
					# 		sec_id = followers[sec]

					# 		# i don't think you need this. just check among the local network.
					# 		s_friends = api.GetFriendIDs(user_id=sec_id,count=5000,total_count=5000)
					# 		s_followers = api.GetFollowerIDs(user_id=sec_id,count=5000,total_count=5000)
						
					# 		sec_data[sec_id] = {"FRIENDS":s_friends, "FOLLOWERS":s_followers}
						
					# 		print "sec", sec, "/", len(followers), "has", len(s_friends), "friends"
					# 		sec += 1
					# 	except twitter.error.TwitterError as e:
					# 		api_count += 1
					# 		new_api = rate_limit(e, api_count)
					# 		api = new_api


				except twitter.error.TwitterError as e:
					api_count += 1
					new_api = rate_limit(None, api_count)
					api = new_api

			f.write(json.dumps(entry))


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