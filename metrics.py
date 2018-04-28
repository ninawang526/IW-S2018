from apps import getAPI
from scraper import get_user_ids_of_post_likes
import datetime
from dateutil.parser import parse
import utils
import time




def check_interaction(sid, tid, targets, node_d, edge_d, social_set, key):
	assert(type([sid]) == type(targets))
	sid = int(sid)
	assert(type(sid) == type(tid))
				
	# node
	if tid != sid:
		node_d[key] += 1
		if tid not in social_set:
			social_set.add(tid)

	# vertex
	if tid in targets:
		edge_d[tid][key] += 1
		print tid, key, "+1"


# returns dictionary of u1-u2 relationship
def user_statuses(user1, targets): #target is list of INTS
	api_count = 0
	api = getAPI(api_count)

	# initialize data
	data = {}
	for t in targets:
		data[t] = {"replies": 0, "likes": 0, "rts": 0, "mentions": 0}

	# if user1 != "2394624246": #and user1 != "901448812283269121":
	# 	return {"replies": 0, "likes": 0, "rts": 0, "mentions": 0},data, 0

	social = {"replies": 0, "rts": 0, "mentions": 0}
	social_set = set()


	# get timeline of user 1 -- returns 200 of user's most recent tweets
	try:
		t1 = api.GetUserTimeline(user1, count=200)
		print "finding weights from", api.GetUser(user_id=user1).screen_name, "uid =", user1
		
	except twitter.error.TwitterError as e:
		if utils.continue_user(e):
			return social, social_set, data, 0
		else:
			api_count += 1
			new_api = utils.rate_limit(api, api_count, app_only=False)
			api = new_api
	except requests.exceptions.ConnectionError:
		time.sleep(60)
		api_count += 1
		new_api = utils.rate_limit(api, api_count)
		api = new_api
	

	i = 0
	while i < len(t1):

		# if i == 10:
		# 	break

		s1 = t1[i]

		# did u1 mention u2
		mentions = s1.user_mentions
		if len(mentions) > 0:
			for m in mentions:
				check_interaction(user1, m.id, targets, social, data, social_set, key="mentions")


		# did u1 reply to u2
		reply = s1.in_reply_to_user_id
		if reply is not None:
			check_interaction(user1, reply, targets, social, data, social_set, key="replies")


		# did u1 retweet from u2?
		rt = s1.retweeted_status
		if rt is not None:
			check_interaction(user1, rt.user.id, targets, social, data, social_set, key="rts")


		# did u2 like things from u1?
		likes = get_user_ids_of_post_likes(s1.id)
		for l in likes:
			assert(type([int(l)]) == type(targets))
			if int(l) in targets:
				data[l]["likes"] += 1
				print l, "likes +1"

		i += 1

	return social, social_set, data, len(t1)



def normalize_weights(metric, iterate, padding=0):
	minimum = min(metric)
	maximum = max(metric)
	r = float(maximum - minimum)
	print minimum, maximum, r

	for i in iterate:
		score = metric[i]
		if r == 0:
			metric[i] = padding
		else:
			metric[i] = padding + ((score-minimum) / r) 	# on range [padding, padding+1]

	return metric


def edge_weight(user1, targets):
	# NOTE: calculate density by averaging over first post & last post.

	node_data, social_set, edge_data, num = user_statuses(user1, targets)


	# NODE WEIGHTS - social
	rep = node_data["replies"]
	rts = node_data["rts"]
	ments = node_data["mentions"]

	node_sum = ((3 * rep) + (2 * rts) + (3 * ments))
	if num == 0:
		social = 0
	else:
		social = node_sum / float(num)

	# NODE WEIGHTS - diversity
	if len(social_set) == 0:
		diversity = 0
	else:
		diversity = len(social_set) / float(rep+rts+ments) # diversity = percentage of interactive posts being w diff ppl


	# EDGE WEIGHTS
	edge_weights = {}
	for user in edge_data.keys():
		d = edge_data[user]

		# maybe there should be a blanket score of if there's interaction at all.
		if (d["replies"] > 0) or (d["likes"] > 0) or (d["rts"] > 0) or (d["mentions"] > 0):
			padding = 2
		else:
			padding = 1

		reply_score = 3 * d["replies"]  
		like_score = 1 * d["likes"] 
		rt_score = 2 * d["rts"] 
		mentions_score = 3 * d["mentions"] 

		if num == 0:
			edge_weights[user] = padding
		else:
			edge_weights[user] = padding + ((reply_score + like_score + rt_score + mentions_score) / float(num))

		print "weight from", user1, "to", user, "=", edge_weights[user]

	return social, diversity, edge_weights

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


def average_neighbor_weight(user, g):
	
	# how active the user is in general, 
	# which is a factor of how much you're invested in network --> social trust.

	# social = what percentage of your statuses interacts with others in general

	# also, how many different people you engage with.

	# average edgescores (averaging them out over how many neighbors (not how many edges))
	edge_weight = g.edge_properties["edge_weight"]

	weight = 0
	
	num = 0
	for neighbor in user.all_neighbors():
		num += 1

		to_edge = g.edge(user, neighbor)
		from_edge = g.edge(neighbor, user)

		if to_edge is not None:
			weight += edge_weight[to_edge]
		
		if from_edge is not None:
			weight += edge_weight[from_edge]

	if num == 0:
		w = 0
	else:
		w = weight / float(num)

	return w

	#******* because rters have more connections based on how i constructed the graph, 
	# i have to measure node importance / connectedness in a different way.



# clusteredness = how many of your neighbors are connected to each other
# or to what degree are they connected to each other
def clusteredness():
	pass








# centrality = how many nodes do you isolate by leaving
# more sophisticatedly, to what degree do you isolate nodes by leaving
def centrality():
	pass

















