<?php
/**
 * This file is part of mediawiki/dependency-analysis.
 *
 * @license GPL 2+
 * @author Daniel Kinzler
 */

namespace MediaWiki\DependencyAnalysis;

require __DIR__.'/../vendor/autoload.php';

$mustache = '';

function readStdin() {
	$f = fopen( 'php://stdin', 'r' );
	$data = '';
	while( $line = fgets( $f ) ) {
	  $data .= $line;
	}
	
	return $data;
}

function writeStdout( $data ) {
	$f = fopen( 'php://stdout', 'a' );
	fputs ( $f, $data );
	fflush( $f );
}

function getDataFromArgs( $argv ) {
	$data = [];
	
	foreach ( $argv as $a ) {
		$a = trim( $a );

		if ( preg_match( '/^(\w+)\s*=\s*(.*?)$/', $a, $m ) ) {
			$data[$m[1]] = $m[2];
		} else {
			$data[$a] = true;
		}
	}
	
	return $data;
}

$data = getDataFromArgs( $argv );
$mustache = readStdin();

$m = new \Mustache_Engine();
$text = $m->render( $mustache, $data );

writeStdout( $text );
