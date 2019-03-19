<?php
/**
 * This file is part of mediawiki/dependency-analysis.
 *
 * @license GPL 2+
 * @author Daniel Kinzler
 */

namespace MediaWiki\DependencyAnalysis;

use Symfony\Component\Console\Application;

require __DIR__.'/../vendor/autoload.php';

$application = new Application('CycleReport' );

$application->add( new MetricsCommand() );
$application->setDefaultCommand( 'metrics', true );

$application->run();
