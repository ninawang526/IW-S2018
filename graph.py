from graph_tool.all import *
import json
import random
import metrics

# 0 = no relationship
# 1 = ui following uj
# 2 = uj following ui
# 3 = mutual

BLACK = [0,0,0,1]
WHITE = [1,1,1,1]
GRAY = [0.709, 0.709, 0.709, 1]

RED = [0.796, 0.062, 0.227, 1]
PINK = [0.952, 0.588, 0.623, 1]



def new_vprop(name, t, g):
	prop = g.new_vertex_property(t)
	g.vertex_properties[name] = prop
	return prop


def new_eprop(name, t, g):
	prop = g.new_edge_property(t)
	g.edge_properties[name] = prop
	return prop


def is_relevant_node(v, g):
	category = g.vertex_properties["category"]
	return (category[v] == "source" or category[v] == "primary" or category[v] == "secondary")


def draw_graph(g):
	# vertex properties
	color = g.vertex_properties["color"]
	uid = g.vertex_properties["uid"]
	node_pen_weight = g.vertex_properties["node_pen_weight"]

	# edge properties
	edge_pen_weight = g.edge_properties["edge_pen_weight"]
	edge_weight = g.edge_properties["edge_weight"]

	# pos = arf_layout(g, max_iter=0)

	graph_draw(g, vertex_fill_color=color, vertex_color=color, #vertex_text=uid, 
			vertex_text_position = 0, vertex_size=node_pen_weight,
			edge_color="gray", edge_pen_width=edge_pen_weight,
			# pos=pos,
			output_size=(700, 700), output="two-nodes.png")


def pretty_graphing(g, edge_w=None, edge_w_pad=0, node_w=None, node_w_pad=0, edge_c="gray"):
	color = g.vertex_properties["color"]

	# edge_color = g.edge_properties["edge_color"]
	edge_pen_weight = g.edge_properties["edge_pen_weight"]
	node_pen_weight = g.vertex_properties["node_pen_weight"]

	for e in g.edges():
		# edge_color[e] = edge_c

		if edge_w is not None:
			edge_pen_weight[e] = (5*(edge_w[e]-edge_w_pad)) + 1 #SCALING BY 2!! -- DRAWING OUT DIFFS
		else:
			edge_pen_weight[e] = 1

	for v in g.vertices():
		if node_w is not None:
			node_pen_weight[v] = (15*(node_w[v]-node_w_pad)) + 10 
		else:
			node_pen_weight[v] = 10
		print node_pen_weight[v]

	draw_graph(g)


def add_edge(g, node_i, node_j, val):
	if val == 1:
		e = g.edge(node_i, node_j, add_missing=True)
	elif val == 2:
		e = g.edge(node_j, node_i, add_missing=True)
	elif val == 3:
		e1 = g.edge(node_i, node_j, add_missing=True)
		e2 = g.edge(node_j, node_i, add_missing=True)


def user_to_node(i, cat, users, g, col, l="", t=""):
	uid = g.vertex_properties["uid"]
	color = g.vertex_properties["color"]
	label = g.vertex_properties["label"]
	category = g.vertex_properties["category"]
	time = g.vertex_properties["time"]

	if i in users:
		node = users[i]
	
	# make new node
	else:

		node = g.add_vertex()

		uid[node] = i
		color[node] = col
		label[node] = l
		category[node] = cat
		time[node] = t
		
		users[i] = node

	return node


def initialize_props(g):
	# INITIAL
	color = new_vprop("color", "vector<float>", g)
	label = new_vprop("label", "string", g)
	uid = new_vprop("uid", "string", g)
	category = new_vprop("category", "string", g)
	time = new_vprop("time", "string", g)	

	# ACTIVITY
	# what % of the statuses are interactive ones 
	node_social_score = new_vprop("node_social_score", "float", g)
	# how many different people the user interacts with
	node_diversity_score = new_vprop("node_diversity_score", "float", g)
	# average neighbor score
	node_neighbors_score = new_vprop("node_neighbors_score", "float", g)
	# total node weight
	node_weight = new_vprop("node_weight", "float", g)
	node_pen_weight = new_vprop("node_pen_weight", "float", g)
	# EDGE PROPERTIES
	edge_weight = new_eprop("edge_weight", "float", g)
	edge_pen_weight = new_eprop("edge_pen_weight", "float", g)
	# edge_color = new_eprop("edge_color", "string", g)


	# CLUSTEREDNESS
	clusteredness = new_vprop("clusteredness", "float", g)

	# CONNECTIVITY
	centrality = new_vprop("centrality", "float", g)


def make_graph(status, rel, t, secs=None):
	g = Graph()
	initialize_props(g)

	rts = status["RTS"]
	likes = status["LIKES"]
	author = str(status["AUTHOR"])

	# graph properties
	color = g.vertex_properties["color"]
	label = g.vertex_properties["label"]
	uid = g.vertex_properties["uid"]
	category = g.vertex_properties["category"]
	time = g.vertex_properties["time"]

	# edge_color = g.edge_properties["edge_color"]


	# adding root
	users = {}
	root = user_to_node(author, "source", users, g, BLACK, t=status["TIME"])


	# one vertex for every user who retweets
	for i in rts:
		node = user_to_node(i, "primary", users, g, RED, t=rts[i]["RT_AT"])
		
		for exposed in secs:
			c = PINK
			if str(i) in likes:
				c = WHITE
			node = user_to_node(exposed, "secondary", users, g, c)


	# adding relationship edges
	if t == "specific":
		for i in rel.keys():
			for j in rel[i].keys():

				node_i = user_to_node(i, "tertiary", users, g, GRAY)
				node_j = user_to_node(j, "tertiary", users, g, GRAY)

				try:
					val = rel[i][j]
				except:
					continue

				add_edge(g, node_i, node_j, val)

	if t == "general":
		for i in rel.keys():
			for j in rel[i].keys():

				node_i = user_to_node(i, "tertiary", users, g, GRAY)
				node_j = user_to_node(j, "tertiary", users, g, GRAY)
	 
				try:
					val = rel[i][j]
				except:
					continue

				add_edge(g, node_i, node_j, val)

	# pos = sfdp_layout(g)
	# pos = arf_layout(g, max_iter=0)
	# pos = fruchterman_reingold_layout(g, n_iter=1000)
	# pos = radial_tree_layout(g, root)

	# graph_draw(g, vertex_fill_color=color, vertex_color=color, vertex_text=label, 
	# 			vertex_text_position = 0, vertex_size=10,
	# 			edge_color="gray", 
	# 			pos=pos,
	# 			output_size=(700, 700), output="two-nodes.png")
	# pretty_graphing(g)

	return g


def in_and_out(v):
	neighbors = []

	for n_out in v.out_neighbors():
		neighbors.append(n_out)
	
	for n_in in v.in_neighbors():
		neighbors.append(n_in)

	return neighbors


def get_activity(g):
	# VERTEX PROPERTIES
	uid = g.vertex_properties["uid"]
	category = g.vertex_properties["category"]

	node_social_score = g.vertex_properties["node_social_score"]
	node_diversity_score = g.vertex_properties["node_diversity_score"]
	node_neighbors_score = g.vertex_properties["node_neighbors_score"]
	node_weight = g.vertex_properties["node_weight"]

	# EDGE PROPERTIES
	edge_weight = g.edge_properties["edge_weight"]

	users = {}

	# examine the timeline of each user, 
	for v in g.vertices():
		s = uid[v]

		# ONLY CALCULATE THIS FOR RELEVANT NODES.
		if is_relevant_node(v, g):

			targets = []
			for t in v.out_neighbors():
				t_int = int(uid[t])
				targets.append(t_int)
				users[t_int] = t # int

			node_social, node_diversity, weights = metrics.edge_weight(s, targets)

			# fill in edge weights
			for t_id_int in weights:
				t = users[t_id_int]
				edge = g.edge(v, t) 
				edge_weight[edge] = weights[t_id_int] 

			node_social_score[v] = node_social 
			node_diversity_score[v] = node_diversity

		else:
			node_social_score[v] = 0
			node_diversity_score[v] = 0

	
	# once found all edge weights, get average neighbor weight for each node
	for v in g.vertices():
		if is_relevant_node(v, g):
			
			node_neighbors_score[v] = metrics.average_neighbor_weight(v, g)
			# print uid[v], "soc", node_social_score[v], "div", node_diversity_score[v], "neigh", node_neighbors_score[v]

		else:
			node_neighbors_score[v] = 0


	# normalizing 
	edge_weight = metrics.normalize_weights(edge_weight, g.edges(), 1)
	
	node_social_score = metrics.normalize_weights(node_social_score, g.vertices())	
	node_diversity_score = metrics.normalize_weights(node_diversity_score, g.vertices())
	node_neighbors_score = metrics.normalize_weights(node_neighbors_score, g.vertices())

	for v in g.vertices():
		soc = node_social_score[v]
		div = node_diversity_score[v]
		neigh = node_neighbors_score[v]

		node_weight[v] = soc + div + neigh	

	node_weight = metrics.normalize_weights(node_weight, g.vertices())


	# pretty graphing
	pretty_graphing(g, edge_weight, 1, node_weight, edge_c="gray")

	return g 


def get_clusteredness(g):
	uid = g.vertex_properties["uid"]
	category = g.vertex_properties["category"]
	clusteredness = g.vertex_properties["clusteredness"]

	print g.vertex_properties.keys()
	print g.edge_properties.keys()


	for v in g.vertices():

		possible = 0
		actual = 0

		if is_relevant_node(v, g):
			# ignore their relation to v
			# discriminate between one-way and two-way edges.

			neighbors = in_and_out(v)

			for source in neighbors:
				for dest in neighbors:

					if source != dest:
						possible += 1
						if g.edge(source, dest) is not None:
							actual += 1

		
		if possible == 0:
			cluster = 0
		else:
			cluster = actual / float(possible)

		clusteredness[v] = cluster

		print uid[v], "possible", possible, "actual", actual, "cluster score =", cluster


	clusteredness = metrics.normalize_weights(clusteredness, g.vertices())

	pretty_graphing(g, edge_w=None, node_w=clusteredness)

	return g



# make sure that it's not skewed toward rters, who are guaranteed to have 5
# basically, are your followers also connected to others in the network. ***
# for secondaries with no followers: drop out of calculation.
def get_centrality(g):
	uid = g.vertex_properties["uid"]
	centrality = g.vertex_properties["centrality"]
	category = g.vertex_properties["category"]

	for v in g.vertices():
		
		total = 0
		bridge = 0

		if is_relevant_node(v, g):
			# ignore their relation to v
			# discriminate between one-way and two-way edges.

			neighbors = in_and_out(v)

			for s in neighbors:
				for t in neighbors:
					if s != t:
						paths = all_shortest_paths(g, s, t)

						for path in paths:
							total +=1 
							if v in path:
								bridge += 1

		if total == 0:
			centrality_score = 0
		else:
			centrality_score = float(bridge) / total

		centrality[v] = centrality_score
		

		print uid[v]
		print "bridge:", bridge, "total:", total, "score:", centrality_score


	centrality = metrics.normalize_weights(centrality, g.vertices())

	pretty_graphing(g, edge_w=None, node_w=centrality)

	return g





def fill_graph(g):

	get_activity(g)
	get_connectivity(g)










	