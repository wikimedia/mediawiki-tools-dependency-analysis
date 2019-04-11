# This file is part of Project Ruprecht, see COPYING for license terms.
# Copied and modified from remove_cycle-Ednges_by_hierarchy.py by zhenv5.
# See contrib/breaking_cycles_in_noisy_hierarchies for the original and the license.

import sys
import os

scriptDir = os.path.dirname( os.path.realpath(__file__) )
sys.path.append( scriptDir + "/../contrib/breaking_cycles_in_noisy_hierarchies" )

import re
import networkx as nx
from remove_cycle_edges_by_hierarchy_greedy import scc_based_to_remove_cycle_edges_iterately
from remove_cycle_edges_by_hierarchy_BF import remove_cycle_edges_BF_iterately
from remove_cycle_edges_by_hierarchy_voting import remove_cycle_edges_heuristic
from measures import F1
from file_io import write_dict_to_file
from file_io import read_dict_from_file
from file_io import write_pairs_to_file

def parseRow( line ):
	return re.split( '[\s,;]+', line.strip(), 2 )

def loadEdges( inFile, tr = None ):
	f = open( inFile, 'r' )
	
	tr = {} if tr is None else tr
	edges = []
	c = 1
	for line in f:
		(key, value) = parseRow( line )
		
		if key in tr:
			n = tr[key]
		else:
			n = c
			c += 1
			tr[key] = n
			
		if value in tr:
			m = tr[value]
		else:
			m = c
			c += 1
			tr[value] = m
			
		edges.append( ( n, m ) )
		
	f.close()
	
	# flip tr before returning it, so it represents the mapping needed to
	# undo the translation.
	inv_tr = {v: k for k, v in tr.iteritems()}
	return edges, inv_tr

def writeEdges( outFile, edges, tr = None ):
	f = open( outFile, 'w' )
	
	for e in edges:
		( k, v ) = e
		
		if tr is not None:
			k = tr[k]
			v = tr[v]
				
		f.write( "%s\t%s\n" % ( k, v ) )
		
	f.close()
	
def get_edges_voting_scores(set_edges_list):
	total_edges = set()
	for edges in set_edges_list:
		total_edges = total_edges | edges
	edges_score = {}
	for e in total_edges:
		edges_score[e] = len(filter(lambda x: e in x, set_edges_list))
	return edges_score

def remove_cycle_edges_strategies( graph_file, nodes_score_dict, score_name = "socialagony", nodetype = int ):
	g = nx.read_edgelist(graph_file,create_using = nx.DiGraph(),nodetype = nodetype)
	# greedy
	e1 = scc_based_to_remove_cycle_edges_iterately(g,nodes_score_dict)
	g = nx.read_edgelist(graph_file,create_using = nx.DiGraph(),nodetype = nodetype)
	# forward
	e2 = remove_cycle_edges_BF_iterately(g,nodes_score_dict,is_Forward = True,score_name = score_name)
	# backward
	g = nx.read_edgelist(graph_file,create_using = nx.DiGraph(),nodetype = nodetype)
	e3 = remove_cycle_edges_BF_iterately(g,nodes_score_dict,is_Forward = False,score_name = score_name)
	return e1,e2,e3

def remove_cycle_edges_by_voting(graph_file,set_edges_list,nodetype = int):
	edges_score = get_edges_voting_scores(set_edges_list)
	e = remove_cycle_edges_heuristic(graph_file,edges_score,nodetype = nodetype)
	return e 

def remove_cycle_edges_by_hierarchy(graph_file,nodes_score_dict,score_name = "socialagony",nodetype = int, recycle = False):
	e1,e2,e3 = remove_cycle_edges_strategies(graph_file,nodes_score_dict,score_name = score_name,nodetype = nodetype)
	e4 = remove_cycle_edges_by_voting(graph_file,[set(e1),set(e2),set(e3)],nodetype = nodetype)
	return e1,e2,e3,e4

def compute_hierarchy( graph_file, tmp_prefix, players_score_func_name, nodetype = int, recycle = False ):
	import os.path
	if players_score_func_name == "socialagony":
		from helper_funs import dir_tail_name
		dir_name,tail = dir_tail_name(graph_file)
		agony_file = tmp_prefix + ".socialagony.tmp"
		#agony_file = graph_file[:len(graph_file)-6] + "_socialagony.txt"
		#from compute_social_agony import compute_social_agony
		#players = compute_social_agony(graph_file,agony_path = "agony/agony ")		
		if False:
		#if os.path.isfile(agony_file):
			print("load pre-computed socialagony from: %s" % agony_file)
			players = read_dict_from_file(agony_file)
		else:
			print("start computing socialagony...")
			from compute_social_agony import compute_social_agony
			players = compute_social_agony(graph_file,agony_path = "agony/agony ")
			print("write socialagony to file: %s" % agony_file)
		return players
	g = nx.read_edgelist(graph_file,create_using = nx.DiGraph(),nodetype = nodetype)
	if players_score_func_name == "pagerank":
		#print("computing pagerank...")
		players = nx.pagerank(g, alpha = 0.85)
		return players
	elif players_score_func_name == "trueskill":
		output_file = tmp_prefix + ".trueskill.tmp"

		players = None
		if recycle:
			print("recycling trueskill from file: %s" % output_file)
			players = read_dict_from_file(output_file, int, float)
			
		if not players:
			print("start computing trueskill...")
			from true_skill import graphbased_trueskill
			players = graphbased_trueskill(g)

			print("write trueskill to file: %s" % output_file)
			write_dict_to_file(players,output_file)
		
		return players

def breaking_cycles_by_hierarchy_output( graph_file, out_file, recycle = False ):
	
	edge_file = out_file + ".edges.tmp"
	edges, tr = loadEdges( graph_file )
	write_pairs_to_file(edges, edge_file)
	
	players_score_dict  = compute_hierarchy( edge_file, out_file, 'trueskill', nodetype = int, recycle = recycle )
	e1, e2, e3, e4 = remove_cycle_edges_by_hierarchy( edge_file, players_score_dict, 'trueskill', nodetype = int, recycle = recycle )

	print( "write results to file: %s" % out_file )
	writeEdges( out_file, e4, tr )


import argparse
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument( "graph_file", help = "input graph file (edges list)" )
	parser.add_argument( "output_file", help = "output edge list file (edges list)" )
	parser.add_argument( "--recycle", help = "recycle temporary files if they exist (useful mostly for debugging)", action='store_true' )
	
	args = parser.parse_args()
	
	print args

	breaking_cycles_by_hierarchy_output( args.graph_file, args.output_file, recycle = args.recycle )

