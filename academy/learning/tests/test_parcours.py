"""Parcours de bout en bout : inscription → leçons → examen → note → certificat (+ récompense Claude Pro)."""

import shutil
import tempfile
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from learning import services
from learning.models import (
    Certificate, Choice, Course, ExamAttempt, LessonProgress, Question, RewardClaim, RewardOffer,
)

TMP_PRIVATE = tempfile.mkdtemp(prefix="academy-test-")
PASSWORD = "Mot-de-passe-solide-2026"
SLUG = "comprendre-ia-automatiser-petite-entreprise"


@override_settings(PRIVATE_ROOT=TMP_PRIVATE, ACADEMY_BASE_URL="https://academy.example.ma")
class Base(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0)
        cls.course = Course.objects.get(slug=SLUG)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_PRIVATE, ignore_errors=True)

    # -- utilitaires
    def make_user(self, email="lina@example.ma", name="Lina Bennani", verified=True, staff=False):
        user = get_user_model().objects.create_user(username=email, email=email, password=PASSWORD, is_staff=staff)
        user.profile.full_name = name
        if verified:
            user.profile.email_verified_at = timezone.now()
        user.profile.save()
        return user

    def login(self, user):
        self.client.force_login(user, backend="learning.auth.EmailBackend")

    def complete_all(self, user):
        for lesson in self.course.ordered_lessons():
            LessonProgress.objects.get_or_create(user=user, lesson=lesson)

    def answers(self, n_correct):
        """Réponses POST avec n_correct bonnes réponses (les autres fausses)."""
        data = {}
        for i, q in enumerate(self.course.questions.order_by("position", "id")):
            good = q.choices.get(is_correct=True)
            bad = q.choices.filter(is_correct=False).first()
            data[f"q{q.id}"] = str(good.id if i < n_correct else bad.id)
        return data

    def take_exam(self, n_correct):
        r = self.client.get(reverse("exam_take", args=[SLUG]))
        self.assertEqual(r.status_code, 200)
        attempt = ExamAttempt.objects.filter(user=r.wsgi_request.user, submitted_at__isnull=True).latest("number")
        data = self.answers(n_correct)
        data["attempt"] = attempt.pk
        r = self.client.post(reverse("exam_take", args=[SLUG]), data)
        self.assertRedirects(r, reverse("exam_result", args=[SLUG, attempt.number]))
        attempt.refresh_from_db()
        return attempt

    def activate_offer(self):
        offer = RewardOffer.objects.get(course=self.course)
        offer.duration_label = "1 mois"
        offer.delivery_method = "Lien cadeau officiel Claude, à activer sur claude.ai/gift/redeem."
        offer.delivery_delay = "sous 7 jours ouvrés"
        offer.funding_confirmed = True
        offer.is_active = True
        offer.full_clean()
        offer.save()
        return offer


class P1InscriptionConnexion(Base):
    def test_inscription_connexion_acces(self):
        r = self.client.post(reverse("signup"), {
            "full_name": "Youssef Alaoui", "email": "Youssef@Example.ma",
            "password1": PASSWORD, "password2": PASSWORD,
        })
        self.assertRedirects(r, reverse("dashboard"))
        self.assertEqual(len(mail.outbox), 1, "e-mail de vérification envoyé")
        self.client.post(reverse("logout"))
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 302)
        # Connexion par e-mail, insensible à la casse
        r = self.client.post(reverse("login"), {"username": "youssef@example.ma", "password": PASSWORD})
        self.assertRedirects(r, reverse("dashboard"))
        self.assertContains(self.client.get(reverse("dashboard")), "Youssef Alaoui")

    def test_mauvais_mot_de_passe(self):
        self.make_user()
        r = self.client.post(reverse("login"), {"username": "lina@example.ma", "password": "faux"})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_lecon_exige_connexion(self):
        lesson = self.course.ordered_lessons()[0]
        r = self.client.get(lesson.get_absolute_url())
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("login"), r["Location"])

    def test_reinitialisation_mot_de_passe(self):
        self.make_user()
        r = self.client.post(reverse("password_reset"), {"email": "lina@example.ma"})
        self.assertRedirects(r, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/mot-de-passe/nouveau/", mail.outbox[0].body)

    def test_verification_email(self):
        user = self.make_user(verified=False)
        self.login(user)
        self.client.post(reverse("resend_verification"))
        link = next(l for l in mail.outbox[-1].body.split() if "/confirmer-email/" in l)
        self.client.get(link.replace("http://testserver", ""))
        user.profile.refresh_from_db()
        self.assertTrue(user.profile.email_verified)


class P2LeconsReprise(Base):
    def test_progression_deconnexion_reprise(self):
        user = self.make_user()
        self.login(user)
        lessons = self.course.ordered_lessons()
        r = self.client.post(reverse("enroll", args=[SLUG]))
        self.assertRedirects(r, lessons[0].get_absolute_url())
        page = self.client.get(lessons[0].get_absolute_url())
        self.assertContains(page, "À retenir")
        self.assertContains(page, "Marquer comme terminée")
        r = self.client.post(reverse("lesson_complete", args=[SLUG, lessons[0].slug]))
        self.assertRedirects(r, lessons[1].get_absolute_url())
        self.client.get(lessons[2].get_absolute_url())
        self.client.post(reverse("logout"))
        self.login(user)
        r = self.client.get(reverse("resume", args=[SLUG]))
        self.assertRedirects(r, lessons[2].get_absolute_url())
        self.assertEqual(services.course_progress(user, self.course)["done"], 1)
        self.assertContains(self.client.get(reverse("dashboard")), "1/8 leçons")


class P3DeblocageExamen(Base):
    def test_examen_verrouille_puis_debloque(self):
        user = self.make_user()
        self.login(user)
        services.enroll(user, self.course)
        r = self.client.get(reverse("exam_take", args=[SLUG]))
        self.assertRedirects(r, reverse("exam_intro", args=[SLUG]))
        self.assertFalse(ExamAttempt.objects.filter(user=user).exists())
        lessons = self.course.ordered_lessons()
        for lesson in lessons[:-1]:
            LessonProgress.objects.create(user=user, lesson=lesson)
        self.assertRedirects(self.client.get(reverse("exam_take", args=[SLUG])), reverse("exam_intro", args=[SLUG]))
        r = self.client.post(reverse("lesson_complete", args=[SLUG, lessons[-1].slug]))
        self.assertRedirects(r, reverse("exam_intro", args=[SLUG]))
        self.assertEqual(self.client.get(reverse("exam_take", args=[SLUG])).status_code, 200)

    def test_bonnes_reponses_absentes_avant_correction(self):
        user = self.make_user()
        self.login(user)
        self.complete_all(user)
        html = self.client.get(reverse("exam_take", args=[SLUG])).content.decode()
        self.assertNotIn("is_correct", html)
        self.assertNotIn("Une hallucination est une information", html)  # explication non divulguée


class P4ReussiteCertificat(Base):
    def test_reussite_et_pdf(self):
        user = self.make_user()
        self.login(user)
        self.complete_all(user)
        attempt = self.take_exam(8)
        self.assertTrue(attempt.passed)
        self.assertEqual(attempt.score20, Decimal("16"))
        r = self.client.get(reverse("exam_result", args=[SLUG, attempt.number]))
        self.assertContains(r, "16")
        self.assertContains(r, "Correction expliquée")
        # Confirmation du nom obligatoire
        r = self.client.post(reverse("certificate_claim", args=[SLUG]), {"full_name": "Lina Bennani"})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Certificate.objects.exists())
        r = self.client.post(reverse("certificate_claim", args=[SLUG]), {"full_name": "Lina Bennani", "confirm": "on"})
        cert = Certificate.objects.get(user=user)
        self.assertRedirects(r, reverse("certificate_ready", args=[cert.number]))
        self.assertTrue(cert.number.startswith("FI-"))
        self.assertTrue(cert.verify_url.startswith("https://academy.example.ma/verifier/"))
        pdf = self.client.get(reverse("certificate_download", args=[cert.number]))
        body = b"".join(pdf.streaming_content)
        self.assertEqual(pdf["Content-Type"], "application/pdf")
        self.assertTrue(body.startswith(b"%PDF"))
        # Re-téléchargement : même certificat, pas de doublon
        self.client.post(reverse("certificate_claim", args=[SLUG]), {"full_name": "Autre Nom", "confirm": "on"})
        self.assertEqual(Certificate.objects.filter(user=user).count(), 1)
        self.assertEqual(Certificate.objects.get(user=user).full_name, "Lina Bennani")

    def test_seuil_exact_14_sur_20(self):
        self.assertTrue(services.is_passing(7, 10, Decimal("70")))
        self.assertFalse(services.is_passing(6, 10, Decimal("70")))
        self.assertTrue(services.is_passing(14, 20, Decimal("70")))
        self.assertFalse(services.is_passing(2, 3, Decimal("66.67")))  # 66,666… % < 66,67 %

    def test_double_envoi_ne_recorrige_pas(self):
        user = self.make_user()
        self.login(user)
        self.complete_all(user)
        attempt = self.take_exam(10)
        data = self.answers(0)
        data["attempt"] = attempt.pk
        self.client.post(reverse("exam_take", args=[SLUG]), data)
        attempt.refresh_from_db()
        self.assertEqual(attempt.correct_answers, 10)
        self.assertEqual(ExamAttempt.objects.filter(user=user).count(), 1)


class P5EchecNouvelleTentative(Base):
    def test_echec_puis_reussite(self):
        user = self.make_user()
        self.login(user)
        self.complete_all(user)
        a1 = self.take_exam(6)
        self.assertFalse(a1.passed)
        r = self.client.get(reverse("exam_result", args=[SLUG, 1]))
        self.assertContains(r, "Leçons à revoir")
        self.assertContains(r, "Refaire l'examen")
        a2 = self.take_exam(7)
        self.assertEqual(a2.number, 2)
        self.assertTrue(a2.passed)
        # Un échec ultérieur ne supprime pas le certificat
        services.issue_certificate(user, self.course, "Lina Bennani")
        self.take_exam(2)
        self.assertEqual(Certificate.objects.filter(user=user).count(), 1)

    def test_limite_de_tentatives(self):
        self.course.max_attempts = 1
        self.course.save()
        user = self.make_user()
        self.login(user)
        self.complete_all(user)
        self.take_exam(3)
        r = self.client.get(reverse("exam_take", args=[SLUG]))
        self.assertRedirects(r, reverse("exam_intro", args=[SLUG]))


class P6CertificatRefuse(Base):
    def test_sans_reussite(self):
        user = self.make_user()
        self.login(user)
        self.complete_all(user)
        self.take_exam(5)
        r = self.client.get(reverse("certificate_claim", args=[SLUG]))
        self.assertRedirects(r, reverse("exam_intro", args=[SLUG]))
        r = self.client.post(reverse("certificate_claim", args=[SLUG]), {"full_name": "Lina Bennani", "confirm": "on"})
        self.assertFalse(Certificate.objects.exists())
        with self.assertRaises(services.CertificateNotAllowed):
            services.issue_certificate(user, self.course, "Lina Bennani")

    def test_url_directe_certificat_d_un_autre(self):
        owner = self.make_user()
        self.complete_all(owner)
        attempt = services.start_attempt(owner, self.course)
        good = {q.id: q.choices.get(is_correct=True).id for q in self.course.questions.all()}
        services.submit_attempt(attempt.pk, owner, good)
        cert, _ = services.issue_certificate(owner, self.course, "Lina Bennani")
        intruder = self.make_user("intrus@example.ma", "Intrus")
        self.login(intruder)
        self.assertEqual(self.client.get(reverse("certificate_download", args=[cert.number])).status_code, 404)
        self.assertEqual(self.client.get(reverse("certificate_ready", args=[cert.number])).status_code, 404)
        self.assertEqual(self.client.get(reverse("certificate_download", args=["FI-2026-00000000"])).status_code, 404)


class P7ProtectionAdminEtDonnees(Base):
    def test_admin_interdit_aux_apprenants(self):
        self.login(self.make_user())
        for name, args in [("staff_overview", []), ("staff_courses", []), ("staff_learners", []),
                           ("staff_results", []), ("staff_rewards", []), ("staff_settings", []),
                           ("staff_questions", [self.course.pk])]:
            self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 403, name)
        r = self.client.post(reverse("staff_course_status", args=[self.course.pk]), {"status": "archived"})
        self.assertEqual(r.status_code, 403)
        self.course.refresh_from_db()
        self.assertEqual(self.course.status, "published")

    def test_admin_anonyme_redirige(self):
        r = self.client.get(reverse("staff_overview"))
        self.assertEqual(r.status_code, 302)

    def test_resultat_d_un_autre(self):
        owner = self.make_user()
        self.login(owner)
        self.complete_all(owner)
        self.take_exam(4)
        self.client.post(reverse("logout"))
        self.login(self.make_user("autre@example.ma", "Autre"))
        self.assertEqual(self.client.get(reverse("exam_result", args=[SLUG, 1])).status_code, 404)
        self.assertNotContains(self.client.get(reverse("dashboard")), "Lina Bennani")

    def test_pages_admin_accessibles_au_staff(self):
        admin = self.make_user("admin@example.ma", "Admin", staff=True)
        self.login(admin)
        q = self.course.questions.first()
        lesson = self.course.ordered_lessons()[0]
        pages = [reverse("staff_overview"), reverse("staff_courses"), reverse("staff_course_new"),
                 reverse("staff_course_edit", args=[self.course.pk]), reverse("staff_course_content", args=[self.course.pk]),
                 reverse("staff_lesson_edit", args=[self.course.pk, lesson.pk]), reverse("staff_lesson_new", args=[self.course.pk]),
                 reverse("staff_questions", args=[self.course.pk]), reverse("staff_question_edit", args=[self.course.pk, q.pk]),
                 reverse("staff_question_new", args=[self.course.pk]), reverse("staff_learners"), reverse("staff_results"),
                 reverse("staff_certificates"), reverse("staff_settings"), reverse("staff_rewards"),
                 reverse("staff_reward_offer_edit", args=[RewardOffer.objects.get().pk])]
        for url in pages:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        pdf = self.client.get(reverse("staff_certificate_preview"))
        self.assertTrue(pdf.content.startswith(b"%PDF"))

    def test_edition_question_et_lecon(self):
        admin = self.make_user("admin@example.ma", "Admin", staff=True)
        self.login(admin)
        r = self.client.post(reverse("staff_question_new", args=[self.course.pk]), {
            "kind": "tf", "text": "L'IA remplace toujours la relecture.", "explanation": "Non.",
            "related_lesson": "", "correct": "1",
            **{f"c{i}-text": "" for i in range(4)},
        })
        self.assertRedirects(r, reverse("staff_questions", args=[self.course.pk]))
        q = Question.objects.get(text__startswith="L'IA remplace")
        self.assertEqual(list(q.choices.values_list("text", "is_correct")), [("Vrai", False), ("Faux", True)])
        lesson = self.course.ordered_lessons()[0]
        r = self.client.post(reverse("staff_lesson_edit", args=[self.course.pk, lesson.pk]), {
            "module": lesson.module_id, "title": lesson.title, "reading_minutes": 5,
            "content": '<p>Texte</p><script>alert(1)</script><div class="exemple">Ex</div>', "key_takeaway": "<p>Ok</p>",
        })
        lesson.refresh_from_db()
        self.assertNotIn("<script>", lesson.content)
        self.assertIn('class="exemple"', lesson.content)


class P8Verification(Base):
    def test_lien_de_verification(self):
        user = self.make_user()
        self.complete_all(user)
        attempt = services.start_attempt(user, self.course)
        services.submit_attempt(attempt.pk, user, {q.id: q.choices.get(is_correct=True).id for q in self.course.questions.all()})
        cert, _ = services.issue_certificate(user, self.course, "Lina Bennani")
        path = cert.verify_url.replace("https://academy.example.ma", "")
        r = self.client.get(path)  # anonyme, comme après un scan du QR code
        self.assertContains(r, cert.number)
        self.assertContains(r, "Lina B.")
        self.assertNotContains(r, "Bennani")
        self.assertNotContains(r, user.email)
        self.assertEqual(self.client.get(reverse("certificate_verify", args=["inconnu"])).status_code, 404)
        cert.status = Certificate.Status.REVOKED
        cert.save()
        self.assertContains(self.client.get(path), "révoqué")


class RecompenseClaudePro(Base):
    def setUp(self):
        self.offer = self.activate_offer()

    def test_offre_brouillon_non_affichee(self):
        self.offer.is_active = False
        self.offer.save()
        self.assertNotContains(self.client.get(self.course.get_absolute_url()), "Claude Pro offert")
        self.offer.is_active = True
        self.offer.funding_confirmed = False
        self.offer.save()
        self.assertIsNone(services.live_offer_for(self.course))

    def test_banniere_publique(self):
        r = self.client.get(self.course.get_absolute_url())
        self.assertContains(r, "Terminez la formation et obtenez 100 % à l'examen final pour recevoir 1 mois de Claude Pro offert par Flux Intelligent.")

    def test_moins_de_100_pas_de_recompense(self):
        user = self.make_user()
        self.login(user)
        self.complete_all(user)
        attempt = self.take_exam(9)
        self.assertTrue(attempt.passed)
        self.assertFalse(RewardClaim.objects.exists())
        self.assertNotContains(self.client.get(reverse("exam_result", args=[SLUG, 1])), "Réclamer mon abonnement Claude Pro")

    def test_100_eligible_sans_doublon_et_suivi(self):
        user = self.make_user()
        self.login(user)
        self.complete_all(user)
        self.take_exam(10)
        r = self.client.get(reverse("exam_result", args=[SLUG, 1]))
        self.assertContains(r, "Félicitations ! Vous avez obtenu 20/20.")
        self.assertContains(r, "Télécharger mon certificat")
        self.assertContains(r, "Réclamer mon abonnement Claude Pro")
        claim = RewardClaim.objects.get(user=user)
        self.assertEqual(claim.status, "eligible")
        # Double clic / renvois : une seule demande
        data = {"full_name": "Lina Bennani", "email": "lina@example.ma", "confirm": "on"}
        r1 = self.client.post(reverse("reward_claim", args=[claim.pk]), data, follow=True)
        self.assertContains(r1, "Votre demande est enregistrée. Retrouvez son avancement dans votre espace personnel.")
        first_requested_at = RewardClaim.objects.get().requested_at
        self.client.post(reverse("reward_claim", args=[claim.pk]), data)
        self.assertEqual(RewardClaim.objects.count(), 1)
        self.assertEqual(RewardClaim.objects.get().requested_at, first_requested_at)
        # Nouvelle tentative à 100 % : pas de seconde récompense
        self.take_exam(10)
        self.assertEqual(RewardClaim.objects.count(), 1)
        # Suivi après reconnexion
        self.client.post(reverse("logout"))
        self.login(user)
        self.assertContains(self.client.get(reverse("dashboard")), "Demande enregistrée")
        # Certificat téléchargeable pendant le traitement
        services.issue_certificate(user, self.course, "Lina Bennani")
        cert = Certificate.objects.get(user=user)
        self.assertEqual(self.client.get(reverse("certificate_download", args=[cert.number])).status_code, 200)
        self.assertContains(self.client.get(reverse("reward_status", args=[claim.pk])), "Télécharger mon certificat")

    def test_email_non_verifie_puis_rattrapage(self):
        user = self.make_user(verified=False)
        self.login(user)
        self.complete_all(user)
        self.take_exam(10)
        self.assertFalse(RewardClaim.objects.exists())
        self.assertContains(self.client.get(reverse("exam_result", args=[SLUG, 1])), "adresse e-mail vérifiée")
        user.profile.email_verified_at = timezone.now()
        user.profile.save()
        self.assertIsNotNone(services.eligible_claim_for(user, self.course))
        self.assertEqual(RewardClaim.objects.count(), 1)

    def test_pas_d_acces_a_la_recompense_d_un_autre(self):
        owner = self.make_user()
        self.complete_all(owner)
        attempt = services.start_attempt(owner, self.course)
        services.submit_attempt(attempt.pk, owner, {q.id: q.choices.get(is_correct=True).id for q in self.course.questions.all()})
        claim = RewardClaim.objects.get(user=owner)
        claim.gift_link = "https://claude.ai/gift/SECRET-LINK"
        claim.save()
        self.login(self.make_user("intrus@example.ma", "Intrus"))
        self.assertEqual(self.client.get(reverse("reward_status", args=[claim.pk])).status_code, 404)
        r = self.client.post(reverse("reward_claim", args=[claim.pk]), {"full_name": "Intrus", "email": "intrus@example.ma", "confirm": "on"})
        self.assertEqual(r.status_code, 404)
        claim.refresh_from_db()
        self.assertEqual(claim.status, "eligible")

    def test_admin_remis_tracable(self):
        owner = self.make_user()
        self.complete_all(owner)
        attempt = services.start_attempt(owner, self.course)
        services.submit_attempt(attempt.pk, owner, {q.id: q.choices.get(is_correct=True).id for q in self.course.questions.all()})
        claim = RewardClaim.objects.get(user=owner)
        admin = self.make_user("admin@example.ma", "Admin", staff=True)
        self.login(admin)
        url = reverse("staff_reward_claim", args=[claim.pk])
        r = self.client.post(url, {"status": "delivered", "gift_link": "", "delivery_method_used": "", "delivery_reference": "", "admin_notes": ""})
        self.assertEqual(r.status_code, 200)  # refusé : remise non traçable
        claim.refresh_from_db()
        self.assertNotEqual(claim.status, "delivered")
        r = self.client.post(url, {"status": "delivered", "gift_link": "https://claude.ai/gift/ABC123", "delivery_method_used": "",
                                   "delivery_reference": "Commande cadeau n° 4521", "admin_notes": ""})
        self.assertRedirects(r, reverse("staff_rewards"))
        claim.refresh_from_db()
        self.assertEqual(claim.status, "delivered")
        self.assertIsNotNone(claim.delivered_at)
        # Le bénéficiaire voit son lien
        self.login(owner)
        self.assertContains(self.client.get(reverse("reward_status", args=[claim.pk])), "https://claude.ai/gift/ABC123")
