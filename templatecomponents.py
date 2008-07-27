#!/usr/bin/env python

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.template import Lexer, TOKEN_TEXT, TOKEN_BLOCK, TOKEN_VAR
from django.template.loader import render_to_string
from django.template.loaders.filesystem import load_template_source
from django.utils.encoding import smart_unicode
from jsmin import jsmin
from os.path import exists, getmtime
from popen2 import popen2
from sha import sha
import os
import re

__VERSION__ = 0, 0, 2

_COMPRESS_JAVASCRIPT = getattr(settings, 'TEMPLATECOMPONENTS_COMPRESS_JAVASCRIPT', not settings.DEBUG)
_COMPRESS_CSS = getattr(settings, 'TEMPLATECOMPONENTS_COMPRESS_CSS', not settings.DEBUG)

compress_js = jsmin

try:
    _YUICOMPRESSOR_JAR = settings.TEMPLATECOMPONENTS_PATH_TO_YUICOMPRESSOR_JAR
    if not exists(_YUICOMPRESSOR_JAR):
        raise ImproperlyConfigured, _YUICOMPRESSOR_JAR + " not found."

    _YUICOMPRESSOR_OPTIONS = getattr(settings, 'TEMPLATECOMPONENTS_OPTIONS', '')

    def _compress_yui(string, type):
        cmdline = "java -jar %s --type %s %s" % (_YUICOMPRESSOR_JAR, type, _YUICOMPRESSOR_OPTIONS)
        readstream, writestream = popen2(cmdline)
        writestream.write(string)
        writestream.close()
        return readstream.read()

    compress_js = lambda s: _compress_yui(s, 'js')
    compress_css = lambda s: _compress_yui(s, 'css')

except AttributeError:
    if _COMPRESS_CSS:
        raise ImproperlyConfigured, (
          'To use css compression, you need to specify a full path to yuicompressor.jar '
          'using settings.TEMPLATECOMPONENTS_PATH_TO_YUICOMPRESSOR_JAR'
        )

if not _COMPRESS_CSS:
    compress_css = lambda s: s

if not _COMPRESS_JAVASCRIPT:
    compress_js = lambda s: s

_hash = lambda s: sha(s.encode("utf-8")).digest()

BLOCKS = {}

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
                sofar.add((group, block.blocktag))

        return list(sofar)

    def without_inline(self):
        return TemplateComponentBucket(
          block for block in self if 'inline' not in block.groups
        )

    def filter(self, type):
        assert type in TemplateComponentBlock.BLOCKTAGS
        return TemplateComponentBucket(
          block for block in self if block.blocktag == type
        )

    def group(self, group):
        if group == None:
            return TemplateComponentBucket(
              block for block in self if len(block.groups) == 0
            )

        return TemplateComponentBucket(
          block for block in self if group in block.groups
        )

    def compress(self):
        if len(self) == 0:
            return ''

        type = self[0].blocktag

        for b in self:
            assert b.blocktag == type, 'Must be of same type!'

        if type == 'javascript':
            return compress_js(str(self))
        elif type == 'css':
            return compress_css(str(self))

        assert False, 'never reach this'


class TemplateComponentBlock:

    BLOCKTAGS = 'css', 'javascript'

    def __init__(self, text, type, groups=[], priority=0, origin=''):
        self.text = text.strip()
        self.blocktag = type
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
        type = parameters[0]
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
          'type': type,
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

        l = Lexer(template_soup, origin)
        within = None
        for m in l.tokenize():
            if m.token_type == TOKEN_BLOCK:

                type = m.split_contents()[0]

                if type not in cls.BLOCKTAGS + tuple(('end' + t) for t in cls.BLOCKTAGS):
                    continue; # shortcicuit here

                prop = cls._parse_parameters(m.split_contents())

                if type in cls.BLOCKTAGS:
                    within = type
                elif type == 'end' + within:
                    within = None
            elif within:
                if m.token_type == TOKEN_TEXT:
                    result.append(TemplateComponentBlock(m.contents, origin=origin, **prop))
                elif m.token_type == TOKEN_VAR:
                    assert False, "Variable replacement in client side magic not yet supported"

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


EXCLUDE_PATHS = '.svn', '.*.swp$', '*.~$', '.git'
def all_templates():
    all = []

    if 'django.template.loaders.filesystem.load_template_source' in settings.TEMPLATE_LOADERS:
        for templatedir in settings.TEMPLATE_DIRS:
            for dirname, subdirs, regular in os.walk(templatedir):
                for filename in regular:
                    if filename.find(".svn") != -1:
                        continue
                    name = (dirname + "/" + filename)[len(templatedir)+1:]
                    all.append(name)
    if 'django.template.loaders.app_directories.load_template_source' in settings.TEMPLATE_LOADERS:
        pass # FIXME: implement

    all.reverse()
    return all
