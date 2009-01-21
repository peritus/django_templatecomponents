#!/usr/bin/env python
import os
from django.core.management.base import BaseCommand
from django.conf import settings
import templatecomponents
import templatecomponents.views

class Command(BaseCommand):
    def handle(self, **options):
        for group, extension in templatecomponents.all().available():
            filename = '%s.%s' % (group, extension)
            print "Generating %s" % filename
            handle = open(os.path.join(settings.MEDIA_ROOT, filename), 'w')
            handle.write(templatecomponents.views.generate_templatecomponents(None, filename).content)
            handle.close()
