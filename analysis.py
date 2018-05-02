import numpy as np
from graph import RED, BLACK, GRAY, PINK
from prettytable import PrettyTable


# in specific network, is there a distinct difference between "social trust" between exposed, retweeted?
def analyze_metric(g, metric):
	# node 
	category = g.vertex_properties["category"]
	node_weight = g.vertex_properties[metric]

	primary = []
	secondary = []

	for v in g.vertices():
		weight = node_weight[v]

		#CHANGE LATER !!!
		if category[v] == "primary":
			primary.append(weight)

		elif category[v] == "secondary":
			secondary.append(weight)

	pr_avg, pr_std = np.mean(np.array(primary)), np.std(np.array(primary))
	sec_avg, sec_std = np.mean(np.array(secondary)), np.std(np.array(secondary))

	# print "primary:", "average =", pr_avg, "std =", pr_std
	# print "secondary:", "average =", sec_avg, "std =", sec_std

	return pr_avg, pr_std, sec_avg, sec_std


def analyze(g):

	pt = PrettyTable()
	pt.field_names = ["metric", "node", "average", "std"]
	

	pr_avg, pr_std, sec_avg, sec_std = analyze_metric(g, "node_weight")
	pt.add_row(["ACTIVITY SCORE", "primary", pr_avg, pr_std])
	pt.add_row(["", "secondary", sec_avg, sec_std])

	pt.add_row(["", "", "", ""])

	pr_avg, pr_std, sec_avg, sec_std = analyze_metric(g, "node_social_score")
	pt.add_row(["SOCIAL SCORE", "primary", pr_avg, pr_std])
	pt.add_row(["", "secondary", sec_avg, sec_std])

	pt.add_row(["", "", "", ""])

	pr_avg, pr_std, sec_avg, sec_std = analyze_metric(g, "node_diversity_score")
	pt.add_row(["DIVERSITY SCORE", "primary", pr_avg, pr_std])
	pt.add_row(["", "secondary", sec_avg, sec_std])

	pt.add_row(["", "", "", ""])

	pr_avg, pr_std, sec_avg, sec_std = analyze_metric(g, "node_neighbors_score")
	pt.add_row(["NEIGHBORS SCORE", "primary", pr_avg, pr_std])
	pt.add_row(["", "secondary", sec_avg, sec_std])





	print(pt)






