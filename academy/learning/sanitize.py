"""Nettoyage du HTML saisi dans l'éditeur visuel : seules les balises de mise en forme sont conservées."""
import nh3

ALLOWED_TAGS = {
    "p", "br", "h2", "h3", "h4", "strong", "b", "em", "i", "u", "s", "ul", "ol", "li",
    "blockquote", "a", "img", "figure", "figcaption", "hr", "code", "pre", "table",
    "thead", "tbody", "tr", "th", "td", "div", "span", "mark",
}
ALLOWED_ATTRIBUTES = {
    "a": {"href", "title", "target"},
    "img": {"src", "alt", "title", "width", "height", "loading"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan", "scope"},
}
# « class » est géré par allowed_classes (liste blanche de classes), pas par les attributs.
ALLOWED_CLASSES = {"div": {"exemple", "astuce", "attention"}, "p": {"exemple", "astuce", "attention"}, "span": {"surligne"}}


def clean_html(value: str) -> str:
    return nh3.clean(
        value or "",
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes={"http", "https", "mailto"},
        link_rel="noopener noreferrer",
        set_tag_attribute_values={"img": {"loading": "lazy"}},
        allowed_classes=ALLOWED_CLASSES,
    )
