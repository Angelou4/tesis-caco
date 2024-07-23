from django import template

register = template.Library()

@register.filter
def format_currency(value):
    try:
        value = int(value)
    except (ValueError, TypeError):
        return value

    if value == 0:
        return "0"

    return f"${value:,}".replace(",", ".")