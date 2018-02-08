# -*- coding: utf-8 -*-
"""
Models for the FOIA application
"""

# Django
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.shortcuts import get_object_or_404

# Standard Library
import logging
import mimetypes
import os
import re
from datetime import datetime

# Third Party
import chardet

# MuckRock
from muckrock.foia.models.request import STATUS, FOIARequest
from muckrock.utils import new_action

logger = logging.getLogger(__name__)

DELIVERED = (
    ('fax', 'Fax'),
    ('email', 'Email'),
    ('mail', 'Mail'),
    ('web', 'Web'),
)


class FOIACommunicationQuerySet(models.QuerySet):
    """Object manager for FOIA Communications"""

    def visible(self):
        """Hide hidden communications"""
        return self.filter(hidden=False)


class FOIACommunication(models.Model):
    """A single communication of a FOIA request"""

    foia = models.ForeignKey(
        FOIARequest, related_name='communications', blank=True, null=True
    )

    from_user = models.ForeignKey(
        'auth.User',
        related_name='sent_communications',
        null=True,
        blank=True,
    )
    to_user = models.ForeignKey(
        'auth.User',
        related_name='received_communications',
        null=True,
        blank=True,
    )

    subject = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField(db_index=True)

    response = models.BooleanField(
        default=False, help_text='Is this a response (or a request)?'
    )

    autogenerated = models.BooleanField(default=False)
    thanks = models.BooleanField(default=False)
    full_html = models.BooleanField(default=False)
    communication = models.TextField(blank=True)
    hidden = models.BooleanField(default=False)

    # what status this communication should set the request to - used for machine learning
    status = models.CharField(
        max_length=10, choices=STATUS, blank=True, null=True
    )

    # only used for orphans
    likely_foia = models.ForeignKey(
        FOIARequest,
        related_name='likely_communications',
        blank=True,
        null=True
    )

    # Depreacted fields
    # keep these for old communications
    from_who = models.CharField(max_length=255, blank=True)
    to_who = models.CharField(max_length=255, blank=True)
    priv_from_who = models.CharField(max_length=255, blank=True)
    priv_to_who = models.CharField(max_length=255, blank=True)

    # these can be deleted eventually
    delivered = models.CharField(
        max_length=10, choices=DELIVERED, blank=True, null=True
    )
    fax_id = models.CharField(max_length=10, blank=True, default='')
    confirmed = models.DateTimeField(blank=True, null=True)
    opened = models.BooleanField(
        default=False,
        help_text='DEPRECATED: If emailed, did we receive an open notification?'
        ' If faxed, did we recieve a confirmation?'
    )

    objects = FOIACommunicationQuerySet.as_manager()

    def __unicode__(self):
        return u'%s - %s' % (self.date, self.subject)

    def get_absolute_url(self):
        """The url for this object"""
        return self.foia.get_absolute_url() + ('#comm-%d' % self.pk)

    def save(self, *args, **kwargs):
        """Remove controls characters from text before saving"""
        remove_control = dict.fromkeys(
            range(0, 9) + range(11, 13) + range(14, 32)
        )
        self.communication = unicode(self.communication
                                     ).translate(remove_control)
        # limit communication length to 150k
        self.communication = self.communication[:150000]
        # special handling for certain agencies
        self._presave_special_handling()
        # update foia's date updated if this is the latest communication
        if (
            self.foia and (
                self.foia.date_updated is None
                or self.date.date() > self.foia.date_updated
            )
        ):
            self.foia.date_updated = self.date.date()
            self.foia.save(comment='update date_updated due to new comm')
        super(FOIACommunication, self).save(*args, **kwargs)

    def anchor(self):
        """Anchor name"""
        return 'comm-%d' % self.pk

    def get_source(self):
        """Get the source line for an attached file"""
        if self.foia and self.foia.agency:
            return self.foia.agency.name[:70]
        elif self.from_user:
            return self.from_user.get_full_name()[:70]
        else:
            return ''

    def move(self, foia_pks, user):
        """
        Move this communication. If more than one foia_pk is given, move the
        communication to the first request, then clone it across the rest of
        the requests. Returns the moved and cloned communications.
        """
        # avoid circular imports
        from muckrock.foia.tasks import upload_document_cloud
        if not foia_pks:
            raise ValueError('Expected a request to move the communication to.')
        if not isinstance(foia_pks, list):
            foia_pks = [foia_pks]
        move_to_request = get_object_or_404(FOIARequest, pk=foia_pks[0])
        old_foia = self.foia
        self.foia = move_to_request
        # if this was an orphan, it has not yet been uploaded
        # to document cloud
        change = old_foia is not None

        access = 'private' if self.foia.embargo else 'public'
        for each_file in self.files.all():
            each_file.access = access
            each_file.source = self.get_source()
            each_file.save()
            upload_document_cloud.apply_async(
                args=[each_file.pk, change], countdown=3
            )
        self.save()
        CommunicationMoveLog.objects.create(
            communication=self,
            foia=old_foia,
            user=user,
        )
        logger.info(
            'Communication #%d moved to request #%d', self.id, self.foia.id
        )
        # if cloning happens, self gets overwritten. so we save it to a variable here
        this_comm = FOIACommunication.objects.get(pk=self.pk)
        moved = [this_comm]
        cloned = []
        if foia_pks[1:]:
            cloned = self.clone(foia_pks[1:], user)
        return moved + cloned

    def clone(self, foia_pks, user):
        """
        Copies the communication to each request in the list,
        then returns all the new communications.
        ---
        When setting self.pk to None and then calling self.save(),
        Django will clone the communication along with all of its data
        and give it a new primary key. On the next iteration of the loop,
        the clone will be cloned along with its data, and so on. Same thing
        goes for each file attached to the communication.
        """
        # pylint: disable=too-many-locals
        request_list = FOIARequest.objects.filter(pk__in=foia_pks)
        if not request_list:
            raise ValueError('No valid request(s) provided for cloning.')
        cloned_comms = []
        original_pk = self.pk
        files = self.files.all()
        emails = self.emails.all()
        faxes = self.faxes.all()
        mails = self.mails.all()
        web_comms = self.web_comms.all()
        for request in request_list:
            this_clone = FOIACommunication.objects.get(pk=original_pk)
            this_clone.pk = None
            this_clone.foia = request
            this_clone.save()
            CommunicationMoveLog.objects.create(
                communication=this_clone,
                foia=self.foia,
                user=user,
            )
            for file_ in files:
                file_.clone(this_clone)
            # clone all sub communications as well
            for comms in [emails, faxes, mails, web_comms]:
                for comm in comms:
                    comm.pk = None
                    comm.communication = this_clone
                    comm.save()
            # for each clone, self gets overwritten. each clone needs to be stored explicitly.
            cloned_comms.append(this_clone)
            logger.info(
                'Communication #%d cloned to request #%d', original_pk,
                this_clone.foia.id
            )
        return cloned_comms

    def make_sender_primary_contact(self):
        """Makes the communication's sender the primary contact of its FOIA."""
        if not self.foia:
            raise ValueError(
                'Communication is an orphan and has no associated request.'
            )

        email_comm = self.emails.first()
        if email_comm and email_comm.from_email:
            self.foia.email = email_comm.from_email
            self.foia.cc_emails.set(email_comm.to_emails.all())
            self.foia.cc_emails.add(*email_comm.cc_emails.all())
            self.foia.save(comment='update primary contact from comm')
        else:
            raise ValueError('Communication was not sent from a valid email.')

    def _presave_special_handling(self):
        """Special handling before saving
        For example, strip out BoP excessive quoting"""

        def test_agency_name(name):
            """Match on agency name"""
            return (
                self.foia and self.foia.agency and self.foia.agency.name == name
            )

        def until_string(string):
            """Cut communication off after string"""

            def modify():
                """Run the modification on self.communication"""
                if string in self.communication:
                    idx = self.communication.index(string)
                    self.communication = self.communication[:idx]

            return modify

        special_cases = [
            # BoP: strip everything after '>>>'
            (test_agency_name('Bureau of Prisons'), until_string('>>>')),
            # Phoneix Police: strip everything after '_'*32
            (
                test_agency_name('Phoenix Police Department'),
                until_string('_' * 32)
            ),
        ]

        for test, modify in special_cases:
            if test:
                modify()

    def process_attachments(self, files):
        """Given uploaded files, turn them into FOIAFiles attached to the comm"""

        ignore_types = [('application/x-pkcs7-signature', 'p7s')]

        for file_ in files.itervalues():
            if not any(
                file_.content_type == t or file_.name.endswith(s)
                for t, s in ignore_types
            ):
                self.attach_file(file_=file_)

    def create_agency_notifications(self):
        """Create the notifications for when an agency creates a new comm"""
        if self.foia and self.foia.agency:
            action = new_action(
                self.foia.agency,
                'sent a communication',
                action_object=self,
                target=self.foia
            )
            self.foia.notify(action)
        if self.foia:
            self.foia.update(self.anchor())

    def attach_file(self, file_=None, content=None, name=None, source=None):
        """Given a file or name and the file contents, attach a file to this"""
        # must supply either file_ or content and name_
        from muckrock.foia.tasks import upload_document_cloud
        if file_ is None:
            file_ = ContentFile(content)
        if name is None:
            name = file_.name
        if source is None:
            source = self.get_source()

        title = os.path.splitext(name)[0][:255]
        access = 'private' if not self.foia or self.foia.embargo else 'public'
        with transaction.atomic():
            foia_file = self.files.create(
                title=title,
                date=datetime.now(),
                source=source[:70],
                access=access,
            )
            name = name[:233].encode('ascii', 'ignore')
            foia_file.ffile.save(name, file_)
            if self.foia:
                transaction.on_commit(
                    lambda: upload_document_cloud.delay(foia_file.pk, False)
                )
        return foia_file

    def attach_files_to_email(self, msg):
        """Attach all of this communications files to the email message"""
        for file_ in self.files.all():
            name = file_.name()
            content = file_.ffile.read()
            mimetype, _ = mimetypes.guess_type(name)
            if mimetype and mimetype.startswith('text/'):
                enc = chardet.detect(content)['encoding']
                content = content.decode(enc)
            msg.attach(name, content)

    def get_raw_email(self):
        """Get the raw email associated with this communication, if there is one"""
        return RawEmail.objects.filter(email__communication=self).first()

    def from_line(self):
        """What to display for who this communication is from"""
        if self.from_user and self.from_user.profile.acct_type == 'agency':
            return self.from_user.profile.agency.name
        elif self.from_user:
            return self.from_user.get_full_name()
        else:
            return self.from_who

    def get_subcomm(self):
        """Get the latest sub communication type"""
        # sort all types of comms by sent datetime,
        # and return the latest
        sorted_comms = sorted(
            list(self.emails.all()) + list(self.faxes.all()) +
            list(self.mails.all()) + list(self.web_comms.all()) +
            list(self.portals.all()),
            key=lambda x: x.sent_datetime,
            reverse=True,
        )
        if not sorted_comms:
            return None
        return sorted_comms[0]

    def get_delivered(self):
        """Get how this comm was delivered"""
        subcomm = self.get_subcomm()
        if subcomm:
            return subcomm.delivered
        else:
            return 'none'

    # for the admin
    get_delivered.short_description = 'delivered'

    def sent_to(self):
        """Who was this communication sent to?"""
        subcomm = self.get_subcomm()
        if subcomm:
            return subcomm.sent_to()
        else:
            return None

    def sent_from(self):
        """Who was this communication sent to?"""
        subcomm = self.get_subcomm()
        if subcomm:
            return subcomm.sent_from()
        else:
            return None

    def get_delivered_and_from(self):
        """Combine get_delivered and sent_from for performance reasons"""
        subcomm = self.get_subcomm()
        if subcomm:
            return (subcomm.delivered, subcomm.sent_from())
        else:
            return (None, None)

    def extract_tracking_id(self):
        """Try to extract a tracking number from this communication"""
        if self.foia.tracking_id:
            return
        patterns = [
            re.compile(r'Tracking Number:\s+([0-9a-zA-Z-]+)'),
        ]
        for pattern in patterns:
            match = pattern.search(self.communication)
            if match:
                self.foia.tracking_id = match.group(1).strip()[:255]
                self.foia.save()
                logger.info(
                    'FOIA Tracking ID set: FOIA PK: %d - Comm PK: %d - '
                    'Tracking ID: %s',
                    self.foia.id,
                    self.id,
                    self.foia.tracking_id,
                )
                break

    class Meta:
        ordering = ['date']
        verbose_name = 'FOIA Communication'
        app_label = 'foia'


class RawEmail(models.Model):
    """The raw email text for a communication - stored seperately for performance"""
    # nullable during transition
    # communication is depreacted and should be removed
    communication = models.OneToOneField(FOIACommunication, null=True)
    email = models.OneToOneField('communication.EmailCommunication', null=True)
    raw_email = models.TextField(blank=True)

    def __unicode__(self):
        return 'Raw Email: %d' % self.pk

    class Meta:
        app_label = 'foia'
        permissions = ((
            'view_rawemail', 'Can view the raw email for communications'
        ),)


class FOIANote(models.Model):
    """A private note on a FOIA request"""

    foia = models.ForeignKey(FOIARequest, related_name='notes')
    author = models.ForeignKey('auth.User', related_name='notes', null=True)
    datetime = models.DateTimeField(auto_now_add=True)
    note = models.TextField()

    def __unicode__(self):
        # pylint: disable=redefined-variable-type
        if self.author:
            user = self.author
        else:
            user = self.foia.user
        return 'Note by %s on %s' % (user.get_full_name(), self.foia.title)

    class Meta:
        ordering = ['foia', 'datetime']
        verbose_name = 'FOIA Note'
        app_label = 'foia'


class CommunicationError(models.Model):
    """An error has occured delivering this communication"""
    # Depreacted
    communication = models.ForeignKey(
        FOIACommunication,
        related_name='errors',
    )
    date = models.DateTimeField()

    recipient = models.CharField(max_length=255)
    code = models.CharField(max_length=10)
    error = models.TextField(blank=True)
    event = models.CharField(max_length=10)
    reason = models.CharField(max_length=255)

    def __unicode__(self):
        return u'CommunicationError: %s - %s' % (
            self.communication.pk, self.date
        )

    class Meta:
        ordering = ['date']
        app_label = 'foia'


class CommunicationOpen(models.Model):
    """A communication has been opened"""
    # Depreacted
    communication = models.ForeignKey(
        FOIACommunication,
        related_name='opens',
    )
    date = models.DateTimeField()

    recipient = models.EmailField()
    city = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    country = models.CharField(max_length=10)

    client_type = models.CharField(max_length=15)
    client_name = models.CharField(max_length=50)
    client_os = models.CharField(max_length=10, verbose_name='Client OS')

    device_type = models.CharField(max_length=10)
    user_agent = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=15, verbose_name='IP Address')

    def __unicode__(self):
        return u'CommunicationOpen: %s - %s' % (
            self.communication.pk, self.date
        )

    class Meta:
        ordering = ['date']
        app_label = 'foia'


class CommunicationMoveLog(models.Model):
    """Track communications being moved to different requests"""
    communication = models.ForeignKey(FOIACommunication)
    foia = models.ForeignKey(
        'foia.FOIARequest',
        blank=True,
        null=True,
    )
    user = models.ForeignKey('auth.User')
    datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        if self.foia:
            foia = u'FOIA {}'.format(self.foia.pk)
        else:
            foia = u'orphan'
        return u'Comm {} moved from {} by {} on {}'.format(
            self.communication.pk,
            foia,
            self.user.username,
            self.datetime,
        )
