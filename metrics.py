from apps import getAPI
from scraper import get_user_ids_of_post_likes
import datetime
from dateutil.parser import parse


# returns dictionary of u1-u2 relationship
def edge_data(user1, targets): #target is list of INTS
	api_count = 0
	api = getAPI(api_count)

	# get timeline of user 1 -- returns 200 of user's most recent tweets
	t1 = api.GetUserTimeline(user1, count=200)

	print "len timeline =", len(t1)

	print "source from", api.GetUser(user_id=user1).screen_name

	data = {}
	for t in targets:
		data[t] = {"replies": 0, "likes": 0, "rts": 0, "mentions": 0}

	i = 0
	while i < len(t1):

		if i == 50:
			break

		# better way is to gather all of u1's destinations & check at once. 
		# iterate through the nodes rather than the edges.

		s1 = t1[i]
		print "checking", i, "/", len(t1)

		# user mentions
		mentions = s1.user_mentions
		if len(mentions) > 0:
			for m in mentions:
				if m.id in targets:
					data[m.id]["mentions"] += 1
					print "mentions +1"

		# in reply to
		reply = s1.in_reply_to_user_id
		if reply is not None:
			if reply in targets:
				data[reply]["replies"] += 1
				print "replies +1"

		# did u1 retweet from u2?
		rt = s1.retweeted_status
		if rt is not None:
			if rt.user.id in targets:
				data[rt.user.id]["rts"] += 1
				print "rts +1"
		
		# did u2 like things from u1?
		likes = get_user_ids_of_post_likes(s1.id)
		for l in likes:
			if int(l) in targets:
				data[l]["likes"] += 1
				print "likes +1"

		i += 1

	if len(t1) == 0:
		return None

	s1 = parse(t1[0].created_at)
	s2 = parse(t1[-1].created_at)

	time_range = (s1-s2).days
	print "time_range", time_range

	return data, time_range



def edge_weight(user1, targets):
	# NOTE: calculate density by averaging over first post & last post.

	data, time_range = edge_data(user1, targets)

	if time_range == 0:
		return 0

	weights = {}
	for user in data.keys():
		d = data[user]

		reply_score = 3 * d["replies"] 
		like_score = 1 * d["likes"] 
		rt_score = 2 * d["rts"] 
		mentions_score = 3 * d["replies"] 

		weights[user] = (reply_score + like_score + rt_score + mentions_score) / double(time_range)

	return weights

		# if interactions are spaced out over time, or in one rapid burst
		# should regularity matter..? i don't think so. i think just
		# span of time should matter. density? should that matter?
		# maybe yes it should matter only in the positive direction.

		# yes -- the regularity of interactions.

		# how to determine edgeweight of 2 directional (double it?)
		# because mutuality definitely strengthens edgeweight, even if
		# rt/like behavior doesn't capture that. 
		# to make sure don't repeat, just calculate for outgoing edges
		# wait..repeats are ok. just add to that score.
		# just don't add the mutual constant twice. -- just add for smaller id.


def node_weight(user):
	
	# how active the user is

	# botscore

	# average edgescores
	
	pass



