'''
>>> from django.conf import settings
>>> from templatecomponents import TemplateComponentBlock
>>> TemplateComponentBlock.from_string("{% css %} foo. {% endcss %}")[0]
/* extracted css */
foo.
>>> TemplateComponentBlock.from_string("{% javascript %} foo. {% endjavascript %}")[0]
/* extracted javascript */
foo.
>>> TemplateComponentBlock.from_string("{% javascript 1 %} foo. {% endjavascript %}")[0]
/* extracted javascript with priority 1 */
foo.
>>> TemplateComponentBlock.from_string("{% javascript eggs 1 %} foo. {% endjavascript %}")[0]
/* extracted javascript with priority 1 within groups eggs */
foo.
>>> TemplateComponentBlock.from_string("{% javascript 1 eggs %} foo. {% endjavascript %}")[0]
/* extracted javascript with priority 1 within groups eggs */
foo.
>>> TemplateComponentBlock.from_string("{% javascript bar %} foo. {% endjavascript %}")[0]
/* extracted javascript within groups bar */
foo.
>>> TemplateComponentBlock.from_string("""
... {% javascript bar %} foo. {% endjavascript %}
... bar
... {% javascript bar %} foo. {% endjavascript %}
... """)
/* extracted javascript within groups bar */
foo.
/* extracted javascript within groups bar */
foo.
>>> #
>>> #
>>> #
>>> #
>>> #
>>> complexexample = """
... {% javascript baz %} x += 1; {% endjavascript %}
... {% javascript bar 10 %} var x = 1; {% endjavascript %}
... {% css print %} var x = 1; {% endcss %}
... <h1>Foo</h1>
... """
>>> #simple filter:
>>> TemplateComponentBlock.from_string(complexexample).filter('css')
/* extracted css within groups print */
var x = 1;
>>> #filter + priority
>>> TemplateComponentBlock.from_string(complexexample).filter('javascript')
/* extracted javascript with priority 10 within groups bar */
var x = 1;
/* extracted javascript within groups baz */
x += 1;
>>> TemplateComponentBlock.from_string(complexexample).filter('javascript').group('baz')
/* extracted javascript within groups baz */
x += 1;
'''

if __name__ == "__main__":
    import doctest
    doctest.testmod()
