import scraper
import json, os, twitter, gzip
from graph import make_graph, fill_edges
from graph_tool.all import *
from apps import getAPI

# api = getAPI(0)
# statuses = api.GetUserTimeline(screen_name="Trey_VonDinkis",count=10)
# for s in statuses:
# 	print s.id_str, s.text

statusids = ["979940346649042946"]

for sid in statusids:

	# get the data
	# retweet_data = scraper.getfriendsfollowers(sid)

	# rtdata = gzip.open("retweetdata.txt.gz", "r").read()
	# status_data = json.loads(rtdata)
	
	# relations = scraper.specific_relationships(status_data)
	# s_relations = json.loads(gzip.open("specific_relationship_data.txt.gz","r").read())
	# specific_graph = make_graph(status_data, s_relations)
	# specific_graph.save("specific.xml.gz")

	# specific_graph = load_graph("specific.xml.gz")
	# filled_specific = fill_edges(specific_graph)


	# relations = scraper.general_relationships(status_data)
	# g_relations = json.loads(gzip.open("general_relationship_data.txt.gz","r").read())
	# general_graph = make_graph(status_data, s_relations, gen=g_relations)
	# general_graph.save("general.xml.gz")

	# g2 = load_graph("my_graph.xml.gz")


# network_data = scraper.interrelationships(rtjson)