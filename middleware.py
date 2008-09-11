from django.http import HttpResponse, Http404
from django.views.static import serve
from mimetypes import guess_type

import templatecomponents

class TemplateComponentsServeMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func != serve:
            return None # not our call

        group, extension = view_kwargs['path'].rsplit(".", 1)

        if not extension in ('js', 'css'):
            return None # not our call

        try:
            serve(request, view_kwargs['path'], view_kwargs['document_root'])
            return None # ok, file exists, let django.views.static.serve do it's job
        except Http404:
            pass

        collected = str(templatecomponents.all().without_inline().filter(extension).group(group))

        if not collected:
            av = ", ".join(["%s.%s" % x for x in templatecomponents.all().available()])
            raise Http404("Template component not found. Available choices: %s" % av)

        return HttpResponse(collected, content_type=guess_type(view_kwargs['path'])[0])

