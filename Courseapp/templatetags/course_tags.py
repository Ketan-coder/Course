# course_tags.py
from django import template

register = template.Library()

@register.filter
def has_completed_all_lessons(section, user):
    lessons = section.lesson.all()
    for lesson in lessons:
        if user not in lesson.completed_by_users.all():
            return False
    return True

@register.filter
def is_dark_mode(request):
    # Check if 'request' is a valid request object and has a user attribute
    # and if the user is authenticated before accessing user.profile
    if not hasattr(request, 'user') or not request.user:
        return False
    if request.user.is_authenticated:
        return hasattr(request.user, 'profile') and hasattr(request.user.profile, 'isDarkTheme') and request.user.profile.isDarkTheme
    return False

@register.filter
def filter_by_section(queryset, section_id):
    """
    Template filter to filter a queryset of lessons based on a section_id.

    Usage in template:
        {{ lessons|filter_by_section:section_id }}

    Args:
        queryset (QuerySet): Queryset of lessons.
        section_id (int): ID of the section to filter by.

    Returns:
        QuerySet: Filtered queryset of lessons.
    """
    return queryset.filter(section__id=section_id)