"""
Autocomplete registry for Agency
"""

import autocomplete_light
from muckrock.agency.models import Agency
from muckrock.jurisdiction.models import Jurisdiction

class AgencyAutocomplete(autocomplete_light.AutocompleteModelBase):
    """Creates an autocomplete field for picking agencies"""
    search_fields = ['^name']
    attrs = {
        'placeholder': 'Agency',
        'data-autocomplete-minimum-characters': 0
    }
    def choices_for_request(self):
        query = self.request.GET.get('q', '')
        jurisdiction_id = self.request.GET.get('jurisdictionId', None)
        choices = self.choices.all().filter(approved=True)
        if query:
            choices = choices.filter(name__icontains=query)
        if jurisdiction_id:
            if jurisdiction_id == 'f':
                jurisdiction_id = (Jurisdiction.objects.filter(level='f')[0]).id
            choices = choices.filter(jurisdiction=jurisdiction_id)
        return self.order_choices(choices)[0:self.limit_choices]

autocomplete_light.register(Agency, AgencyAutocomplete)
