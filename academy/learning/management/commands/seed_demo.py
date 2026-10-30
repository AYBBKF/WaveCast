"""Crée (ou recrée) la formation de démonstration et les réglages par défaut.

Usage : python manage.py seed_demo [--reset]
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from learning.models import Choice, Course, Lesson, Module, Question, RewardOffer, SiteSettings

DEMO_SLUG = "comprendre-ia-automatiser-petite-entreprise"

MODULES = [
    (
        "Comprendre l'IA sans jargon",
        [
            (
                "Ce qu'est (et n'est pas) l'intelligence artificielle",
                7,
                """
<p>L'intelligence artificielle (IA) désigne des programmes capables d'accomplir des tâches qui demandaient jusqu'ici un raisonnement humain : comprendre un texte, rédiger une réponse, classer des informations, reconnaître une image.</p>
<h2>Les assistants conversationnels</h2>
<p>Les outils les plus utiles pour une petite entreprise sont les <strong>assistants conversationnels</strong> (Claude, ChatGPT, Gemini…). On leur écrit une consigne en langage courant — un <em>prompt</em> — et ils répondent par un texte : un brouillon d'e-mail, un résumé, un tableau, une liste d'idées.</p>
<div class="exemple"><p><strong>Exemple :</strong> « Voici l'e-mail d'un client mécontent. Propose une réponse polie qui s'excuse du retard et propose une remise de 10 %. » En quelques secondes, vous obtenez un brouillon à relire et ajuster.</p></div>
<h2>Ce que l'IA n'est pas</h2>
<ul>
<li>Elle ne « sait » pas tout : elle peut se tromper avec assurance. On parle d'<strong>hallucination</strong>.</li>
<li>Elle ne connaît pas votre entreprise tant que vous ne lui donnez pas le contexte.</li>
<li>Elle ne remplace pas votre jugement : vous restez responsable de ce qui est envoyé.</li>
</ul>
<div class="attention"><p>Ne collez jamais dans un outil d'IA des données sensibles (mots de passe, coordonnées bancaires, dossiers médicaux) sans avoir vérifié les conditions d'utilisation et les réglages de confidentialité de l'outil.</p></div>
""",
                "<p>L'IA est un assistant qui produit des brouillons à partir de vos consignes. Elle peut se tromper : relisez toujours avant d'envoyer, et ne lui confiez pas de données sensibles.</p>",
            ),
            (
                "Ce que l'IA sait bien faire dans une petite entreprise",
                6,
                """
<p>Pour une TPE ou une PME, l'IA est surtout utile sur des tâches <strong>textuelles et répétitives</strong>.</p>
<h2>Quatre familles de tâches</h2>
<ol>
<li><strong>Rédiger</strong> : e-mails, devis, fiches produits, publications.</li>
<li><strong>Résumer</strong> : un long échange, un compte rendu de réunion, un document.</li>
<li><strong>Classer et extraire</strong> : retrouver le nom, le besoin et l'urgence dans une demande client.</li>
<li><strong>Transformer</strong> : passer des notes en tableau, traduire, reformuler plus simplement.</li>
</ol>
<div class="exemple"><p><strong>Exemple :</strong> une agence de voyage reçoit 40 demandes par semaine via son formulaire. L'IA lit chaque demande et en extrait la destination, le budget et les dates dans un tableau. La gérante n'a plus qu'à rappeler les demandes prioritaires.</p></div>
<div class="astuce"><p>Plus la consigne est précise (rôle, contexte, format attendu, ton), meilleur est le résultat. « Réponds en 5 lignes, ton chaleureux, tutoiement interdit » vaut mieux que « réponds au client ».</p></div>
""",
                "<p>L'IA excelle pour rédiger, résumer, classer et transformer du texte. Une consigne précise (contexte, format, ton) donne un meilleur résultat.</p>",
            ),
        ],
    ),
    (
        "Repérer les tâches à automatiser",
        [
            (
                "Cartographier ses tâches répétitives",
                6,
                """
<p>Avant de choisir un outil, il faut savoir <strong>où part votre temps</strong>. Pendant une semaine, notez les tâches que vous refaites souvent.</p>
<h2>La grille en trois questions</h2>
<ul>
<li><strong>Fréquence</strong> : combien de fois par semaine ?</li>
<li><strong>Durée</strong> : combien de minutes à chaque fois ?</li>
<li><strong>Règles</strong> : la tâche suit-elle toujours les mêmes étapes ?</li>
</ul>
<p>Multipliez fréquence × durée pour obtenir le temps passé par semaine.</p>
<div class="exemple"><p><strong>Exemple :</strong> recopier les demandes du formulaire du site dans un tableur : 20 fois par semaine × 5 minutes = <strong>100 minutes</strong> par semaine, avec des étapes toujours identiques. C'est une excellente candidate.</p></div>
""",
                "<p>Notez vos tâches pendant une semaine et calculez fréquence × durée. Les tâches fréquentes, longues et aux étapes toujours identiques sont les meilleures candidates.</p>",
            ),
            (
                "Choisir la première automatisation",
                6,
                """
<p>La première automatisation doit être <strong>simple, utile et peu risquée</strong>. Un premier succès rapide donne confiance à toute l'équipe.</p>
<h2>Les bons critères</h2>
<ul>
<li>Un gain de temps visible (au moins une heure par semaine).</li>
<li>Peu de conséquences en cas d'erreur : un brouillon relu plutôt qu'un envoi automatique au client.</li>
<li>Des outils que vous utilisez déjà (messagerie, tableur, formulaire).</li>
</ul>
<div class="attention"><p>Évitez de commencer par une tâche qui engage l'entreprise sans relecture humaine : facturation, réponses juridiques, décisions RH.</p></div>
<div class="astuce"><p>Des outils d'automatisation sans code (comme n8n, Make ou Zapier) relient vos applications entre elles : « quand un formulaire arrive, ajoute une ligne au tableur et préviens-moi ».</p></div>
""",
                "<p>Commencez par une tâche simple, à gain visible et peu risquée, en gardant une relecture humaine avant tout envoi important.</p>",
            ),
        ],
    ),
    (
        "Automatiser la relation client",
        [
            (
                "Répondre plus vite aux demandes clients",
                7,
                """
<p>Un client qui attend une réponse plus d'une journée va souvent voir ailleurs. L'IA aide à <strong>trier</strong> et à <strong>préparer</strong> les réponses.</p>
<h2>Un circuit simple</h2>
<ol>
<li>La demande arrive (formulaire, e-mail, WhatsApp).</li>
<li>L'IA la classe : devis, réclamation, question pratique.</li>
<li>Elle prépare un brouillon de réponse adapté.</li>
<li>Un membre de l'équipe relit et envoie.</li>
</ol>
<div class="exemple"><p><strong>Exemple :</strong> un plombier reçoit « Fuite sous l'évier, c'est urgent, je suis à Casablanca Maarif ». L'IA classe la demande en <em>urgence</em>, extrait le quartier et prépare : « Bonjour, nous pouvons passer aujourd'hui entre 14 h et 16 h. Pouvez-vous confirmer votre adresse ? »</p></div>
<div class="astuce"><p>Préparez une petite « fiche entreprise » (horaires, zones, tarifs de base, ton à employer) à donner à l'IA à chaque fois : ses réponses seront cohérentes.</p></div>
""",
                "<p>Classer chaque demande puis préparer un brouillon relu par l'équipe permet de répondre vite sans perdre en qualité. Une fiche entreprise rend les réponses cohérentes.</p>",
            ),
            (
                "Suivre ses prospects sans rien oublier",
                6,
                """
<p>Beaucoup de ventes se perdent faute de <strong>relance</strong>. Un suivi simple dans un tableur ou un CRM suffit, à condition qu'il soit tenu à jour.</p>
<h2>Les colonnes indispensables</h2>
<ul>
<li>Nom et contact du prospect</li>
<li>Besoin exprimé</li>
<li>Étape : nouveau, devis envoyé, en négociation, gagné, perdu</li>
<li>Date de la prochaine relance</li>
</ul>
<p>L'automatisation remplit le tableau à chaque nouvelle demande et vous envoie chaque matin la liste des relances du jour. L'IA peut rédiger le message de relance à partir de l'historique.</p>
<div class="exemple"><p><strong>Exemple :</strong> « Rédige une relance courte pour M. Benali, devis de rénovation envoyé il y a 7 jours, sans réponse. Ton cordial, propose un appel. »</p></div>
""",
                "<p>Un tableau de suivi avec une date de prochaine relance, rempli automatiquement, évite d'oublier des prospects. L'IA peut rédiger les relances.</p>",
            ),
        ],
    ),
    (
        "Gagner du temps au bureau",
        [
            (
                "Rédiger et trier ses e-mails avec l'IA",
                6,
                """
<p>La messagerie absorbe souvent une à deux heures par jour. L'IA aide à <strong>rédiger plus vite</strong> et à <strong>repérer l'essentiel</strong>.</p>
<h2>Trois usages concrets</h2>
<ul>
<li>Transformer trois mots-clés en e-mail complet et poli.</li>
<li>Résumer un long fil d'échanges en cinq points.</li>
<li>Proposer plusieurs versions d'un message délicat (refus, retard, réclamation).</li>
</ul>
<div class="exemple"><p><strong>Exemple :</strong> « Résume ce fil de 15 messages avec le fournisseur : ce qui a été décidé, ce qui reste à faire, et qui doit agir. »</p></div>
<div class="attention"><p>Relisez toujours les chiffres, dates et noms propres : c'est là que l'IA se trompe le plus souvent.</p></div>
""",
                "<p>L'IA rédige, résume et reformule vos e-mails. Vérifiez systématiquement les chiffres, dates et noms avant d'envoyer.</p>",
            ),
            (
                "Automatiser son reporting et mesurer les gains",
                7,
                """
<p>Le <strong>reporting</strong> (chiffre d'affaires de la semaine, nombre de demandes, devis signés) est souvent fait à la main dans un tableur. Il peut être généré automatiquement.</p>
<h2>Un rapport hebdomadaire automatique</h2>
<ol>
<li>Les données sont déjà dans vos outils (tableur, logiciel de caisse, CRM).</li>
<li>Chaque lundi, une automatisation rassemble les chiffres.</li>
<li>L'IA rédige un court commentaire : ce qui progresse, ce qui baisse.</li>
<li>Le rapport arrive par e-mail à l'équipe.</li>
</ol>
<h2>Mesurer le gain</h2>
<p>Comparez le temps passé <strong>avant</strong> et <strong>après</strong> : si le rapport prenait 2 heures et ne prend plus que 15 minutes de relecture, vous gagnez 1 h 45 par semaine, soit plus de 80 heures par an.</p>
<div class="astuce"><p>Notez ce gain dans un tableau : il justifie les automatisations suivantes et aide à choisir les prochaines priorités.</p></div>
""",
                "<p>Un rapport hebdomadaire peut être assemblé et commenté automatiquement. Mesurez le temps avant/après pour chiffrer le gain réel.</p>",
            ),
        ],
    ),
]

# (texte, type, [(réponse, correcte)], explication, index de la leçon liée 0-7)
QUESTIONS = [
    ("Qu'appelle-t-on une « hallucination » d'une IA ?", "mcq",
     [("Une réponse fausse donnée avec assurance", True), ("Une panne du logiciel", False),
      ("Une image générée par l'IA", False), ("Une réponse trop longue", False)],
     "Une hallucination est une information inventée ou fausse que l'IA présente comme vraie. C'est pourquoi il faut toujours relire ses réponses.", 0),
    ("Vous restez responsable des messages envoyés, même s'ils ont été rédigés par une IA.", "tf",
     [("Vrai", True), ("Faux", False)],
     "L'IA produit des brouillons ; c'est l'entreprise qui envoie et engage sa responsabilité. La relecture humaine reste indispensable.", 0),
    ("Parmi ces consignes, laquelle donnera le meilleur résultat ?", "mcq",
     [("« Réponds au client. »", False),
      ("« Réponds à ce client en 5 lignes, ton chaleureux, en proposant un rendez-vous jeudi. »", True),
      ("« Fais au mieux. »", False), ("« Écris un e-mail. »", False)],
     "Une consigne efficace précise le contexte, le format, le ton et l'objectif. Plus elle est précise, plus le brouillon est utilisable.", 1),
    ("Une tâche faite 20 fois par semaine pendant 5 minutes représente combien de temps par semaine ?", "mcq",
     [("25 minutes", False), ("50 minutes", False), ("100 minutes", True), ("200 minutes", False)],
     "On multiplie la fréquence par la durée : 20 × 5 = 100 minutes, soit plus d'une heure et demie chaque semaine.", 2),
    ("Pour une première automatisation, il vaut mieux commencer par la facturation envoyée automatiquement aux clients sans relecture.", "tf",
     [("Vrai", False), ("Faux", True)],
     "La première automatisation doit être peu risquée. Une facture envoyée sans relecture engage l'entreprise : mieux vaut commencer par une tâche dont les erreurs sont sans conséquence.", 3),
    ("À quoi sert un outil d'automatisation sans code comme n8n, Make ou Zapier ?", "mcq",
     [("À remplacer votre site internet", False), ("À relier vos applications pour enchaîner des actions automatiquement", True),
      ("À stocker vos mots de passe", False), ("À écrire du code à votre place", False)],
     "Ces outils connectent vos applications : « quand un formulaire arrive, ajoute une ligne au tableur et préviens-moi ».", 3),
    ("Dans le circuit de réponse aux demandes clients, quelle étape reste humaine ?", "mcq",
     [("La réception de la demande", False), ("Le classement de la demande", False),
      ("La relecture et l'envoi de la réponse", True), ("Aucune, tout est automatique", False)],
     "L'IA classe et prépare un brouillon ; un membre de l'équipe relit et envoie. Cela garantit la qualité et la justesse de la réponse.", 4),
    ("Quelle information est indispensable dans un tableau de suivi des prospects pour ne rien oublier ?", "mcq",
     [("La couleur préférée du prospect", False), ("La date de la prochaine relance", True),
      ("Le nombre de visites sur le site", False), ("La météo du jour", False)],
     "La date de prochaine relance permet de recevoir chaque matin la liste des prospects à recontacter : c'est elle qui évite les ventes perdues.", 5),
    ("Lors de la relecture d'un e-mail rédigé par l'IA, sur quoi faut-il être le plus vigilant ?", "mcq",
     [("La police d'écriture", False), ("Les chiffres, dates et noms propres", True),
      ("La longueur des paragraphes", False), ("Le nombre de virgules", False)],
     "Les chiffres, dates et noms propres sont les éléments où l'IA se trompe le plus souvent, et les erreurs les plus coûteuses.", 6),
    ("Un rapport qui prenait 2 heures ne demande plus que 15 minutes de relecture. Quel est le gain par semaine ?", "mcq",
     [("15 minutes", False), ("1 heure", False), ("1 h 45", True), ("2 heures", False)],
     "2 h − 15 min = 1 h 45 gagnées chaque semaine, soit plus de 80 heures sur une année.", 7),
]


class Command(BaseCommand):
    help = "Crée la formation de démonstration « Comprendre l'IA et automatiser les tâches d'une petite entreprise »."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Supprime et recrée la formation de démonstration (si personne n'a commencé).")

    @transaction.atomic
    def handle(self, *args, **opts):
        SiteSettings.load()
        existing = Course.objects.filter(slug=DEMO_SLUG).first()
        if existing and not opts["reset"]:
            self.stdout.write("La formation de démonstration existe déjà (utilisez --reset pour la recréer).")
            return
        if existing:
            if existing.enrollments.exists():
                self.stderr.write("Des apprenants ont commencé la démo : elle n'est pas supprimée.")
                return
            existing.delete()

        course = Course.objects.create(
            title="Comprendre l'IA et automatiser les tâches d'une petite entreprise",
            slug=DEMO_SLUG,
            summary="Formation de démonstration : les bases de l'IA et quatre automatisations concrètes pour gagner du temps chaque semaine.",
            description=(
                "Cette formation de démonstration montre le fonctionnement de la plateforme. "
                "Elle explique simplement ce qu'est l'intelligence artificielle, comment repérer les tâches à automatiser "
                "et comment gagner du temps sur les demandes clients, le suivi des prospects, les e-mails et le reporting. "
                "Aucun prérequis technique."
            ),
            objectives="\n".join([
                "Comprendre ce que l'IA sait faire et ses limites",
                "Repérer les tâches répétitives qui valent la peine d'être automatisées",
                "Accélérer les réponses aux demandes clients et le suivi des prospects",
                "Gagner du temps sur les e-mails et le reporting, et mesurer ce gain",
            ]),
            level=Course.Level.BEGINNER,
            duration="1 heure",
            status=Course.Status.PUBLISHED,
            is_demo=True,
        )
        lessons = []
        for mpos, (mtitle, items) in enumerate(MODULES):
            module = Module.objects.create(course=course, title=mtitle, position=mpos)
            for lpos, (title, minutes, content, takeaway) in enumerate(items):
                lessons.append(Lesson.objects.create(
                    module=module, title=title, reading_minutes=minutes, position=lpos,
                    content=content.strip(), key_takeaway=takeaway,
                ))
        for qpos, (text, kind, choices, explanation, lesson_idx) in enumerate(QUESTIONS):
            q = Question.objects.create(course=course, text=text, kind=kind, explanation=explanation,
                                        related_lesson=lessons[lesson_idx], position=qpos)
            for cpos, (ctext, ok) in enumerate(choices):
                Choice.objects.create(question=q, text=ctext, is_correct=ok, position=cpos)

        # Offre Claude Pro préparée en brouillon : à compléter et activer par l'administration.
        RewardOffer.objects.get_or_create(course=course, defaults={"duration_label": "1 mois", "is_active": False})
        self.stdout.write(self.style.SUCCESS(
            f"Formation de démonstration créée : {len(lessons)} leçons, {len(QUESTIONS)} questions. Offre Claude Pro en brouillon."
        ))
