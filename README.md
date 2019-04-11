This project contains scripts for generating reports about cyclic
dependencies in the [MediaWiki](https://mediawiki.org) code base. 
The analysis is based on [phpda](https://github.com/mamuz/PhpDependencyAnalysis).

Installation
--------------
* ensure that you have both Python 2 and Python 3 installed
* ensure that you have graph-tool for Python 3 installed (see [https://git.skewed.de/count0/graph-tool/wikis/installation-instructions](graph-tool installation instructions))
* ensure that you have networkx for Python 2 installed (use pip)
* clone this repository
* run `git submodule update --init --recursive` to pull in submodules
* run `composer install` to pull in libraries

Usage
------
* call `bin/generate-reports *<path-to-mediawiki>*`
* a report will be generated in www/report
* visit [the www directory](./www/) with your browser

License
--------
(c) Wikimedia Foundation 2019, licensed [GPL 2.0 or later](./COPYING).
