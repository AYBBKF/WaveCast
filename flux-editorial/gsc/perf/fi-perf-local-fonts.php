<?php
/**
 * Plugin Name: Flux Intelligent — polices Space Grotesk / Public Sans auto-hébergées
 * Description: Sur les pages dont le contenu appelle Google Fonts (pages villes,
 *              rejoignez-nous), remplace la feuille fonts.googleapis.com, bloquante
 *              et tierce, par les mêmes fichiers woff2 servis depuis le site
 *              (uploads/fi-fonts/), mêmes familles, graisses, unicode-range et
 *              font-display:swap. Les deux fichiers latins sont préchargés.
 * Version:     1.0.0
 *
 * Restauration : supprimer ce fichier (ou le renommer en .off), puis purger le
 * cache HTML. Le <link> Google Fonts du contenu revient tel quel.
 *
 * @package flux-intelligent
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/* 'test' = uniquement avec ?fi_inline=1 ; 'on' = toutes les pages ; 'off'. */
if ( ! defined( 'FI_LOCAL_FONTS_MODE' ) ) {
	define( 'FI_LOCAL_FONTS_MODE', 'on' );
}

const FI_LOCAL_FONTS_RE = '#<link[^>]+href=["\']https://fonts\.googleapis\.com/css2\?family=Space\+Grotesk:wght@500;600;700&(?:\#038;|amp;)?family=Public\+Sans:wght@400;500;600&(?:\#038;|amp;)?display=swap["\'][^>]*>\s*#i';

function fi_local_fonts_css() {
	static $css = null;
	if ( null === $css ) {
		$uploads = wp_upload_dir( null, false );
		$file    = trailingslashit( $uploads['basedir'] ) . 'fi-fonts/fi-local-fonts.css';
		$css     = is_readable( $file ) ? (string) file_get_contents( $file ) : ''; // phpcs:ignore WordPress.WP.AlternativeFunctions
		if ( false !== stripos( $css, '</style' ) ) {
			$css = '';
		}
	}
	return $css;
}

function fi_local_fonts_active() {
	static $on = null;
	if ( null !== $on ) {
		return $on;
	}
	$on = false;
	if ( is_admin() || is_feed() || ! is_singular() || 'off' === FI_LOCAL_FONTS_MODE ) {
		return $on;
	}
	if ( 'test' === FI_LOCAL_FONTS_MODE && ! ( isset( $_GET['fi_inline'] ) && '1' === $_GET['fi_inline'] ) ) { // phpcs:ignore WordPress.Security.NonceVerification
		return $on;
	}
	$post = get_queried_object();
	if ( ! $post instanceof WP_Post || ! preg_match( FI_LOCAL_FONTS_RE, $post->post_content ) || '' === fi_local_fonts_css() ) {
		return $on;
	}
	$on = true;
	return $on;
}

add_action(
	'wp_head',
	function () {
		if ( ! fi_local_fonts_active() ) {
			return;
		}
		$base = trailingslashit( wp_upload_dir( null, false )['baseurl'] ) . 'fi-fonts/';
		foreach ( array( 'spacegrotesk-87c506d8.woff2', 'publicsans-e4c9b081.woff2' ) as $f ) {
			printf( '<link rel="preload" as="font" type="font/woff2" href="%s" crossorigin>' . "\n", esc_url( set_url_scheme( $base . $f ) ) );
		}
		echo "<style id='fi-local-fonts'>" . fi_local_fonts_css() . "</style>\n"; // phpcs:ignore WordPress.Security.EscapeOutput
	},
	2
);

add_filter(
	'the_content',
	function ( $content ) {
		if ( ! fi_local_fonts_active() || ! is_main_query() || get_the_ID() !== get_queried_object_id() ) {
			return $content;
		}
		return preg_replace( FI_LOCAL_FONTS_RE, '', $content, 1 );
	},
	PHP_INT_MAX
);
