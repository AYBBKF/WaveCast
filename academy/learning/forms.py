from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm

from .models import Choice, Course, Lesson, Module, Question, RewardClaim, RewardOffer, SiteSettings
from .sanitize import clean_html

User = get_user_model()


class StyledMixin:
    def _style(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                continue
            widget.attrs.setdefault("class", "input")


# ------------------------------------------------------------------ Comptes
class SignupForm(StyledMixin, forms.Form):
    full_name = forms.CharField(label="Nom complet", max_length=150, help_text="Tel qu'il apparaîtra sur votre certificat.")
    email = forms.EmailField(label="Adresse e-mail")
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput, help_text="10 caractères minimum.")
    password2 = forms.CharField(label="Confirmation du mot de passe", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()
        self.fields["email"].widget.attrs["autocomplete"] = "email"
        self.fields["password1"].widget.attrs["autocomplete"] = "new-password"
        self.fields["password2"].widget.attrs["autocomplete"] = "new-password"

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un compte existe déjà avec cette adresse. Connectez-vous ou réinitialisez votre mot de passe.")
        return email

    def clean(self):
        data = super().clean()
        p1, p2 = data.get("password1"), data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Les deux mots de passe ne correspondent pas.")
        if p1:
            candidate = User(username=data.get("email", ""), email=data.get("email", ""), first_name=data.get("full_name", ""))
            try:
                password_validation.validate_password(p1, candidate)
            except forms.ValidationError as exc:
                self.add_error("password1", exc)
        return data

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(username=data["email"], email=data["email"], password=data["password1"])
        user.profile.full_name = data["full_name"].strip()
        user.profile.save()
        return user


class LoginForm(StyledMixin, AuthenticationForm):
    username = forms.EmailField(label="Adresse e-mail", widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email"}))

    error_messages = {
        "invalid_login": "Adresse e-mail ou mot de passe incorrect.",
        "inactive": "Ce compte est désactivé.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class ProfileForm(StyledMixin, forms.Form):
    full_name = forms.CharField(label="Nom complet", max_length=150)
    email = forms.EmailField(label="Adresse e-mail")

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self._style()

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Cette adresse est déjà utilisée par un autre compte.")
        return email


class ConfirmNameForm(StyledMixin, forms.Form):
    full_name = forms.CharField(label="Nom complet à inscrire sur le certificat", max_length=150, min_length=3)
    confirm = forms.BooleanField(
        label="Je confirme que ce nom est correct. Il ne pourra plus être modifié sur ce certificat.", required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class RewardRequestForm(StyledMixin, forms.Form):
    full_name = forms.CharField(label="Nom complet", max_length=150, min_length=3)
    email = forms.EmailField(label="Adresse e-mail de remise", help_text="L'adresse associée (ou à associer) à votre compte Claude.")
    confirm = forms.BooleanField(
        label="Je confirme ces informations. Flux Intelligent ne me demandera jamais le mot de passe de mon compte Claude.",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


# ------------------------------------------------------------ Administration
class CourseForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "title", "summary", "description", "cover", "objectives", "level", "duration",
            "pass_threshold", "max_attempts", "is_demo", "position",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "objectives": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class ModuleForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Module
        fields = ["title"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class LessonForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["module", "title", "reading_minutes", "content", "key_takeaway"]
        widgets = {
            "content": forms.HiddenInput(attrs={"data-editor": "content"}),
            "key_takeaway": forms.HiddenInput(attrs={"data-editor": "key_takeaway"}),
        }

    def __init__(self, *args, course=None, **kwargs):
        super().__init__(*args, **kwargs)
        if course is not None:
            self.fields["module"].queryset = course.modules.all()
        self._style()

    def clean_content(self):
        return clean_html(self.cleaned_data.get("content", ""))

    def clean_key_takeaway(self):
        return clean_html(self.cleaned_data.get("key_takeaway", ""))


class QuestionForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Question
        fields = ["kind", "text", "related_lesson", "explanation"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3}),
            "explanation": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, course=None, **kwargs):
        super().__init__(*args, **kwargs)
        if course is not None:
            self.fields["related_lesson"].queryset = Lesson.objects.filter(module__course=course).order_by(
                "module__position", "position"
            )
        self.fields["related_lesson"].required = False
        self._style()


class ChoiceForm(forms.Form):
    text = forms.CharField(label="Réponse", max_length=400, required=False, widget=forms.TextInput(attrs={"class": "input"}))


class SiteSettingsForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            "platform_name", "organization_name", "primary_color", "accent_color", "logo",
            "certificate_signature", "certificate_signatory", "certificate_signatory_title",
            "certificate_text", "support_email",
        ]
        widgets = {
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "accent_color": forms.TextInput(attrs={"type": "color"}),
            "certificate_text": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class RewardOfferForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = RewardOffer
        fields = ["course", "duration_label", "delivery_method", "delivery_delay", "funding_confirmed", "is_active"]
        widgets = {"delivery_method": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class RewardClaimAdminForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = RewardClaim
        fields = ["status", "gift_link", "delivery_method_used", "delivery_reference", "admin_notes"]
        widgets = {"admin_notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()

    def clean(self):
        data = super().clean()
        if data.get("status") == RewardClaim.Status.DELIVERED:
            if not (data.get("gift_link") or data.get("delivery_method_used")):
                raise forms.ValidationError(
                    "Pour passer au statut « Remis », renseignez le lien cadeau officiel ou la modalité de remise utilisée."
                )
            if not data.get("delivery_reference"):
                raise forms.ValidationError(
                    "Pour passer au statut « Remis », renseignez une référence de livraison traçable."
                )
        return data
