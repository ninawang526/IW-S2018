from apps import getAPI

api_count = 1
api = getAPI(api_count)


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


# returns dictionary of u1-u2 relationship
def edge_weight(user1, user2, mutual):
	# get timeline of user -- returns 3200 of user's most recent tweets
	t1 = api.GetUserTimeline(user1)
	# t2 = api.GetUserTimeline(user2)

	# mutual = Boolean, others are lists
	weight = {"mutual": mutual, "replies": 0, "likes": 0, "rts": 0, "mentions": 0, "timestamps":[]}

	for s1 in t1:
		date = s1.created_at
		in_reply_to = s1.in_reply_to_user_id

		# user mentions
		mentions = s1.user_mentions
		if len(mentions) > 0:
			for m in mentions:
				if m.id == u2.id:
					weight["mentions"] += 1
					timestamps.add(date)

		# in reply to
		if in_reply_to is not None:
			if in_reply_to == user2.id:
				weight["replies"] += 1
				timestamps.add(date)

		# did u1 retweet from u2?
		rt = retweeted_status
		if rt is not None:
			if rt.source.user.id == user2.id:
				weight["rts"] += 1
				timestamps.add(date)
		
		# did u2 like things from u1?
		likes = get_user_ids_of_post_likes(s1.id)
		if u2.id in likes:
			weight["likes"] += 1
			timestamps.add(date)


	return weight
		

		# if interactions are spaced out over time, or in one rapid burst
		# should regularity matter..? i don't think so. i think just
		# span of time should matter. density? should that matter?
		# maybe yes it should matter only in the positive direction.

		# how to determine edgeweight of 2 directional (double it?)
		# because mutuality definitely strengthens edgeweight, even if
		# rt/like behavior doesn't capture that. 
		# to make sure don't repeat, just calculate for outgoing edges
		# wait..repeats are ok. just add to that score.
		# just don't add the mutual constant twice. -- just add for smaller id.


def node_weight(user):
	
	# how active the user is

	# botscore

	pass



