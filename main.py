import scraper
import json
import graph



retweet_data = scraper.getfriendsfollowers()


# rtdata = open("sampledata.txt", "r").read()
# retweet_data = json.loads(rtdata)

# for s_id in retweet_data:
# 	status_network = retweet_data[s_id]
	
# 	# relations = scraper.specific_relationships(status_network)
# 	relations = json.loads(open("relationship_data.txt","r").read())

# 	graph.graph_network(status_network, relations)


# network_data = scraper.interrelationships(rtjson)