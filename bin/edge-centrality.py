#!/usr/bin/env python3
# This file is part of Project Ruprecht. See COPYING for license.

import sys
import graph_tool as gt
import graph_tool.centrality as centr

def print_top_e( g, eprops ):
	names = g.vertex_properties['name'];

	ee = list( g.edges() )
	ee.sort( key= lambda a: eprops[a], reverse=True )	
	
	for e in ee:
		print( names[e.source()], names[e.target()] )

g = gt.load_graph_from_csv( sys.argv[1], csv_options = { 'delimiter': "\t" } )

btwv, btwe = centr.betweenness( g )
print_top_e( g, btwe )
