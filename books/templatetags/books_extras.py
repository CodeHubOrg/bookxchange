from django import template
from ..models import Book


register = template.Library()


@register.simple_tag
def countBooks():
    return Book.objects.count()
