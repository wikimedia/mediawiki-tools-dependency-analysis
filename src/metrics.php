<?php
/**
 * This file is part of mediawiki/dependency-analysis.
 *
 * @license GPL 2+
 * @author Daniel Kinzler
 */

namespace MediaWiki\DependencyAnalysis;

require __DIR__ . '/../vendor/autoload.php';

function flatten( $array ) {
    return array_reduce( $array,
		function( $acc, $item ) {
			return array_merge(
				$acc,
				is_array( $item ) ? flatten( $item ) : [$item]
			);
		},
	[] );
}

function extractMetrics( $name, $file ) {
	$json = file_get_contents( $file );
	$data = json_decode( $json, JSON_OBJECT_AS_ARRAY );
	
	$inCycles = array_unique( flatten( $data['cycles'] ) );
	$numInCycles = count( $inCycles );
	$numEdges = count( $data['edges'] );
	$numVertices = count( $data['vertices'] );
	$numCycles = count( $data['cycles'] );

	$density = $numVertices
		? round( $numEdges / ( $numVertices * $numVertices ), 2 )
		: 0;

	$degree = $numVertices
		? round( ( $numEdges / $numVertices ), 2 )
		: 0;
	
	$cyclicity = $numVertices
		? round( $numInCycles / $numVertices, 2 )
		: 0;
		
	$metrics = [
		'entity' => $name,
		'edges' => $numEdges,
		'vertices' => $numVertices,
		'cycles' => $numCycles,
		'verticesInCycles' => $numInCycles,
		'cyclicity' => $cyclicity,
		'density' => $density,
		'degree' => $degree,
	];
	
	return $metrics;
}

function collectMetrics( $dir ) {
	$metrics = [
		'generator' => 'mediawiki-dependency-analysis',
		'timestamp' => gmdate( 'c' ),
		'metrics' => [],
	];
	
	$namespaceUsageReport = "$dir/namespace-usage.json";
	$classUsageReport = "$dir/class-usage.json";
	
	if ( file_exists( $namespaceUsageReport ) ) {
		$metrics['metrics'][] = extractMetrics(
			'namespaces', $namespaceUsageReport
		);
	}
	
	if ( file_exists( $classUsageReport ) ) {
		$metrics['metrics'][] = extractMetrics(
			'classes', $classUsageReport
		);
	}
	
	return $metrics;
}

function writeMetricsJson( $metrics, $outFile ) {
	$json = json_encode( $metrics, JSON_PRETTY_PRINT );
	file_put_contents( $outFile, $json );
}

function writeMetricsHtml( $metrics, $outFile ) {
	$template = __DIR__ . '/metrics.mustache';
	$mustache = file_get_contents( $template );
	
	$m = new \Mustache_Engine();
	file_put_contents( $outFile, $m->render( $mustache, $metrics ) );
}

if ( !isset( $argv[1] ) ) {
	echo( "USAGE: metrics.php <report-dir>" );
	exit( 1 );
}

$dir = $argv[1];

if ( !is_dir( $dir ) ) {
	echo( "Not found (or not a directory): $dir" );
	exit( 2 );
}

$metrics = collectMetrics( $dir );
writeMetricsJson( $metrics, "$dir/metrics.json" );
writeMetricsHtml( $metrics, "$dir/metrics.html" );
