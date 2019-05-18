<?php
require __DIR__ . '/../vendor/autoload.php';

use Symfony\Component\Finder\Finder;
use SebastianBergmann\PHPLOC\Analyser;

class ClassNameExtractor {
	/**
	 * Extract (first) class or interface name.
	 * 
	 * Code inspired by the Analyzer class in PHPLOC
	 * by Sepbastian Bergmann.
	 *
	 * @param string|false $filename
	 */
	public function extractName( $filename ) {
		$tokens    = \token_get_all(\file_get_contents($filename));
		$numTokens = \count($tokens);
		$namespace = false;

		for ( $i = 0; $i < $numTokens; $i++ ) {
			if (\is_string($tokens[$i])) {
				continue;
			}
			switch ($tokens[$i][0]) {
				case \T_NAMESPACE:
					$namespace = $this->getNamespaceName( $tokens, $i );
					break;
				case \T_INTERFACE:
				case \T_CLASS:
					if ( !$this->isClassDeclaration( $tokens, $i ) ) {
						break;
					}
					$className = $this->getClassName( $namespace, $tokens, $i );
					return $className;
			}
		}
		
		return false;
	}

    /**
     * Code stolen from PHPLOC's Analyzer class.
     *
     * @param int $i
     *
     * @return string
     */
    private function getNamespaceName( array $tokens, $i ) {
        if ( isset( $tokens[$i + 2][1] ) ) {
            $namespace = $tokens[$i + 2][1];
            for ( $j = $i + 3;; $j += 2 ) {
                if ( isset( $tokens[$j] ) && $tokens[$j][0] == \T_NS_SEPARATOR ) {
                    $namespace .= '\\' . $tokens[$j + 1][1];
                } else {
                    break;
                }
            }
            return $namespace;
        }
        return false;
    }

    /**
     * Code stolen from PHPLOC's Analyzer class.
     *
     * @param string $namespace
     * @param int    $i
     *
     * @return string
     */
    private function getClassName( $namespace, array $tokens, $i ) {
        $i += 2;
        if ( !isset($tokens[$i][1]) ) {
            return 'invalid class name';
        }
        $className  = $tokens[$i][1];
        $namespaced = $className === '\\';
        while ( \is_array( $tokens[$i + 1] ) && $tokens[$i + 1][0] !== \T_WHITESPACE ) {
            $className .= $tokens[++$i][1];
        }
        if ( !$namespaced && $namespace !== false ) {
            $className = $namespace . '\\' . $className;
        }
        return $className;
    }

    /**
     * Code copyied from PHPLOC's Analyzer class by Sepbastian Bergmann.
     * 
     * @param int $start
     *
     * @return bool
     */
    private function getPreviousNonWhitespaceTokenPos( array $tokens, $start ) {
        if ( isset( $tokens[$start - 1] ) ) {
            if ( isset( $tokens[$start - 1][0] ) &&
                $tokens[$start - 1][0] == \T_WHITESPACE &&
                isset( $tokens[$start - 2] ) ) {
                return $start - 2;
            }
            return $start - 1;
        }
        return false;
    }

    /**
     * Code copyied from PHPLOC's Analyzer class by Sepbastian Bergmann.
     * 
     * @param int $i
     *
     * @return bool
     */
    private function isClassDeclaration( array $tokens, $i ) {
        $n = $this->getPreviousNonWhitespaceTokenPos( $tokens, $i );
        return !isset( $tokens[$n] )
            || !\is_array( $tokens[$n] )
            || !\in_array( $tokens[$n][0], [\T_DOUBLE_COLON, \T_NEW], true );
    }
}

$nameExtractor = new ClassNameExtractor(); 

// print( "file\tloc\tncloc\tlloc\tccn\n" );
while ( $path = fgets( STDIN ) ) {
	$path = trim( $path );
	$analyzer = new Analyser();
	
	if ( is_dir( $path ) ) {
		$finder = new Finder();
		$finder->files()->name( '*.php' )->in( $path );

		$filesToCount = iterator_to_array( $finder );
		$name = $path;
	} else {
		if ( !file_exists( $path ) ) {
			continue;
		}
		$filesToCount = [ $path ];
		$name = $nameExtractor->extractName( $path );
		$name = $name ?: $path;
	}

	$stats = $analyzer->countFiles( $filesToCount, true );
	
	print( "$name\t{$stats['loc']}\t{$stats['ncloc']}\t{$stats['lloc']}\t{$stats['ccn']}\n" );
}
