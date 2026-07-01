from django import template

register = template.Library()


@register.filter(name='split')
def split(value, arg):
    return value.split(arg)


@register.filter(name='trim')
def trim(value):
    return value.strip()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    for kwarg, value in kwargs.items():
        if value == '':
            if kwarg in query:
                del query[kwarg]
        else:
            query[kwarg] = value
    return query.urlencode()
