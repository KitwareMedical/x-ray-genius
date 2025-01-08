from pathlib import Path

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import SafeString
import markdown

register = template.Library()


@register.filter
@stringfilter
def render_markdown_file(file_path: SafeString) -> str:
    tos_md = Path(__file__).parent.parent / 'templates' / file_path.strip()
    return markdown.markdown(tos_md.read_text())
