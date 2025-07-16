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
