<?php
/**
 * Plugin Name: Flux Intelligent — CSS critiques en ligne (FCP/LCP mobile)
 * Description: Imprime directement dans le <head> le contenu des feuilles de style
 *              locales bloquant le rendu (thème, global-styles, block-library,
 *              CSS de contenu fi-css). Supprime un aller-retour réseau avant le
 *              premier affichage. Même ordre, même contenu : aucun style n'est
 *              retiré ni modifié (seuls les chemins url() relatifs deviennent absolus).
 * Version:     1.0.0
 *
 * Restauration : supprimer ce fichier (ou le renommer en .off), puis purger le
 * cache HTML. Les <link rel="stylesheet"> d'origine reviennent tels quels.
 *
 * @package flux-intelligent
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/*
 * Mode : 'test' = actif uniquement avec ?fi_inline=1 (comparaison A/B),
 *        'on'   = actif pour toutes les pages publiques,
 *        'off'  = désactivé.
 */
if ( ! defined( 'FI_INLINE_CSS_MODE' ) ) {
	define( 'FI_INLINE_CSS_MODE', 'on' );
}

/** Taille maximale cumulée imprimée en ligne (octets non compressés). */
const FI_INLINE_CSS_MAX_TOTAL = 120000;
/** Taille maximale d'un fichier imprimé en ligne. */
const FI_INLINE_CSS_MAX_FILE = 60000;

function fi_inline_css_active() {
	static $on = null;
	if ( null !== $on ) {
		return $on;
	}
	$on = false;
	if ( is_admin() || wp_doing_ajax() || is_feed() || is_customize_preview() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) ) {
		return $on;
	}
	if ( 'on' === FI_INLINE_CSS_MODE ) {
		$on = true;
	} elseif ( 'test' === FI_INLINE_CSS_MODE ) {
		$on = isset( $_GET['fi_inline'] ) && in_array( $_GET['fi_inline'], array( '1', '2' ), true ); // phpcs:ignore WordPress.Security.NonceVerification
	}
	return $on;
}

/**
 * Chemin local d'une URL de feuille de style du site, ou null si elle est externe.
 */
function fi_inline_css_local_path( $src ) {
	$src = strtok( $src, '?#' );
	if ( 0 === strpos( $src, '//' ) ) {
		$src = 'https:' . $src;
	}
	$s       = set_url_scheme( $src, 'https' );
	$uploads = wp_upload_dir( null, false );
	$map     = array(
		set_url_scheme( trailingslashit( $uploads['baseurl'] ), 'https' ) => trailingslashit( $uploads['basedir'] ),
		set_url_scheme( trailingslashit( content_url() ), 'https' )       => trailingslashit( WP_CONTENT_DIR ),
		set_url_scheme( trailingslashit( includes_url() ), 'https' )      => trailingslashit( ABSPATH . WPINC ),
		set_url_scheme( home_url( '/' ), 'https' )                        => ABSPATH,
	);
	foreach ( $map as $url => $dir ) {
		if ( 0 !== strpos( $s, $url ) ) {
			continue;
		}
		$rel  = substr( $s, strlen( $url ) );
		$path = wp_normalize_path( $dir . ltrim( $rel, '/' ) );
		if ( false !== strpos( $rel, '..' ) || '.css' !== substr( $path, -4 ) || ! is_file( $path ) ) {
			return null;
		}
		return $path;
	}
	return null;
}

/** Rend absolus les url() relatifs, par rapport au dossier du fichier d'origine. */
function fi_inline_css_rebase( $css, $src ) {
	$base = trailingslashit( dirname( strtok( $src, '?#' ) ) );
	return preg_replace_callback(
		'#url\(\s*([\'"]?)(?!data:|https?:|//|/|\#)([^\'")]+)\1\s*\)#i',
		function ( $m ) use ( $base ) {
			$u     = $base . $m[2];
			$parts = explode( '/', preg_replace( '#^https?://[^/]+#', '', $u ) );
			$out   = array();
			foreach ( $parts as $p ) {
				if ( '..' === $p ) {
					array_pop( $out );
				} elseif ( '.' !== $p ) {
					$out[] = $p;
				}
			}
			$host = preg_match( '#^https?://[^/]+#', $u, $h ) ? $h[0] : '';
			return 'url(' . $m[1] . $host . implode( '/', $out ) . $m[1] . ')';
		},
		$css
	);
}

add_filter(
	'style_loader_tag',
	function ( $tag, $handle, $href, $media ) {
		static $total = 0;
		if ( ! fi_inline_css_active() ) {
			return $tag;
		}
		if ( false === stripos( $tag, "rel='stylesheet'" ) && false === stripos( $tag, 'rel="stylesheet"' ) ) {
			return $tag;
		}
		if ( $media && ! in_array( $media, array( 'all', 'screen' ), true ) ) {
			return $tag;
		}
		$path = fi_inline_css_local_path( $href );
		if ( ! $path ) {
			return $tag;
		}
		$size = filesize( $path );
		$big  = isset( $_GET['fi_inline'] ) && '2' === $_GET['fi_inline'] && 'test' === FI_INLINE_CSS_MODE; // phpcs:ignore WordPress.Security.NonceVerification
		$mf   = $big ? 80000 : FI_INLINE_CSS_MAX_FILE;
		$mt   = $big ? 300000 : FI_INLINE_CSS_MAX_TOTAL;
		if ( ! $size || $size > $mf || $total + $size > $mt ) {
			return $tag;
		}
		$css = file_get_contents( $path ); // phpcs:ignore WordPress.WP.AlternativeFunctions
		if ( false === $css || false !== stripos( $css, '</style' ) || false !== stripos( $css, '@import' ) ) {
			return $tag;
		}
		$total += $size;
		$css    = fi_inline_css_rebase( $css, $href );
		$GLOBALS['fi_inline_css_orig'][ $handle ] = $tag;
		return sprintf( "<style id='%s-inline-file'>%s</style>\n", esc_attr( $handle ), $css );
	},
	PHP_INT_MAX,
	4
);

/*
 * Tout ou rien, décidé sur le HTML final (après la remontée par WordPress des
 * feuilles imprimées en pied de page) : s'il reste dans le <head> une feuille
 * <link rel="stylesheet"> bloquante, la mise en ligne n'apporterait rien (il
 * resterait un aller-retour) et alourdirait le HTML. On restaure alors les
 * balises <link> d'origine : la page est servie exactement comme avant.
 */
$GLOBALS['fi_inline_css_orig'] = array();
add_action(
	'template_redirect',
	function () {
		if ( ! fi_inline_css_active() ) {
			return;
		}
		ob_start(
			function ( $html ) {
				$orig = $GLOBALS['fi_inline_css_orig'];
				if ( empty( $orig ) || ! is_string( $html ) ) {
					return $html;
				}
				$end  = stripos( $html, '</head>' );
				$head = false === $end ? '' : substr( $html, 0, $end );
				$blocking = false;
				if ( preg_match_all( '#<link\b[^>]*rel=[\'"]stylesheet[\'"][^>]*>#i', $head, $mm ) ) {
					foreach ( $mm[0] as $l ) {
						if ( ! preg_match( '#media=[\'"]print[\'"]#i', $l ) ) {
							$blocking = true;
							break;
						}
					}
				}
				if ( ! $blocking ) {
					return $html;
				}
				foreach ( $orig as $handle => $tag ) {
					$html = preg_replace_callback(
						"#<style id='" . preg_quote( esc_attr( $handle ), '#' ) . "-inline-file'>.*?</style>\n?#s",
						function () use ( $tag ) {
							return $tag;
						},
						$html,
						1
					);
				}
				return $html;
			}
		);
	},
	0
);

