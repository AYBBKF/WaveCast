# Procédure validée : image mise en avant via le MCP wordpress-mcp

Validée le 03/11 sur la page 4489 (média 4536). Le téléversement base64 d'environ 20 000 caractères fonctionne, et le fichier en ligne a le même md5 que le fichier local.

Dossier de travail : /home/user/WaveCast/flux-editorial/exec. Correspondance contenu / image / alt dans `image-map.json`, dont les champs `img` et `alt` sont lus pour chaque slug.

Charge les schémas une fois avec ToolSearch : `select:mcp__wordpress-mcp__wp_upload_media,mcp__wordpress-mcp__wp_update_media,mcp__wordpress-mcp__wp_update_post,mcp__wordpress-mcp__wp_update_page,mcp__wordpress-mcp__wp_posts_search,mcp__wordpress-mcp__wp_pages_search`.

Pour CHAQUE contenu, un par un :

1. **Préparer le fichier** : `cd /home/user/WaveCast/flux-editorial/exec && python3 prep_img.py <slug>`. Le script produit /tmp/<slug>-up.webp en choisissant la plus grande largeur (800, 720 ou 640 px) et la meilleure qualité dont le base64 tient sous 22 000 caractères, ainsi que l'aperçu /tmp/<slug>-prev.jpg ; il affiche la taille base64 et le md5.
2. **Regarder l'aperçu** `/tmp/<slug>-prev.jpg` avec l'outil Read. Vérifie que l'alt de `image-map.json` décrit fidèlement l'image ; sinon, corrige-le.
3. **Encoder** : `base64 -w0 /tmp/<slug>-up.webp`. Copie la chaîne EXACTEMENT, sans rien ajouter ni retirer, dans `wp_upload_media` :
   - file = la chaîne ;
   - title = `<slug>` (c'est ce qui donne le nom de fichier) ;
   - post = ID du contenu.

   L'alt passé ici est ignoré.
4. **Vérifier le fichier** : `curl -s <source_url renvoyée> -o /tmp/<slug>-dl.webp -w "%{http_code} %{content_type}\n"; md5sum /tmp/<slug>-dl.webp`.
   - Exige 200, image/webp et un md5 identique.
   - Sinon, retente une seule fois. Si l'échec persiste, consigne l'échec et passe au contenu suivant, sans associer le média.
5. **Mettre l'alt** : `wp_update_media` avec id = ID du média, alt_text = l'alt, post = ID du contenu.
6. **Associer l'image** :
   - pour un article : `wp_update_post` avec {"id": ID, "featured_media": ID_MEDIA} ;
   - pour une page : `wp_update_page`.

   N'envoie RIEN d'autre (ni date, ni statut, ni contenu), pour conserver la date et le statut programmés.
7. **Contrôler** :
   - `wp_posts_search` (ou `wp_pages_search` pour une page) avec include [ID], status ["future","draft","publish"], context "embed" ;
   - vérifie que featured_media = ID_MEDIA et que la date n'a pas changé ;
   - pour un contenu publié, vérifie aussi `curl -s https://fluxintelligent.com/wp-json/wp/v2/posts/ID?_fields=featured_media` et la présence de l'URL de l'image dans le HTML public de l'article (`curl -s <lien> | grep -c <nom-fichier>`).
8. **Consigner** une ligne JSON dans `results-img/<slug>.json` : {"wp_id","slug","media_id","source_url","md5_ok","alt","featured_ok","date_avant","date_apres","statut","erreur"}.

L'aperçu WordPress d'un contenu programmé ou en brouillon exige d'être connecté, ce que la session n'a pas : le contrôle se fait sur l'API (featured_media), le fichier (200 + md5) et l'alt du média. Pour un contenu déjà publié, contrôle aussi le HTML public.

Réponse finale : une ligne par contenu (ID, média, featured OK, date inchangée, erreur éventuelle), sans recopier les chaînes base64.
