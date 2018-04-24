import scraper
import json, os, twitter, gzip
import graph
import metrics
from graph_tool.all import *
from apps import getAPI
import analysis

# api = getAPI(0)
# statuses = api.GetUserTimeline(screen_name="Trey_VonDinkis",count=10)
# for s in statuses:
# 	print s.id_str, s.text

# statusids = ["979940346649042946"]
statusids = ["988580059928825857"]

for sid in statusids:

	# get the data
	retweet_data = scraper.getfriendsfollowers(sid)

	# rtdata = gzip.open("retweetdata.txt.gz", "r").read()
	# status_data = json.loads(rtdata)
	
	# relations = scraper.specific_relationships(status_data)
	# s_relations = json.loads(gzip.open("specific_relationship_data.txt.gz","r").read())
	# specific_graph = graph.make_graph(status_data, s_relations, "specific")
	# specific_graph.save("specific.xml.gz")

	# specific_graph = load_graph("specific.xml.gz")
	# filled_specific = graph.get_clusteredness(specific_graph)
	# filled_specific.save("specific_edge_weights.xml.gz")

	# g = load_graph("specific_edge_weights.xml.gz")
	# draw_graph(g)
	
	# g_relations = scraper.general_relationships(status_data)
	# g_relations = json.loads(gzip.open("general_relationship_data.txt.gz","r").read())
	# general_graph = graph.make_graph(status_data, g_relations, "general")
	# general_graph.save("general.xml.gz")

	# general_graph = load_graph("general.xml.gz")
	# filled_general = graph.get_activity(general_graph)
	# filled_general.save("general_edge_weights.xml.gz")

	# pr_avg, pr_std, sec_avg, sec_std = analysis.analyze_activity(general_graph)

	# g2 = load_graph("my_graph.xml.gz")



# network_data = scraper.interrelationships(rtjson)