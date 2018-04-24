import numpy as np
from graph import RED, BLACK, GRAY, PINK

# in specific network, is there a distinct difference between "social trust" between exposed, retweeted?
def analyze_activity(g):
	# node 
	color = g.vertex_properties["color"]
	node_weight = g.vertex_properties["node_weight"]
	# category = g.vertex_properties["category"]

	primary = []
	secondary = []

	for v in g.vertices():
		weight = node_weight[v]

		#CHANGE LATER !!!
		if color[v] == RED:
			primary.append(weight)

		elif category[v] == PINK:
			secondary.append(weight)

	pr_avg, pr_std = np.mean(np.array(primary)), np.std(np.array(primary))
	sec_avg, sec_std = np.mean(np.array(secondary)), np.std(np.array(secondary))

	print "primary:", "average =", pr_avg, "std =", pr_std
	print "secondary:", "average =", sec_avg, "std =", sec_std

	return pr_avg, pr_std, sec_avg, sec_std

