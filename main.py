import scraper
import json, os, twitter, gzip, csv
# import graph
import metrics
# from graph_tool.all import *
from apps import getAPI
# import analysis
import utils


# STEP 1: HYDRATE TWEETS, IDENTIFY RELEVANT ONES
# realids, fakeids = scraper.get_relevant_statuses()


with open("realids-clean.txt", "r") as f:
	statuses = json.loads(f.read())
	statusids = statuses.keys()

# 
# statusids = ["979940346649042946"] # fake news
# statusids = ["988580059928825857"] # NYT

i = 0
while i < len(statusids):

	sid = statusids[i]

	print "~~~~~ WORKING ON STATUS", i, "~~~~~"

	# # get the data
	retweet_data = scraper.getfriendsfollowers(sid)

	# rtdata = gzip.open("retweetdata.txt.gz", "r").read()
	# status_data = json.loads(rtdata)
	
	# # relations = scraper.specific_relationships(status_data)
	# s_relations = json.loads(gzip.open("specific_relationship_data.txt.gz","r").read())
	# # specific_graph = graph.make_graph(status_data, s_relations, "specific")
	# # specific_graph.save("specific.xml.gz")

	# specific_graph = load_graph("specific.xml.gz")
	# filled_specific = graph.get_activity(specific_graph)
	# # filled_specific.save("specific_edge_weights-ACTIVITY.xml.gz")

	# g = load_graph("specific_edge_weights-ACTIVITY.xml.gz")
	# graph.draw_graph(g)



	# analysis.analyze_activity(g)
	

	i += 1



# network_data = scraper.interrelationships(rtjson)