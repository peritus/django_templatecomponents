#!/usr/bin/env python

from django.core.management.base import BaseCommand
from django.conf import settings
from django_templatecomponents import templatecomponents

class Command(BaseCommand):
    def handle(self, **options):
        for group, type in templatecomponents.all().available():
            filename = '%s.%s' % (group, type)
            if type == 'javascript':
                filename = filename[:-10] + 'js'

            print "Generating", filename
       
            handle = open(settings.MEDIA_ROOT + filename, 'w')
            handle.write(templatecomponents.all().filter(type).group(group).compress())
            handle.close()
