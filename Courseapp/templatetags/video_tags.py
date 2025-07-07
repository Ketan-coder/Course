import re
from django import template

register = template.Library()

@register.filter
def youtube_id(value):
    # Extracts ID from full YouTube URL
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', value)
    return match.group(1) if match else ''
