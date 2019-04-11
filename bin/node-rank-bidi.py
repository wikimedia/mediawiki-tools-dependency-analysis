#!/usr/bin/env python3
# This file is part of Project Ruprecht. See COPYING for license.

import sys
import graph_tool as gt
import graph_tool.centrality as centr

def print_top_v( g, vprops ):
	names = g.vertex_properties['name'];

	vv = list( g.vertices() )
	vv.sort( key= lambda a: vprops[a], reverse=True )
	
	for v in vv:
		print( names[v] )
			
def pageRankBiDi( g ):
	# calculate the product of the PageRange and reverse PageRank for each vertex
	pr = centr.pagerank( g )

	g.set_reversed( True )
	rpr = centr.pagerank( g )
	g.set_reversed( False )

	for v in g.vertices():
		pr[v] = pr[v] * rpr[v]
		
	return pr

g = gt.load_graph_from_csv( sys.argv[1], csv_options = { 'delimiter': "\t" } )

pr = pageRankBiDi( g )
print_top_v( g, pr )
