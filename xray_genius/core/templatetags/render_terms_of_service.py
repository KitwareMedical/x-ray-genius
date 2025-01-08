from pathlib import Path

from django import template
import markdown

register = template.Library()


@register.simple_tag
def render_terms_of_service() -> str:
    tos_md = Path(__file__).parent.parent / 'templates' / 'terms_of_service.md'
    return markdown.markdown(tos_md.read_text())
