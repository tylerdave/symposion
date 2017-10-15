from django import template
from django.template.defaultfilters import linebreaks, urlize

from symposion.conference.models import current_conference
from symposion.schedule import models

from itertools import chain

register = template.Library()


@register.assignment_tag
def speakers(slug=None):
    """
    {% speakers as speakers %}
    """
    speaker_iters = list(i.speakers() for i in models.Presentation.objects.all())
    speakers = chain(*speaker_iters)
    speakers = list(speakers)

    return speakers
