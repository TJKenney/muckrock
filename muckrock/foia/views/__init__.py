"""
Views for the FOIA application
"""

import autocomplete_light
autocomplete_light.autodiscover()

from muckrock.foia.views.views import *
from muckrock.foia.views.actions import *
from muckrock.foia.views.orphans import *
from muckrock.foia.views.composers import *