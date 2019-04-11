#!/usr/bin/env python3
# This file is part of Project Ruprecht. See COPYING for license.

import sys
import graph_tool as gt
import graph_tool.topology as topo
	
def analyze_histogram( hist ):
	num_total = 0
	num_small = 0
	sum_total = 0
	largest_size = 0
	
	for size in hist:
		num_total += 1
		sum_total += size
		
		if size == 1:
			num_small += 1

		if size > largest_size:
			largest_size = size
			
	return num_total, num_small, sum_total, largest_size

g = gt.load_graph_from_csv( sys.argv[1], csv_options = { 'delimiter': "\t" } )

comp, hist = topo.label_components( g )
num_total, num_small, sum_total, largest_size = analyze_histogram( hist )
print( "Numer of nodes: %i" % ( sum_total ) )
# print( "Numer of tangles: %i" % ( num_total- num_small ) )
print( "Nodes in tangles: %i (%i%%)" % ( ( sum_total - num_small ), ( 100 * ( sum_total - num_small ) / sum_total ) ) )
print( "Nodes in largest tangle: %i (%i%%)" % ( largest_size, ( 100 * largest_size / sum_total ) ) )
