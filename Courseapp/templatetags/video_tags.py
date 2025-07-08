# in templatetags/video_tags.py
import re
from django import template

register = template.Library()

@register.filter
def youtube_id(value):
    """
    Extracts the YouTube ID from a full URL.
    """
    regex = (r'(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|'
             r'youtu\.be/)([^"&?/ ]{11})')
    match = re.search(regex, value)
    if match:
        return match.group(1)
    return value  # fallback to original
