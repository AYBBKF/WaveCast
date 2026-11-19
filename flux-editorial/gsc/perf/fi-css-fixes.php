<?php
/**
 * Plugin Name: Flux Intelligent — correctifs CSS ciblés (CLS contact, contraste villes)
 * Description: 1) Réserve la hauteur du formulaire Forminator 3117 (contact) avant
 *                 son affichage par JavaScript, et celle du widget Turnstile :
 *                 supprime le décalage de mise en page (CLS) du bloc situé dessous.
 *              2) Rétablit le texte blanc des boutons principaux des pages villes,
 *                 écrasé par la règle de liens « .fi-city .sec > p a » (contraste 1,41).
 *              Aucun style existant n'est retiré.
 * Version:     1.0.0
 *
 * Restauration : supprimer ce fichier (ou le renommer en .off), puis purger les URL.
 *
 * @package flux-intelligent
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

add_action(
	'wp_head',
	function () {
		if ( is_admin() || is_feed() ) {
			return;
		}
		/*
		 * Hauteurs finales mesurées le 19/11 : formulaire 590 px (< 900 px de large),
		 * 630 px (>= 900 px) ; conteneur Turnstile 73 px. Le pseudo-élément n'existe
		 * que tant que Forminator garde le formulaire en display:none ; dès que le
		 * formulaire s'affiche, il disparaît et le formulaire occupe la même hauteur.
		 */
		$css  = '.forminator-custom-form-3117 .forminator-turnstile{min-height:73px}';
		$css .= '.formcard:has(> form#forminator-module-3117[style*="display: none"])::after{content:"";display:block;height:590px}';
		$css .= '@media (min-width:900px){.formcard:has(> form#forminator-module-3117[style*="display: none"])::after{height:630px}}';
		$css .= '.fi-city .sec > p a.btn-primary,.fi-city .sec > p a.btn-primary:hover,.fi-city .band p a.btn-primary,.fi-city .band p a.btn-primary:hover{color:#fff}';
		// 3) Bouton « Envoyer » du formulaire de contact : fond violet sans couleur de texte (noir par défaut, contraste 3,38). Blanc, comme sur /rejoignez-nous/.
		$css .= '.fi-ct .forminator-ui .forminator-button-submit{color:#fff!important}';
		echo "<style id='fi-css-fixes'>" . $css . "</style>\n"; // phpcs:ignore WordPress.Security.EscapeOutput
	},
	99
);

/*
 * Articles : préchargement de l'image à la une (élément LCP), imprimé en tout
 * début de <head>, avant les préchargements de polices. Mêmes URL, srcset et
 * sizes que la balise <img> : aucun téléchargement supplémentaire.
 * Mode : FI_LCP_IMG_PRELOAD = 'test' (?fi_lcpimg=1), 'on' ou 'off'.
 */
if ( ! defined( 'FI_LCP_IMG_PRELOAD' ) ) {
	define( 'FI_LCP_IMG_PRELOAD', 'on' );
}
add_action(
	'wp_head',
	function () {
		if ( is_admin() || ! is_singular( 'post' ) || 'off' === FI_LCP_IMG_PRELOAD ) {
			return;
		}
		if ( 'test' === FI_LCP_IMG_PRELOAD && ! ( isset( $_GET['fi_lcpimg'] ) && '1' === $_GET['fi_lcpimg'] ) ) { // phpcs:ignore WordPress.Security.NonceVerification
			return;
		}
		$id = get_post_thumbnail_id( get_queried_object_id() );
		if ( ! $id ) {
			return;
		}
		$src = wp_get_attachment_image_src( $id, 'fi-media' );
		if ( ! $src ) {
			return;
		}
		$srcset = wp_get_attachment_image_srcset( $id, 'fi-media' );
		printf(
			'<link rel="preload" as="image" href="%s"%s imagesizes="(max-width:980px) 100vw, 740px" fetchpriority="high">' . "\n",
			esc_url( $src[0] ),
			$srcset ? ' imagesrcset="' . esc_attr( $srcset ) . '"' : ''
		);
	},
	0
);

/*
 * Archives (blog, catégories) : la première image de carte est l'élément LCP mais
 * le thème la charge en loading="lazy" (délai de découverte ~2,9 s en labo). Seule
 * cette première image passe en chargement immédiat et prioritaire ; les suivantes
 * restent en lazy. « auto, » est retiré de sizes (réservé aux images lazy).
 * Mode : FI_ARCHIVE_LCP = 'test' (?fi_card=1), 'on' ou 'off'.
 */
if ( ! defined( 'FI_ARCHIVE_LCP' ) ) {
	define( 'FI_ARCHIVE_LCP', 'on' );
}
add_filter(
	'wp_get_attachment_image_attributes',
	function ( $attr ) {
		static $done = false;
		if ( $done || is_admin() || 'off' === FI_ARCHIVE_LCP || ! ( is_home() || is_archive() ) || ! in_the_loop() ) {
			return $attr;
		}
		if ( 'test' === FI_ARCHIVE_LCP && ! ( isset( $_GET['fi_card'] ) && '1' === $_GET['fi_card'] ) ) { // phpcs:ignore WordPress.Security.NonceVerification
			return $attr;
		}
		if ( empty( $attr['class'] ) || false === strpos( $attr['class'], 'attachment-fi-card' ) ) {
			return $attr;
		}
		$done                  = true;
		$attr['loading']       = 'eager';
		$attr['fetchpriority'] = 'high';
		if ( isset( $attr['sizes'] ) ) {
			$attr['sizes'] = preg_replace( '/^auto,\s*/', '', $attr['sizes'] );
		}
		return $attr;
	},
	PHP_INT_MAX
);

/* Archives : préchargement de la première image de carte (même URL, srcset et sizes que la balise). */
add_action(
	'wp_head',
	function () {
		if ( is_admin() || 'off' === FI_ARCHIVE_LCP || ! ( is_home() || is_archive() ) ) {
			return;
		}
		if ( 'test' === FI_ARCHIVE_LCP && ! ( isset( $_GET['fi_card'] ) && '1' === $_GET['fi_card'] ) ) { // phpcs:ignore WordPress.Security.NonceVerification
			return;
		}
		global $wp_query;
		$first = ! empty( $wp_query->posts ) ? $wp_query->posts[0] : null;
		$id    = $first ? get_post_thumbnail_id( $first ) : 0;
		if ( ! $id ) {
			return;
		}
		$src = wp_get_attachment_image_src( $id, 'fi-card' );
		if ( ! $src ) {
			return;
		}
		$srcset = wp_get_attachment_image_srcset( $id, 'fi-card' );
		printf(
			'<link rel="preload" as="image" href="%s"%s imagesizes="(max-width:700px) 100vw, 280px" fetchpriority="high">' . "\n",
			esc_url( $src[0] ),
			$srcset ? ' imagesrcset="' . esc_attr( $srcset ) . '"' : ''
		);
	},
	0
);
