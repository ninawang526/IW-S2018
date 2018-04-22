from graph_tool.all import *
import json
import random
import metrics

# 0 = no relationship
# 1 = ui following uj
# 2 = uj following ui
# 3 = mutual
def add_edge(g, node_i, node_j, val):
	if val == 1:
		e = g.edge(node_i, node_j, add_missing=True)
	elif val == 2:
		e = g.edge(node_j, node_i, add_missing=True)
	elif val == 3:
		e1 = g.edge(node_i, node_j, add_missing=True)
		e2 = g.edge(node_j, node_i, add_missing=True)



def user_to_node(i, users, g, color, c, label=None, l=None):
	if i not in users:
		node = g.add_vertex()
		color[node] = c
		if label is not None and l is not None:
			label[node] = l
		users[i] = node
	else:
		node = users[i]

	return node



def make_graph(status, rel, gen=None):
	g = Graph()

	rts = status["RTS"]
	likes = status["LIKES"]
	author = str(status["AUTHOR"])

	# g.vertex_properties["color"] = g.new_vertex_property("string")
	color = g.new_vertex_property("string")
	label = g.new_vertex_property("string")
	uid = g.new_vertex_property("string")

	g.vertex_properties["color"] = color
	g.vertex_properties["label"] = label
	g.vertex_properties["uid"] = uid

	# adding root
	users = {}
	root = user_to_node(author, users, g, color, "black", label, author)

	# one vertex for every user who retweets
	# points = following
	for i in rts.keys():
		node = user_to_node(i, users, g, color, "red", label, i)
		
		for exposed in rts[i]["FOLLOWERS"]["ids"].keys():
			c = "white"
			if str(i) in likes:
				c = "pink"
			node = user_to_node(exposed, users, g, color, c)
			uid[node] = i


	# adding relationship edges
	for i in rel.keys():
		for j in rel[i].keys():

			node_i = user_to_node(i, users, g, color, "white")
			node_j = user_to_node(j, users, g, color, "white")
			uid[node_i] = i
			uid[node_j] = j
 
			try:
				val = rel[i][j]
			except:
				continue

			add_edge(g, node_i, node_j, val)

			
	if gen is not None:
		for i in gen.keys():
			for j in gen[i].keys():

				node_i = user_to_node(i, users, g, color, "gray")
				node_j = user_to_node(j, users, g, color, "gray")
				uid[node_i] = i
				uid[node_j] = j
	 
				try:
					val = gen[i][j]
				except:
					continue

				add_edge(g, node_i, node_j, val)


	# pos = sfdp_layout(g)
	pos = arf_layout(g, max_iter=0)
	# pos = fruchterman_reingold_layout(g, n_iter=1000)
	# pos = radial_tree_layout(g, root)

	graph_draw(g, vertex_fill_color=color, vertex_color=color, vertex_text=label, 
				vertex_text_position = 0, vertex_size=10,
				edge_color="gray", 
				pos=pos,
				output_size=(700, 700), output="two-nodes.png")

	return g


def fill_edges(g):
	uid = g.vertex_properties["uid"]

	for v in g.vertices():
		s = uid[v]
		targets = [int(uid[t]) for t in v.out_neighbors()]

		weights = metrics.edge_weight(s, targets)

		print "weight from", s, "to", t, "=", weights

		#print vprop[vertex].title

	# g.edge(node_j, node_i, add_missing=True)




def fill_graph(g):
	fill_edges(g)

# 	for v in g.vertices():
#     print(v)
# for e in g.edges():
#     print(e)





	