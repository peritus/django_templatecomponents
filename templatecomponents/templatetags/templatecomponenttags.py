#!/usr/bin/env python

from django.template import Library, Node
from django.template.defaulttags import CommentNode
import templatecomponents

register = Library()

def templatecomponents_tag(parser, token):
    tag, options = token.split_contents()[0], token.split_contents()[1:]
    inner = parser.parse(('end' + tag, "end" + token.contents))
    parser.delete_first_token()

    return CommentNode()

templatecomponents_tag = register.tag('js', templatecomponents_tag)
templatecomponents_tag = register.tag('css', templatecomponents_tag)

# backwards compatiblity
templatecomponents_tag = register.tag('javascript', templatecomponents_tag)
