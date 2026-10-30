"""
Génération du certificat PDF (A4 paysage) avec ReportLab.

Le fichier est créé une seule fois, à la délivrance, puis conservé : un nouveau
téléchargement renvoie exactement le même document.
"""
import io
from pathlib import Path

import qrcode
from django.conf import settings
from django.utils import formats, timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas


def _hex(value, fallback="#673DE6"):
    try:
        return colors.HexColor(value or fallback)
    except Exception:
        return colors.HexColor(fallback)


def _image(field):
    try:
        if field and field.name and Path(field.path).exists():
            return ImageReader(field.path)
    except Exception:
        return None
    return None


def certificate_text(cert, site):
    template = site.certificate_text or ""
    try:
        return template.format(
            organisme=site.organization_name,
            nom=cert.full_name,
            formation=cert.course_title,
            note=cert.score20_display,
        )
    except (KeyError, IndexError, ValueError):
        return (
            f"{site.organization_name} atteste que {cert.full_name} a suivi la formation « {cert.course_title} » "
            f"et a réussi son évaluation finale avec une note de {cert.score20_display}/20."
        )


def build_pdf_bytes(cert, site):
    buf = io.BytesIO()
    width, height = landscape(A4)
    c = canvas.Canvas(buf, pagesize=landscape(A4))
    c.setTitle(f"Certificat {cert.number}")
    c.setAuthor(site.organization_name)
    c.setSubject(f"Certificat de réussite — {cert.course_title}")

    primary = _hex(site.primary_color)
    dark = _hex(site.accent_color, "#111014")
    soft = colors.HexColor("#F7F5FF")
    grey = colors.HexColor("#5E5B66")

    # Fond et cadres
    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, stroke=0, fill=1)
    c.setFillColor(soft)
    c.rect(12 * mm, 12 * mm, width - 24 * mm, height - 24 * mm, stroke=0, fill=1)
    c.setStrokeColor(primary)
    c.setLineWidth(2.2)
    c.rect(12 * mm, 12 * mm, width - 24 * mm, height - 24 * mm, stroke=1, fill=0)
    c.setLineWidth(0.6)
    c.rect(16 * mm, 16 * mm, width - 32 * mm, height - 32 * mm, stroke=1, fill=0)
    c.setFillColor(primary)
    c.rect(12 * mm, height - 20 * mm, width - 24 * mm, 8 * mm, stroke=0, fill=1)

    # Logo ou nom de l'organisme
    top = height - 34 * mm
    logo = _image(site.logo)
    if logo:
        iw, ih = logo.getSize()
        h = 18 * mm
        w = min(70 * mm, iw * h / ih)
        c.drawImage(logo, (width - w) / 2, top - h, width=w, height=h, mask="auto", preserveAspectRatio=True)
        y = top - h - 10 * mm
    else:
        c.setFillColor(dark)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width / 2, top - 8 * mm, site.organization_name.upper())
        y = top - 20 * mm

    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(width / 2, y, "Certificat de réussite")
    y -= 14 * mm

    c.setFillColor(grey)
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, y, "Ce certificat est décerné à")
    y -= 14 * mm

    c.setFillColor(dark)
    name_size = 30 if len(cert.full_name) <= 32 else 24
    c.setFont("Helvetica-Bold", name_size)
    c.drawCentredString(width / 2, y, cert.full_name)
    c.setStrokeColor(primary)
    c.setLineWidth(1)
    c.line(width / 2 - 85 * mm, y - 4 * mm, width / 2 + 85 * mm, y - 4 * mm)
    y -= 16 * mm

    style = ParagraphStyle(
        "body", fontName="Helvetica", fontSize=13, leading=19, alignment=TA_CENTER, textColor=dark
    )
    para = Paragraph(
        certificate_text(cert, site).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), style
    )
    pw = width - 90 * mm
    _, ph = para.wrap(pw, 40 * mm)
    para.drawOn(c, (width - pw) / 2, y - ph)
    y -= ph + 12 * mm

    # Bloc d'informations
    issued = timezone.localtime(cert.issued_at)
    info = [
        ("Date de réussite", formats.date_format(issued, "j F Y")),
        ("Note obtenue", f"{cert.score20_display}/20"),
        ("N° de certificat", cert.number),
    ]
    col_w = 62 * mm
    start_x = width / 2 - col_w * 1.5
    for i, (label, value) in enumerate(info):
        x = start_x + i * col_w + col_w / 2
        c.setFillColor(grey)
        c.setFont("Helvetica", 9.5)
        c.drawCentredString(x, y, label.upper())
        c.setFillColor(dark)
        c.setFont("Helvetica-Bold", 12.5)
        c.drawCentredString(x, y - 6 * mm, value)

    # Pied : émetteur, signature, QR code
    base_y = 26 * mm
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(28 * mm, base_y + 8 * mm, f"Délivré par {cert.issuer}")
    c.setFillColor(grey)
    c.setFont("Helvetica", 9)
    c.drawString(28 * mm, base_y + 2.5 * mm, site.platform_name)

    signature = _image(site.certificate_signature)
    sig_x = width / 2
    if signature:
        iw, ih = signature.getSize()
        h = 16 * mm
        w = min(55 * mm, iw * h / ih)
        c.drawImage(signature, sig_x - w / 2, base_y + 6 * mm, width=w, height=h, mask="auto", preserveAspectRatio=True)
    if signature or site.certificate_signatory:
        c.setStrokeColor(grey)
        c.setLineWidth(0.5)
        c.line(sig_x - 32 * mm, base_y + 5 * mm, sig_x + 32 * mm, base_y + 5 * mm)
        c.setFillColor(dark)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(sig_x, base_y, site.certificate_signatory or "")
        c.setFillColor(grey)
        c.setFont("Helvetica", 8.5)
        c.drawCentredString(sig_x, base_y - 4.5 * mm, site.certificate_signatory_title or "")

    qr = qrcode.QRCode(border=1, box_size=8, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(cert.verify_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qbuf = io.BytesIO()
    img.save(qbuf, format="PNG")
    qbuf.seek(0)
    qsize = 26 * mm
    qx = width - 28 * mm - qsize
    c.drawImage(ImageReader(qbuf), qx, base_y - 2 * mm, width=qsize, height=qsize)
    c.setFillColor(grey)
    c.setFont("Helvetica", 7.5)
    c.drawRightString(qx - 3 * mm, base_y + 12 * mm, "Vérifier ce certificat :")
    c.drawRightString(qx - 3 * mm, base_y + 8 * mm, cert.verify_url.split("://", 1)[-1][:70])

    c.showPage()
    c.save()
    return buf.getvalue()


def render_certificate_pdf(cert, site):
    """Écrit le PDF dans le stockage privé et renvoie son chemin relatif."""
    root = Path(settings.PRIVATE_ROOT) / "certificates"
    root.mkdir(parents=True, exist_ok=True)
    rel = f"certificates/{cert.number}-{cert.verify_id[:8]}.pdf"
    (Path(settings.PRIVATE_ROOT) / rel).write_bytes(build_pdf_bytes(cert, site))
    return rel
