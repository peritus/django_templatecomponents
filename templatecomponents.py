#!/usr/bin/env python

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.template import Lexer, Parser, NodeList, TOKEN_TEXT, TOKEN_BLOCK, TOKEN_VAR
from django.template.context import Context
from django.template.loader import render_to_string
from django.template.loaders.filesystem import load_template_source
from django.utils.encoding import smart_unicode
from os.path import exists, getmtime
from popen2 import popen2
from sha import sha
import os
import re

__VERSION__ = 0, 0, 3

_hash = lambda s: sha(s.encode("utf-8")).digest()

BLOCKS = {}

TEMPLATECOMPONENTS_CONTEXT = Context(dict_={
    'settings': settings,
})

class TemplateComponentBucket(list):
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        self.sort(lambda x, y: y.priority - x.priority)
        return "\n".join(str(b) for b in self)

    def available(self):
        sofar = set()
        for block in self.without_inline():
            for group in block.groups:
                extension = block.blocktag
                if extension == 'javascript':
                    extension = 'js'
                sofar.add((group, extension))

        return list(sofar)

    def without_inline(self):
        return TemplateComponentBucket(
          block for block in self if 'inline' not in block.groups
        )

    def filter(self, filter_for):
        assert filter_for in TemplateComponentBlock.BLOCKTAGS


        if filter_for == 'js':
            # backwards compatibility
            filter_for = 'js', 'javascript'
        else:
            filter_for = (filter_for, )

        return TemplateComponentBucket(
          block for block in self if block.blocktag in filter_for
        )

    def group(self, group):
        if group == None:
            return TemplateComponentBucket(
              block for block in self if len(block.groups) == 0
            )

        return TemplateComponentBucket(
          block for block in self if group in block.groups
        )

class TemplateComponentBlock:

    BLOCKTAGS = 'css', 'js', 'javascript'
    ENDBLOCKTAGS = tuple(('end%s' % t) for t in BLOCKTAGS)

    def __init__(self, text, blocktag, groups=[], priority=0, origin=''):
        self.text = text.strip()
        self.blocktag = blocktag
        self.priority = priority
        self.origin = origin

        if 'inline' in groups and len(groups) > 1:
            raise ImproperlyConfigured, (
              "Error in %s: If a template component block has "
              "group inline, it can't have other groups.") % self.origin

        self.groups = groups

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        origin = ''
        if self.origin:
            origin = " from template '%s'" % self.origin

        priority = ''
        if self.priority:
            priority = ' with priority %d' % self.priority

        groups = ''
        if self.groups:
            groups = ' with groups ' + ', '.join(self.groups)

        return "/* extracted %s%s%s%s */\n%s" % (
          self.blocktag, origin, priority, groups, self.text
        )

    @classmethod
    def _parse_parameters(_, parameters):
        blocktag = parameters[0]
        parameters = parameters[1:]
        priority = 0
        groups = []
        for p in parameters:
            try:
                priority = int(p)
            except ValueError:
                groups.append(p)

        return {
          'priority': priority,
          'groups': groups,
          'blocktag': blocktag,
        }

    @classmethod
    def from_template(cls, templatepath):
        template_string, _ = load_template_source(templatepath)

        # Cache to speed things up.
        hash = _hash("_".join([templatepath, template_string]))
        if hash in BLOCKS:
            return BLOCKS[hash]

        try:
            return cls.from_string(template_string, origin=templatepath)
        except UnicodeDecodeError:
            return "/* could not load %s as a template */\n" % templatepath

    @classmethod
    def from_string(cls, template_soup, origin=''):
        result = TemplateComponentBucket()

        within = None
        node_bucket = NodeList()

        for m in Lexer(template_soup, origin).tokenize():
            attributes = m.split_contents()
            if not attributes:
                continue

            if attributes[0] in cls.BLOCKTAGS:
                prop = cls._parse_parameters(attributes)
                within = attributes[0]
                node_bucket = NodeList()
            elif attributes[0] in cls.ENDBLOCKTAGS:
                prop['blocktag'] = within
                within = None
                rendered_inner = Parser(node_bucket).parse().render(TEMPLATECOMPONENTS_CONTEXT)
                result.append(TemplateComponentBlock(rendered_inner, origin=origin, **prop))
            elif within:
                node_bucket.append(m)

        return result

def all():
    pile = TemplateComponentBucket()
    for template in all_templates():
        for block in TemplateComponentBlock.from_template(template):
            pile.append(block)

    additional = getattr(settings, 'TEMPLATECOMPONENTS_ADDITIONAL', {})

    for path, parameters in additional.items():
        if not os.path.exists(path):
            raise ImproperlyConfigured, "%s was not found, but specified in settings.TEMPLATECOMPONENTS_ADDITIONAL" % path
        block = TemplateComponentBlock(open(path).read(), origin=path, **TemplateComponentBlock._parse_parameters(parameters.split(" ")))
        pile.append(block)

    return pile


EXCLUDE_PATHS = '.*\.svn*', '.*\.*\.swp$', '.*.~$', '.*\.git*', '.*\.bak$', '.*\.backup$', '.*\.gitignore$'
def all_templates():
    all = []

    if 'django.template.loaders.filesystem.load_template_source' in settings.TEMPLATE_LOADERS:
        for templatedir in settings.TEMPLATE_DIRS:
            for dirname, subdirs, regular in os.walk(templatedir):
                for filename in regular:
                    if any([re.match(exclude, filename) for exclude in EXCLUDE_PATHS]):
                        continue
                    name = (dirname + "/" + filename)[len(templatedir)+1:]
                    all.append(name)
    if 'django.template.loaders.app_directories.load_template_source' in settings.TEMPLATE_LOADERS:
        pass # FIXME: implement

    all.reverse()
    return all
