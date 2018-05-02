import twitter
import time, csv
from apps import lenapis, getAPI
from prettytable import PrettyTable


real_news = ["nyti.ms", "washingtonpost", "thehill", "huff.to", "cnn",
			"thenation.com", "n.pr", "nationalreview", "wsj", "bbc", "economist",
			"politico.com", "foxnews", "reut.rs", "fxn.ws"]

def fake_news():
	fake_news_sites = []
	with open('fake_news_sites.csv', 'rb') as f:
	    reader = csv.reader(f)
	    data = list(reader)
	    for line in data:
	    	name = line[0].split(".")[0].lower()
	    	if line[1] == "Fake news" or line[1]=="Some fake stories":
	    		fake_news_sites.append(name)
	return fake_news_sites


def is_fake(url):
	for fake_url in fake_news():
		if fake_url in url:
			print "FAKE", fake_url, url
			return True

	return False


def is_real(url, count):
	for real_url in real_news:
		if real_url in url:
			
			# keep track of what websites we've seen
			if real_url in count:
				
				if count[real_url] < 10:
					count[real_url] += 1
					print "REAL", url, count[real_url]
					return True

			else:
				count[real_url] = 1
				print "REAL", url, count[real_url]
				return True

	print url
	return False


def rate_limit(api, apc, app_only=False):
	rl = api.CheckRateLimit("/friends/ids.json")
	print "current time:", time.strftime("%H:%M:%S", time.gmtime()) 
	print "api", apc % lenapis, "will resume at", time.strftime("%H:%M:%S", time.gmtime(rl[2])), "\n"

	# time.sleep(10)

	new_api = getAPI(apc, app_only=app_only) 
	new_api.InitializeRateLimit()

	return new_api


# error handling		
def continue_user(e):
	print e
	try:
		if e[0][0]["code"] == 88 or e[0][0]["code"] == 32: 
			return False
		else:
			return True
	except:
		return True


def prettytable_activity(g):
	pt = PrettyTable()
	pt.field_names = ["uid", "type", "social", "diversity", "neighbors", "total"]

	uid = g.vertex_properties["uid"]
	category = g.vertex_properties["category"]

	node_social_score = g.vertex_properties["node_social_score"]
	node_diversity_score = g.vertex_properties["node_diversity_score"]
	node_neighbors_score = g.vertex_properties["node_neighbors_score"]
	node_weight = g.vertex_properties["node_weight"]
	edge_weight = g.edge_properties["edge_weight"]
	

	for v in g.vertices():
		if category[v] == "source" or category[v] == "primary":
			pt.add_row([uid[v], category[v], node_social_score[v], node_diversity_score[v], 
						node_neighbors_score[v], node_weight[v]])

	for v in g.vertices():
		if category[v] == "secondary":
			pt.add_row([uid[v], category[v], node_social_score[v], node_diversity_score[v], 
						node_neighbors_score[v], node_weight[v]])

	print(pt)


def prettytable_clusteredness(g):
	pt = PrettyTable()
	pt.field_names = ["uid", "type", "clusteredness"]

	uid = g.vertex_properties["uid"]
	category = g.vertex_properties["category"]

	clusteredness = g.vertex_properties["clusteredness"]
	
	for v in g.vertices():
		if category[v] == "source" or category[v] == "primary":
			pt.add_row([uid[v], category[v], clusteredness[v]])

	for v in g.vertices():
		if category[v] == "secondary":
			pt.add_row([uid[v], category[v], clusteredness[v]])


	print(pt)


def prettytable_centrality(g):
	pt = PrettyTable()
	pt.field_names = ["uid", "type", "centrality"]

	uid = g.vertex_properties["uid"]
	category = g.vertex_properties["category"]

	centrality = g.vertex_properties["centrality"]
	

	for v in g.vertices():
		if category[v] == "source" or category[v] == "primary":
			pt.add_row([uid[v], category[v], centrality[v]])

	for v in g.vertices():
		if category[v] == "secondary":
			pt.add_row([uid[v], category[v], centrality[v]])


	print(pt)









