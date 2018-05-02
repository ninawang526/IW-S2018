import scraper
import json, os, twitter, gzip, csv, glob
import graph
import metrics
from graph_tool.all import *
from apps import getAPI
import analysis
import utils

NUM = 25

# STEP 1: HYDRATE TWEETS, IDENTIFY RELEVANT ONES
# realids, fakeids = scraper.get_relevant_statuses()

NEWS = "FAKE"
TYPE = "GENERAL"


statusids = glob.glob("RTER-FILES/"+NEWS+"/*")

# statusids = ["979940346649042946"] # fake news
# statusids = ["988580059928825857"] # NYT
api_count = 5

i = 0
while i < len(statusids) and i < NUM:

	if i == 1:
		break

	sidfolder = statusids[i]
	rterfiles = glob.glob(sidfolder+"/*")

	sid = sidfolder.split("/")[2]
	print "AT STATUS", i, "/", min(NUM,len(statusids)), "STATUS ID =", sid
	
	status_data = scraper.recover_status(sid)
	if status_data is None:
		i+=1
		continue
	status_relations = {}

	
	j = 0
	# FOR EACH RETWEETER
	secs = []
	while j < len(rterfiles) and j < NUM:
	
		if j == 5:
			break
		
		rterfolder = rterfiles[j]
		rter_id = rterfolder.split("/")[3].split(".")[0]
		print "AT RTER", j, "/", min(NUM,len(rterfiles)), "UID =", rter_id

		# load retweeter data
		with gzip.open(rterfolder, "r") as f:
			rter_data = json.loads(f.read())

		# add to status data
		status_data["RTS"][rter_id] = rter_data 
	
		# scrape for general relations 
		relations_data, api_count = scraper.general_relationships(rter_id, rter_data, api_count)
		status_relations.update(relations_data["relations"])
		secs += relations_data["secs"]

		j+=1

	save = True
	
	# write for each status
	if save:
		save_path = "RTER-RESULTS/"+NEWS+"/"
		with gzip.open(os.path.join(save_path, TYPE+"/"+sid+".txt.gz"), 'w') as f:
			f.write(json.dumps({"relations":status_relations, "secs":secs})) # writing for each rter
	else:
		with gzip.open(save_path+TYPE+"/"+sid+".txt.gz", "r") as f:
			rel = json.loads(f.read())
			status_relations = rel["relations"]
			secs = rel["secs"]

	# make graph
	g = graph.make_graph(status_data, status_relations, TYPE.lower(), secs=secs)
	g.save("general_relationships.xml.gz")
	graph.pretty_graphing(g)

	# graph operations
	









	# s_relations = json.loads(gzip.open("specific_relationship_data.txt.gz","r").read())
	# specific_graph = graph.make_graph(status_data, s_relations, "specific")
	# specific_graph.save("specific.xml.gz")

	# specific_graph = load_graph("specific.xml.gz")
	# filled_specific = graph.get_centrality(specific_graph)
	# filled_specific.save("specific_edge_weights-CENTRAL.xml.gz")

	# g = load_graph("specific_edge_weights-CENTRAL.xml.gz")

	# node_social_score = g.vertex_properties["node_social_score"]
	# node_diversity_score = g.vertex_properties["node_diversity_score"]
	# node_neighbors_score = g.vertex_properties["node_neighbors_score"]
	# node_weight = g.vertex_properties["node_weight"]
	# edge_weight = g.edge_properties["edge_weight"]

	# graph.pretty_graphing(g, edge_weight, 1, node_neighbors_score)

	# utils.prettytable_centrality(g)



	# analysis.analyze_activity(g)
	

	i += 1



# network_data = scraper.interrelationships(rtjson)