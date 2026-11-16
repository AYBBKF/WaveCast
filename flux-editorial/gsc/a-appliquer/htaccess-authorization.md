# Mots de passe d'application WordPress : en-tête Authorization supprimé

Constat du 16/11 : une requête REST avec Basic Auth, même factice, renvoie `rest_not_logged_in` au lieu de `incorrect_password`. L'en-tête `Authorization` n'arrive donc pas jusqu'à PHP.

Correctif usuel chez Hostinger/LiteSpeed : dans `public_html/.htaccess`, **au-dessus** du bloc `# BEGIN WordPress`, ajouter :

    SetEnvIf Authorization "(.*)" HTTP_AUTHORIZATION=$1

Contrôle : `curl -s -u utilisateur:faux https://fluxintelligent.com/wp-json/wp/v2/users/me` doit renvoyer `incorrect_password` ou `invalid_username`.

Retour arrière : supprimer la ligne.

Si le problème persiste, vérifier qu'une extension de sécurité (WPMU DEV Defender, Hub Connector) ne désactive pas l'authentification REST par mot de passe d'application.
