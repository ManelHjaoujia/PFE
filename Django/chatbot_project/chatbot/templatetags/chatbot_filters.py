from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.filter
def make_links_clickable(text):
    """
    Convertit les URLs et les balises HTML de liens en liens cliquables
    """
    if not text:
        return text

    # Échapper d'abord le texte pour éviter les injections XSS
    from django.utils.html import escape
    text = escape(text)

    # Regex améliorée pour détecter les URLs en excluant la ponctuation finale
    url_pattern = r'(https?://[^\s<>"{}|\\^`\[\]]+?)(?=[)\].,;:!?]*(?:\s|$))'

    # Remplacer les URLs par des liens cliquables
    text = re.sub(url_pattern,
                  r'<a href="\1" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">\1</a>',
                  text)

    # Si le texte contient déjà des balises <a> échappées, les restaurer
    text = re.sub(r'&lt;a\s+href=&quot;([^&]+?)&quot;[^&]*&gt;([^&]+)&lt;/a&gt;',
                  r'<a href="\1" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">\2</a>',
                  text)

    return mark_safe(text)


@register.filter
def safe_html(text):
    """
    Permet l'affichage sécurisé du HTML pour les liens uniquement
    """
    if not text:
        return text

    # Autoriser seulement les balises <a> avec href
    allowed_pattern = r'<a\s+href=["\']([^"\']*)["\'][^>]*>([^<]*)</a>'

    # Échapper tout le texte d'abord
    from django.utils.html import escape
    escaped_text = escape(text)

    # Puis restaurer seulement les liens valides
    def replace_link(match):
        href = match.group(1)
        link_text = match.group(2)
        return f'<a href="{href}" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">{link_text}</a>'

    # Chercher les liens dans le texte original (non échappé)
    links = re.findall(allowed_pattern, text)
    result = escaped_text

    for href, link_text in links:
        escaped_link = escape(f'<a href="{href}">{link_text}</a>')
        safe_link = f'<a href="{href}" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">{link_text}</a>'
        result = result.replace(escaped_link, safe_link)

    return mark_safe(result)
