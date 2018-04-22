import scraper
import json, os, twitter
from graph import make_graph
from apps import getAPI

# api = getAPI(0)
# statuses = api.GetUserTimeline(screen_name="Trey_VonDinkis",count=10)
# for s in statuses:
# 	print s.id_str, s.text

statusids = ["987822889817772032"]

for sid in statusids:

	# get the data
	retweet_data = scraper.getfriendsfollowers(sid)


# rtdata = open("sampledata.txt", "r").read()
# retweet_data = json.loads(rtdata)

# for s_id in retweet_data:
# 	status_network = retweet_data[s_id]
	
# 	# relations = scraper.specific_relationships(status_network)
# 	s_relations = json.loads(open("specific_relationship_data.txt","r").read())
# 	specific_graph = make_graph(status_network, s_relations)
# 	specific_graph.save("specific.xml.gz")

	# g_relations = json.loads(open("general_relationship_data.txt","r").read())
	# general_graph = make_graph(status_network, relations, general=g_relations)
	# specific_graph.save("general.xml.gz")


# network_data = scraper.interrelationships(rtjson)