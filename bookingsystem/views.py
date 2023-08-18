from django.shortcuts import render

from django.http import HttpResponse
from django.utils.translation import gettext as _, get_language, activate, gettext


def index(request):
    # translation = translate(language='fr')
    # return HttpResponse(translation)
    return render(request, 'index.html')


def translate(language):
    current_language = get_language()
    try:
        activate(language)
        text = gettext('hello')
    finally:
        activate(current_language)
    return text

