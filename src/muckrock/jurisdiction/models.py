"""
Models for the Jurisdiction application
"""
from django.db import models
from django.db.models import Sum

from easy_thumbnails.fields import ThumbnailerImageField

from tags.models import Tag

class RequestHelper(object):
    """Helper methods for classes that have a foiarequest_set"""
    # pylint: disable=E1101

    def exemptions(self):
        """Get a list of exemptions tagged for requests from this agency"""

        exemption_list = []
        for tag in Tag.objects.filter(name__startswith='exemption'):
            count = self.foiarequest_set.filter(tags=tag).count()
            if count:
                exemption_list.append({'name': tag.name, 'count': count})

        return exemption_list

    def interesting_requests(self):
        """Return a list of interesting requests to display on the agency's detail page"""
        # pylint: disable=W0141

        def make_req(headline, reqs):
            """Make a request dict if there is at least one request in reqs"""
            if reqs.exists():
                return {'headline': headline, 'req': reqs[0]}

        return filter(None, [
            make_req('Most Recently Completed Request',
                     self.foiarequest_set
                         .get_done()
                         .get_public()
                         .order_by('-date_done')),
            make_req('Oldest Overdue Request',
                     self.foiarequest_set
                         .get_overdue()
                         .get_public()
                         .order_by('date_due')),
            make_req('Largest Fufilled Request',
                     self.foiarequest_set
                         .get_done()
                         .get_public()
                         .filter(documents__pages__gt=0)
                         .annotate(pages=Sum('documents__pages'))
                         .order_by('-pages')),
            make_req('Most Viewed Request',
                     self.foiarequest_set
                         .get_public()
                         .order_by('-times_viewed')),
        ])

    def average_response_time(self):
        """Get the average response time from a submitted to completed request"""

        reqs = self.foiarequest_set.exclude(date_submitted=None).exclude(date_done=None)
        if reqs.exists():
            return sum((req.date_done - req.date_submitted).days for req in reqs) / reqs.count()
        else:
            return 0

    def total_pages(self):
        """Total pages released"""

        pages = self.foiarequest_set.aggregate(Sum('documents__pages'))['documents__pages__sum']
        if pages is None:
            return 0
        return pages


class Jurisdiction(models.Model, RequestHelper):
    """A jursidiction that you may file FOIA requests in"""

    levels = ( ('f', 'Federal'), ('s', 'State'), ('l', 'Local') )

    name = models.CharField(max_length=50)
    # slug should be slugify(unicode(self))
    slug = models.SlugField(max_length=55)
    abbrev = models.CharField(max_length=5, blank=True)
    level = models.CharField(max_length=1, choices=levels)
    parent = models.ForeignKey('self', related_name='children', blank=True, null=True)
    hidden = models.BooleanField(default=False)
    days = models.PositiveSmallIntegerField(blank=True, null=True)
    image = ThumbnailerImageField(upload_to='jurisdiction_images', blank=True, null=True,
                                  resize_source={'size': (372, 233), 'crop': 'smart'})
    image_attr_line = models.CharField(blank=True, max_length=255, help_text='May use html')
    public_notes = models.TextField(blank=True, help_text='May use html')

    def __unicode__(self):
        # pylint: disable=E1101
        if self.level == 'l':
            return '%s, %s' % (self.name, self.parent.abbrev)
        else:
            return self.name

    @models.permalink
    def get_absolute_url(self):
        """The url for this object"""
        # pylint: disable=E1101
        return ('jurisdiction-detail', [], {'slug': self.slug, 'idx': self.pk})

    def legal(self):
        """Return the jurisdiction abbreviation for which law this jurisdiction falls under"""
        # pylint: disable=E1101
        if self.level == 'l':
            return self.parent.abbrev
        else:
            return self.abbrev

    def get_days(self):
        """How many days does an agency have to reply?"""
        # pylint: disable=E1101
        if self.level == 'l':
            return self.parent.days
        else:
            return self.days

    class Meta:
        # pylint: disable=R0903
        ordering = ['name']

