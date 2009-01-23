from django.http import HttpResponse, Http404
from django.views.static import serve
from mimetypes import guess_type

import templatecomponents

def generate(request, path):
    group, extension = path.rsplit(".", 1)

    collected = unicode(templatecomponents.all().without_inline().filter(extension).group(group))

    if not collected:
        av = ", ".join(["%s.%s" % x for x in templatecomponents.all().available()])
        raise Http404("templatecomponent '%s.%s' not found. Available choices: %s" % (group, extension, av,))

    return HttpResponse(collected, content_type=guess_type(path)[0])

# this is for backwards compatibility
generate_templatecomponents = generate

