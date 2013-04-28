'''Filter to create a range for forloops.'''

from django.template import Library

register = Library()


@register.filter
def get_range(value):
    """ Filter - returns a list containing range made from the
    given value.
    Usage (in template):

    <ul>{% for i in 3|get_range %}
        <li>{{ i }}. Do something</li>
        {% endfor %}
    </ul>

    Results with the HTML:
    <ul>
        <li>0. Do something</li>
        <li>1. Do something</li>
        <li>2. Do something</li>
    </ul>

    Instead of 3 one may use a variable set in the views."""
    return range(value)

register.filter('get_range', get_range)


@register.filter
def nth(value, arg):
    """Returns the nth item from a list."""
    return value[arg]

register.filter('nth', nth)
