from django.conf import settings
from django.template import add_to_builtins

add_to_builtins(settings.SETTINGS_MODULE.split('.')[0] + '.django_templatecomponents.templatetags.templatecomponenttags')
