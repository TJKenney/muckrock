"""
Autocomplete registry for crowdfunds
"""

# Third Party
from autocomplete_light import shortcuts as autocomplete_light

# MuckRock
from muckrock.crowdfund.models import Crowdfund

autocomplete_light.register(
    Crowdfund,
    name='CrowdfundAutocomplete',
    choices=Crowdfund.objects.all(),
    search_fields=('name',),
    attrs={
        'placeholder': 'Search for crowdfunds',
        'data-autocomplete-minimum-characters': 1
    }
)
