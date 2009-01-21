# this is for backwards compatability

print "'django_templatecomponents' module name has changed. You should use 'templatecomponents' instead."

import sys, os
sys.path.append(os.path.dirname(__file__))

from templatecomponents import *
import templatecomponents

class views:
  pass
