=========================
django-templatecomponents
=========================

:Author: `Filip Noetzel <http://filip.noetzel.co.uk/>`_
:Version: v0.03
:Web: http://j03.de/projects/django-templatecomponents/
:Git: ``git clone http://j03.de/git/django-templatecomponents.git/``
  ( `browse <http://j03.de/git/?p=django-templatecomponents.git>`_,
  also `on github <http://github.com/peritus/django-templatecomponents/>`_)
:Download: `django-templatecomponents.tar.gz <http://j03.de/git/?p=django-templatecomponents.git;a=snapshot;sf=tgz>`_

A `django <http://djangoproject.com/>`_ application that makes it easy to
organize your component source (JavaScript, CSS) right in your django templates
to make your website much faster.

Benefits
========

Keeps you organized
-------------------

Define your JavaScript and CSS source right beneath the HTML skeleton that it's
used on:
::

  {% css print %}
    a[href]:after{
      content: " [" attr(href) "] ";
    }
  {% endcss %}
  
  {% css screen print %}
    #clickme { font-weight: bold; }
  {% endcss %}
  
  {% javascript screen %}
    document.getElementById('clickme').onclick = function() {
      alert('Ugh! I have been clicked');
    }
  {% endjavascript %}
  
  <a id='clickme' href="/click/">Click me</a>

Serve your components from one file
-----------------------------------
(see also `rule #1 <http://stevesouders.com/hpws/rule-min-http.php>`_) 
Using the above example, all your ``javascript`` blocks from all your templates
would be available concatenated via ``{{ MEDIA_URL }}screen.js`` (e.g.
``http://www.example.com/static/screen.js``).

You can arrange your template component blocks in (multiple) groups, to access
them by different urls (Here, ``print.js`` will contain the concatenated
content of the first two blocks).

One can imagine groups for

* printing CSS
* screen CSS
* presentation CSS
* additional CSS and JavaScript for authenticated / paying users
* CSS for browers with enabled or disabled JavaScript
* CSS and JavaScript for mobile devices
* CSS and JavaScript for legacy browsers
* `Splitting the initial payload <http://www.stevesouders.com/blog/2008/05/14/split-the-initial-payload/>`_
* Splitting JavaScript in `25K-Slices for the iPhone <http://yuiblog.com/blog/2008/02/06/iphone-cacheability/>`_

Static file generation
----------------------

While you want your template components be processed on the fly while
developing, you can generate static files from your template components upon
each deployment:
::

  $ ./manage.py generate_templatecomponents
  Generating print.css
  Generating screen.css
  Generating screen.js

Priority based block dependency
-------------------------------

Some CSS Rules and JavaScript might depend on each other (Specific CSS rules
override basic CSS Rules; some of your JavaScript depends on your favorite ajax
library).

Each block can have a priority, the following example illustrates this:

::

  # template1.html
  {% javascript screen 5 %} x = x + 1; {% endjavascript %}

::

  # template2.html
  {% javascript screen 10 %} var x = 1; {% endjavascript %}

This would ensure, the javascript block from template2.html appears above the
one from template1.html:

::

  /* from 'template2.html' with priority 10 with groups screen */
  var x = 1;
  /* from 'template1.html' with priority 5 with groups screen */
  x = x + 1;

It is recommended to give a high priority for JavaScript libraries, a lower for
custom built library code and a very low priority for custom code snippets.

Including external libraries
----------------------------

You can easily include additional static files (like JavaScript libraries, CSS
frameworks, ..), by specifying them in your ``settings.py``:
::

  TEMPLATECOMPONENTS_ADDITIONAL = {
      os.path.join(MEDIA_ROOT, 'js/prototype.js'):     'javascript 10 script',
      os.path.join(MEDIA_ROOT, 'js/scriptaculous.js'): 'javascript 9 script',
      os.path.join(MEDIA_ROOT, 'js/effects.js'):       'javascript 8 script',
      # .. 
  }

This way, you can avoid putting third party code in your ``templates/``
directory and adding django template tags in the first and last line.

Installation 
============

* Clone the git repository or download the tarball (links on top of this page),
* Put the folder ``django_templatecomponents`` somewhere in your ``$PYTHONPATH`` (presumably your project folder, where your ``manage.py`` lives).
* Configure (see next section) and begin adapting your templates.

Adopt your development ``urls.py`` like this:

::

  if settings.DEBUG:
      urlpatterns += patterns('',
        (r'^media/(?P<path>.*.js)$', 'django_templatecomponents.views.generate_templatecomponents',),
        (r'^media/(?P<path>.*.css)$', 'django_templatecomponents.views.generate_templatecomponents',),

        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

Syntax highlighting in vim
--------------------------
To get the syntax highlighting for the (now embedded) css and javascript in
vim, create a file at ``~/.vim/after/syntax/htmldjango.vim`` with the following
contents:
::

  syn region javaScript start=+{% js+ keepend end=+{% endjs %}+me=s-1 contains=@htmlJavaScript,htmlCssStyleComment,htmlScriptTag,@htmlPreproc
  syn region cssStyle start=+{% css+ keepend end=+{% endcss %}+ contains=@htmlCss,htmlTag,htmlEndTag,htmlCssStyleComment,@htmlPreproc

What next ?
===========

* Convert all your components to template components.
* Read `Steve Souder's "High Performance Web Sites" <http://stevesouders.com/hpws/rules.php>`_

License
=======

django_templatecomponents is licensed as `Beerware
<http://en.wikipedia.org/wiki/Beerware>`_, patches (including documentation!)
and suggestions are welcome.
