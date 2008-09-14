#!/usr/bin/env python
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django_templatecomponents import templatecomponents

class Command(BaseCommand):
    def handle(self, **options):
        for group, extension in templatecomponents.all().available():

            filename = '%s.%s' % (group, extension)
            print "Generating", filename

            handle = open(os.path.join(settings.MEDIA_ROOT, filename), 'w')
            handle.write(templatecomponents.all().filter(extension).group(group))
            handle.close()
