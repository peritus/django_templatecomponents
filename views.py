#!/usr/bin/env python

import templatecomponents
from django.http import HttpResponse, Http404

def generate_clientsidemagic_view(tag, content_type):
  def view(request, group='empty'):
    collected = templatecomponents.all().without_inline().filter(tag).group(group)

    if tag == 'js'
      collected = templatecomponents.compress_js(collected)
    elif tag == 'css':
      collected = templatecomponents.compress_css(collected)

    if len(collected) == 0:
      av = ", ".join(["%s.%s" % x for x in templatecomponents.all().available()])
      raise Http404("Template component not found. Available choices: %s" % av)
    return HttpResponse(collected, content_type=content_type)
  return view

javascript = generate_clientsidemagic_view('javascript', 'text/javascript')
css = generate_clientsidemagic_view('css', 'text/css')
