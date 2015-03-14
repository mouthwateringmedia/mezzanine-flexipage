from django.template.loader import render_to_string

from flexipage.models import FlexiPage
from flexipage.utils import get_flexi_template_location
from flexipage.page_processors import get_flexi_variables_context, get_flexi_forms_context

from mezzanine import template

register = template.Library()


@register.simple_tag(takes_context=True)
def flexipage_by_template(context, template_name):
    """
    Includes a template using the FlexiPage object to generate
    the context variables. Only templates that are listed in
    settings.FLEXI_TEMPLATES will be usable.

    Before you can use the template with this tag, you must create
    a FlexiPage in Django admin and choose the template.

    Usage:
        {% load flexipage_tags %}
        {% flexipage_by_template 'template_name.html' %}
    """
    try:
        page = FlexiPage.objects.get(template_name=template_name)
    except FlexiPage.DoesNotExist:
        raise FlexiPage.DoesNotExist('FlexiPage for template_name={!r}'.format(template_name))
    if 'request' not in context:
        raise ValueError('flexipage_by_template expects the request in the context')
    request = context['request']
    # Get the template from the flexipage model, or raise exception.
    template_path = get_flexi_template_location(page.template_name)
    if request.user.is_staff:
        # Calling save ensures that the FlexiContent models are created
        page.flexipage.save()

    variables_context = get_flexi_variables_context(page)
    forms_context = get_flexi_forms_context(page)
    new_context = dict(variables_context.items() + forms_context.items())
    new_context['request'] = request
    new_context['is_flexipage_included'] = True
    return render_to_string(template_name=template_path, dictionary=new_context)
