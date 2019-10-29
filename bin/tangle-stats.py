#!/usr/bin/env python3
# This file is part of Project Ruprecht. See COPYING for license.

import sys
import csv
import graph_tool as gt
import graph_tool.topology as topo
	
def analyze_histogram( hist, weights = None ):
	num_total = 0
	sum_good = 0
	sum_total = 0
	largest_size = 0
	
	for n in range( 0, len( hist ) ):
		size = hist[n]
		w = weights[n] if weights else size;
		
		num_total += 1
		sum_total += w
		
		if size == 1:
			# if the component size is 1, the component is not a tangle,
			# so count the node as "good". 
			sum_good += w
		elif w > largest_size:
			largest_size = w
			
	return num_total, sum_good, sum_total, largest_size
	
def load_loc( path, g ):
	loc = g.new_vertex_property( "int" )
	names = g.vertex_properties["name"]
	g.vertex_properties["loc"] = loc

	vertex_by_name = {}

	for v in g.vertices():
		name = names[v]
		vertex_by_name[name] = v

	csv_file = open( path )
	csv_reader = csv.reader( csv_file, delimiter="\t" )

	for row in csv_reader:
		name = row[0]

		if name in vertex_by_name:
			key = vertex_by_name[name]
			loc[key] = int(row[1])
		
	return loc

def compute_weighted_histogram( g, comp, weights ):
	weighted_hist = {} # todo: make this an ndarray
	
	for v in g.vertices():
		label = comp[v]
		w = weights[v]

		if label in weighted_hist:
			weighted_hist[label] += w
		else:
			weighted_hist[label] = w
	
	return weighted_hist

def dump_vprops( g, prop ):
	m = {}
	
	for v in g.vertices():
		idx = g.vertex_index[ v ]
		m[idx] = prop[v]
	
	print( m )

def dump_nprops( prop ):
	m = {}
	
	for n in range( 0, len( prop ) ):
		m[n] = prop[n]
	
	print( m )

g = gt.load_graph_from_csv( sys.argv[1], csv_options = { 'delimiter': "\t" }, directed=True )

if len( sys.argv ) > 2:
	loc = load_loc( sys.argv[2], g )
else:
	loc = None

comp, hist = topo.label_components( g )

num_total, sum_good, sum_total, largest_size = analyze_histogram( hist )

if sum_total == 0:
	print( "No classes found!" )
	sys.exit( 3 )

print( "Number of nodes: %i" % ( sum_total ) )
# print( "Number of tangles: %i" % ( num_total- sum_good ) )
print( "Nodes in tangles: %i (%i%%)" % ( ( sum_total - sum_good ), ( 100 * ( sum_total - sum_good ) / sum_total ) ) )
print( "Nodes in largest tangle: %i (%i%%)" % ( largest_size, ( 100 * largest_size / sum_total ) ) )

if loc:
	loc_hist = compute_weighted_histogram( g, comp, loc );
	#dump_vprops( g, g.vertex_properties['name'] )
	#dump_vprops( g, comp )
	#dump_nprops( hist )
	#dump_nprops( loc_hist )

	num_total, sum_good, sum_total, largest_size = analyze_histogram( hist, loc_hist )
	print( "LoC: %i" % ( sum_total ) )
	# print( "LoC not tangled: %i" % ( sum_good ) )
	if sum_total:
		print( "LoC in tangles: %i (%i%%)" % ( ( sum_total - sum_good ), ( 100 * ( sum_total - sum_good ) / sum_total ) ) )
		print( "LoC in largest tangle: %i (%i%%)" % ( largest_size, ( 100 * largest_size / sum_total ) ) )
