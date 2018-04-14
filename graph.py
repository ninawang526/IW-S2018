from graph_tool.all import *
import json
import random

# 0 = no relationship
# 1 = ui following uj
# 2 = uj following ui
# 3 = mutual
def graph_network(status, rel):

	# An empty graph can be created by instantiating a Graph class:
	g = Graph()

	rts = status["RTS"]
	likes = status["LIKES"]
	author = str(status["AUTHOR"])

	# g.vertex_properties["color"] = g.new_vertex_property("string")
	color = g.new_vertex_property("string")
	label = g.new_vertex_property("string")

	# adding root
	root = g.add_vertex()
	color[root]="black"
	label[root]=author
	
	users = {author:root}

	# one vertex for every user who retweets
	# points = following
	for uid in rts.keys():
		if uid not in users:
			node = g.add_vertex()
			color[node] = "red"
			label[node] = uid
			users[uid] = node

	# # one vertex for everyone else in the network
	for uid in rel.keys():
		if uid not in users:
			node = g.add_vertex()
			if uid in likes:
				color[node]="pink"
			else:
				color[node] = "white"
			label[node] = uid
			users[uid] = node

	# adding relationship edges
	for i in rel.keys():
		for j in rel[i].keys():

			node_i = users[i]

			if j not in users:
				node_j = g.add_vertex()
				color[node_j] = "white"
				label[node_j] = j
				users[j] = node_j # IN THE FUTURE, PASS THROUGH SET OF ALL NODES INSTEAD
			else:
				node_j = users[j]

			try:
				val = rel[i][j]
			except:
				continue

			if val == 1:
				e = g.add_edge(node_i, node_j)
			elif val == 2:
				e = g.add_edge(node_j, node_i)
			elif val == 3:
				e1 = g.add_edge(node_i, node_j)
				e2 = g.add_edge(node_j, node_i)


	# pos = sfdp_lxayout(g)
	# pos = arf_layout(g, max_iter=0)
	# pos = fruchterman_reingold_layout(g, n_iter=1000)
	pos = radial_tree_layout(g, root)
	graph_draw(g, vertex_fill_color=color, vertex_color=color, vertex_text=label, 
				vertex_text_position = 0, vertex_size=30,
				edge_color="gray", 
				pos=pos,
				output_size=(700, 700), output="two-nodes.png")


# status_data = [json.loads(open("sampledata.txt","r").read())]
# rel_data = json.loads(open("relationship_data.txt", "r").read())

# for status in status_data:

# 	status_id = status["TWEET_ID"]
# 	rel = rel_data[str(status_id)]

# 	graph(status, rel)







	