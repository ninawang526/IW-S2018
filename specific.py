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
TYPE = "SPECIFIC"
ACTIVE = False


statusids = glob.glob("RTER-FILES/"+NEWS+"/*")

ignore_files = glob.glob("RTER-RESULTS/"+NEWS+"/"+TYPE+"/*")
ignore = [x.split("/")[3].split(".")[0] for x in ignore_files]

# statusids = ["979940346649042946"] # fake news
# statusids = ["988580059928825857"] # NYT
api_count = 5

i = 0
while i < len(statusids):

	if i == 1:
		break

	sidfolder = statusids[i]
	rterfiles = glob.glob(sidfolder+"/*")

	sid = sidfolder.split("/")[2]
	
	# if sid in ignore:
 #        print "IGNORED", sid
 #        i+=1
 #        continue

	print "AT STATUS", i, "/", len(statusids), "STATUS ID =", sid
	
	status_data = scraper.recover_status(sid)
	if status_data is None:
		i+=1
		continue


	j = 0
	# FOR EACH RETWEETER
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

		j+=1

	# scrape for specific relations 
	save_path = "RTER-RESULTS/"+NEWS+"/"

	if ACTIVE:
		rel, api_count = scraper.specific_relationships(status_data, api_count)
		with gzip.open(os.path.join(save_path, TYPE+"/"+sid+".txt.gz"), 'w') as f:
			f.write(json.dumps(rel)) # writing for each rter
	else:
		with gzip.open(save_path+TYPE+"/"+sid+".txt.gz", "r") as f:
			rel = json.loads(f.read())
	
	status_relations = rel["relations"]
	secs = rel["secs"]

	# make graph
	name = "specific_relationships.xml.gz"
	if True:
		g = graph.make_graph(status_data, status_relations, TYPE.lower(), secs)
		g.save(name)
	else:
		g = load_graph(name)
	

	# # graph operations - ACTIVITY
	# name = "general_edge_weights-ACTIVITY.xml.gz"
	# if ACTIVE:
	# 	filled_active = graph.get_activity(g)
	# 	filled_active.save("general_edge_weights-ACTIVITY.xml.gz")
	# else:
	# 	filled_active = load_graph(name)

	# # utils.prettytable_activity(filled_active)

	# # graph operations - CLUSTEREDNESS
	# name = "general_edge_weights-CLUSTER.xml.gz"
	# if ACTIVE:
	# 	filled_cluster = graph.get_clusteredness(g)
	# 	filled_cluster.save("general_edge_weights-CLUSTER.xml.gz")
	# else:
	# 	filled_cluster = load_graph(name)

	# # utils.prettytable_clusteredness(filled_cluster)


	# # graph operations - CENTRALITY
	# name = "general_edge_weights-CENTRAL.xml.gz"
	# if ACTIVE:
	# 	filled_central = graph.get_centrality(g)
	# 	filled_central.save("general_edge_weights-CENTRAL.xml.gz")
	# else:
	# 	filled_central= load_graph(name)

	# # utils.prettytable_centrality(filled_central)

	# analysis.analyze(filled_active)

	







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