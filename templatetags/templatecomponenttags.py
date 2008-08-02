#!/usr/bin/env python

# Template functionality

from django.template import Library, Node
from django_templatecomponents import templatecomponents

register = Library()

def clientsidemagic(parser, token):
    tag, options = token.split_contents()[0], token.split_contents()[1:]
    inner = parser.parse(('end' + tag, "end" + token.contents))
    parser.delete_first_token()

    if tag == 'javascript':
        return MagicJavascriptNode(inner, options)
    elif tag == 'css':
        return MagicCSSNode(inner, options)
    assert False, "don't reach this"

clientsidemagic = register.tag('javascript', clientsidemagic)
clientsidemagic = register.tag('css', clientsidemagic)

class MagicClientNode(Node):
    def __init__(self, inner, options):
        self.inner = inner
        self.options = options

    def render(self, context):
        if 'inline' in self.options:
            content = self.compress(self.inner.render(context))
            return self.INLINE_FRAMING % content

        # act as comment node
        return ''

class MagicCSSNode(MagicClientNode):
    compress = lambda _, s: templatecomponents.compress_css(s)
    INLINE_FRAMING = '<style type="text/css">%s</</style>'

class MagicJavascriptNode(MagicClientNode):
    compress = lambda _, s: templatecomponents.compress_js(s)
    INLINE_FRAMING = '<script type="text/javascript">%s</script>'
