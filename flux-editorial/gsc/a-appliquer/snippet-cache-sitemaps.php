<?php
/**
 * Flux Intelligent : durée de cache courte pour les sitemaps XML Rank Math.
 * À coller dans Extensions > Code Snippets > Ajouter (type PHP, « Exécuter partout »).
 * Effet : les sitemaps envoient « Cache-Control: public, max-age=300, s-maxage=300 ».
 * Cloudflare (Browser Cache TTL « respecter les en-têtes ») et le cache serveur ne les gardent plus 4 h.
 * Le cache des autres pages n'est pas modifié. Retour arrière : désactiver le snippet.
 */
add_action( 'init', function () {
	$path = wp_parse_url( $_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH );
	if ( $path && preg_match( '#/(sitemap_index|[a-z0-9_-]+-sitemap[0-9]*)\.xml$#i', $path ) ) {
		header( 'Cache-Control: public, max-age=300, s-maxage=300', true );
		header( 'X-LiteSpeed-Cache-Control: no-cache', true ); // exclut le cache serveur LiteSpeed/Hostinger
	}
}, 0 );
