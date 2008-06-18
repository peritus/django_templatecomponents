from django.conf.urls.defaults import *
from django.conf import settings
from django_templatecomponents.views import css, javascript

# In your urls.py use
#
# from django.conf import settings
# if settings.DEBUG:
#     urlpatterns += patterns('', ('', include('django_templatecomponents.urls')))

urlpatterns = patterns('',
  (r'^%s(?P<group>.*).css$' % settings.MEDIA_URL[1:], css),
  (r'^%s(?P<group>.*).js$' % settings.MEDIA_URL[1:], javascript),
)
