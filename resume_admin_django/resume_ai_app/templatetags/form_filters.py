from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    if hasattr(field, 'field') and field.errors:
        css_class += ' is-invalid'
    return field.as_widget(attrs={"class": css_class})