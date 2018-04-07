# import requests


# >>> users = api.GetFriends()
# >>> print([u.name for u in users])

# >>> status = api.PostUpdate('I love python-twitter!')
# >>> print(status.text)
# I love python-twitter!

# There are many other methods, including:

# >>> api.PostUpdates(status)
# >>> api.PostDirectMessage(user, text)
# >>> api.GetUser(user)
# >>> api.GetReplies()
# >>> api.GetUserTimeline(user)
# >>> api.GetHomeTimeline()
# GetStatus(status_id) # single status
# GetStatuses(status_ids)
# GetStatusOembed
# >>> api.GetFriends(user)
# >>> api.GetFollowers()
# >>> api.LookupFriendship(user)
# GetShortUrlLength
# GetSearch
# GetUsersSearch
# GetUserRetweets
# GetRetweets
# GetRetweeters
# GetRetweetsOfMe
# UsersLookup
# GetUserStream
# GetMentions


import twitter
import json
import csv
import time
from apps import getAPI

import urllib2
import re

api_count = 1
api = getAPI(api_count)


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


f = open("data.txt", 'a')
inter = open("inter.txt", 'a')

data = {}

#for s in statuses:
for i in range(0, 5):

	if i >= len(statuses):
		continue

	s = statuses[i]	

	if s.retweeted:
		source = s.retweeted_status
		
		if source is not None:
			urls = source.urls

			for url in urls:

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
				while rter_i < len(rts):

					uid = rts[rter_i]
					# username = api.GetUser(user_id=uid).name
					# print username

					try:
						friends = api.GetFriendIDs(user_id=uid)
						followers = api.GetFollowerIDs(user_id=uid)

						network_rt = list(set(friends+followers).intersection(set(rts+[source.user.id])))
						network_like = list(set(friends+followers).intersection(set(likes+[source.user.id])))
						
						print "network rt", network_rt
						print "network like", network_like

						#only do secondary on those who follow you.
						tertiary_data = {}
						tertiary = 0
						while tertiary < len(followers): 
							try:
								tertiary_id = followers[tertiary]
								# name =  api.GetUser(user_id=tertiary_id).name
								# print name

								t_friends = api.GetFriendIDs(user_id=tertiary_id)
								t_followers = api.GetFollowerIDs(user_id=tertiary_id)
							
								tertiary_data[tertiary_id] = {"FRIENDS":t_friends, "FOLLOWERS":t_followers}
							
								print "tert has", len(t_followers), "followers"
								tertiary += 1
							except twitter.error.TwitterError as e:
								if e[0][0]["code"] != 88:
									raise e
								print "t api", api_count % 15, "is busy at", time.strftime("%H:%M:%S", time.gmtime()) 
								api_count += 1
								api = getAPI(api_count) 
								time.sleep(60)

						entry["RTS"][uid] = {"FRIENDS":friends, "FOLLOWERS":tertiary_data}
						inter.write(json.dumps(entry["RTS"][uid]))

						rter_i += 1 #only when successful do you move on

					except twitter.error.TwitterError as e:	
						if e[0][0]["code"] != 88:
							raise e
						print "api", api_count % 15, "is busy at", time.strftime("%H:%M:%S", time.gmtime()) 
						api_count += 1
						api = getAPI(api_count) 
						time.sleep(60)


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