=========================
django_templatecomponents
=========================

:Author: `Filip Noetzel <http://filip.noetzel.co.uk/>`_
:Version: v0.02
:Web: http://j03.de/projects/django_templatecomponents/
:Source: http://j03.de/projects/django_templatecomponents/git/ (also `on github <http://github.com/peritus/django_templatecomponents/>`_)
:Download: http://j03.de/projects/django_templatecomponents/releases/

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
* additional CSS and JavaScript for authenticated / paying in users
* CSS for browers with enabled or disabled JavaScript
* CSS and JavaScript for mobile devices
* CSS and JavaScript for legacy browsers

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

Minification
------------

(See also `rule #10 <http://stevesouders.com/hpws/rule-minify.php>`_)
django_templatecomponents allows you to `minify
<http://en.wikipedia.org/wiki/Minify>`_ your components both on the fly and
during static file generation. Currently `JSMin
<http://www.crockford.com/javascript/jsmin.html>`_ and `YUICompressor
<http://developer.yahoo.com/yui/compressor/>`_ are supported.

During development it is recommended to disable minification at all, as
debugging with tools such as `Firebug
<http://www.joehewitt.com/software/firebug/>`_ is a lot easier. So, you can
even debug your favourite ajax library using the non-minified version.

You can enable minification during development to test if your component code
plays well with minification (see `Configuration` below.).

Inline minification
-------------------

If you absolutly need to use inline components, you can minify these as well:
::

  {% javascript inline %}
    var getRandomNumber = function() {
      return 4; // chosen by fair dice roll.
                // guaranteed to be random.
    };
  {% endjavascript %}

would become
::

  <script type='text/javascript'>var getRandomNumber=function(){return 4};</script>

Within inline blocks, all of django's template syntax and context is supported.

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

This would ensure, the JavaScript Block from template2.html appears above the
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

Configuration 
=============

Here is a sample configuration file for **production**:
::

  TEMPLATECOMPONENTS_PATH_TO_YUICOMPRESSOR_JAR = \
    '/opt/yuicompressor/build/yuicompressor-2.3.5.jar'

  TEMPLATECOMPONENTS_COMPRESS_JAVASCRIPT = True

  TEMPLATECOMPONENTS_COMPRESS_CSS = True

Here is a sample configuration file for **development**:
::

  TEMPLATECOMPONENTS_PATH_TO_YUICOMPRESSOR_JAR = os.path.join(__file__,
    '/yuicompressor-2.3.5/build/yuicompressor-2.3.5.jar')

  TEMPLATECOMPONENTS_COMPRESS_JAVASCRIPT = False

  TEMPLATECOMPONENTS_COMPRESS_CSS = False

For development, you also want to add this to your urls.py (but *before*
http://www.djangoproject.com/documentation/static_files/#how-to-do-it)

::

  from django.conf import settings
  if settings.DEBUG:
      urlpatterns += patterns('', ('', include('django_templatecomponents.urls')))

What next ?
=================

* Convert all your components to template components.
* Read `Steve Souder's »High Performance Web Sites« <http://stevesouders.com/hpws/rules.php>`_

License
=======

django_templatecomponents is licensed as `Beerware
<http://en.wikipedia.org/wiki/Beerware>`_, patches (including documentation!)
and suggestions are welcome.
