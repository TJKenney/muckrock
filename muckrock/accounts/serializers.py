"""
Serilizers for the accounts application API
"""

# Django
from django.contrib.auth.models import User

# Third Party
from rest_framework import serializers

# MuckRock
from muckrock.accounts.models import Profile, Statistics
from muckrock.jurisdiction.models import Jurisdiction


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model"""
    location = serializers.PrimaryKeyRelatedField(
        queryset=Jurisdiction.objects.all(),
        style={
            'base_template': 'input.html'
        }
    )

    class Meta:
        model = Profile
        exclude = ('user',)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'is_staff',
            'is_superuser', 'last_login', 'date_joined', 'groups', 'profile'
        )


class StatisticsSerializer(serializers.ModelSerializer):
    """Serializer for Statistics model"""

    def __init__(self, *args, **kwargs):
        # pylint: disable=super-on-old-class
        super(StatisticsSerializer, self).__init__(*args, **kwargs)
        if 'request' not in self.context or not self.context['request'
                                                             ].user.is_staff:
            staff_only = (
                'pro_users',
                'pro_user_names',
                'total_page_views',
                'daily_requests_pro',
                'daily_requests_basic',
                'daily_requests_beta',
                'daily_requests_proxy',
                'daily_requests_admin',
                'daily_requests_org',
                'daily_articles',
                'total_tasks',
                'total_unresolved_tasks',
                'total_generic_tasks',
                'total_unresolved_generic_tasks',
                'total_orphan_tasks',
                'total_unresolved_orphan_tasks',
                'total_snailmail_tasks',
                'total_unresolved_snailmail_tasks',
                'total_rejected_tasks',
                'total_unresolved_rejected_tasks',
                'total_staleagency_tasks',
                'total_unresolved_staleagency_tasks',
                'total_flagged_tasks',
                'total_unresolved_flagged_tasks',
                'total_newagency_tasks',
                'total_unresolved_newagency_tasks',
                'total_response_tasks',
                'total_unresolved_response_tasks',
                'total_faxfail_tasks',
                'total_unresolved_faxfail_tasks',
                'total_payment_tasks',
                'total_unresolved_payment_tasks',
                'total_crowdfundpayment_tasks',
                'total_unresolved_crowdfundpayment_tasks',
                'daily_robot_response_tasks',
                'admin_notes',
                'total_active_org_members',
                'total_active_orgs',
                'sent_communications_email',
                'sent_communications_fax',
                'sent_communications_mail',
                'total_users_filed',
                'flag_processing_days',
                'unresolved_snailmail_appeals',
                'total_crowdfunds',
                'total_crowdfunds_pro',
                'total_crowdfunds_basic',
                'total_crowdfunds_beta',
                'total_crowdfunds_proxy',
                'total_crowdfunds_admin',
                'open_crowdfunds',
                'open_crowdfunds_pro',
                'open_crowdfunds_basic',
                'open_crowdfunds_beta',
                'open_crowdfunds_proxy',
                'open_crowdfunds_admin',
                'closed_crowdfunds_0',
                'closed_crowdfunds_0_25',
                'closed_crowdfunds_25_50',
                'closed_crowdfunds_50_75',
                'closed_crowdfunds_75_100',
                'closed_crowdfunds_100_125',
                'closed_crowdfunds_125_150',
                'closed_crowdfunds_150_175',
                'closed_crowdfunds_175_200',
                'closed_crowdfunds_200',
                'total_crowdfund_payments',
                'total_crowdfund_payments_loggedin',
                'total_crowdfund_payments_loggedout',
                'public_projects',
                'private_projects',
                'unapproved_projects',
                'crowdfund_projects',
                'project_users',
                'project_users_pro',
                'project_users_basic',
                'project_users_beta',
                'project_users_proxy',
                'project_users_admin',
                'total_exemptions',
                'total_invoked_exemptions',
                'total_example_appeals',
                'requests_processing_days',
            )
            for field in staff_only:
                self.fields.pop(field)

    class Meta:
        model = Statistics
        fields = (
            'date',
            'total_requests',
            'total_requests_success',
            'total_requests_denied',
            'total_requests_draft',
            'total_requests_submitted',
            'total_requests_awaiting_ack',
            'total_requests_awaiting_response',
            'total_requests_awaiting_appeal',
            'total_requests_fix_required',
            'total_requests_payment_required',
            'total_requests_no_docs',
            'total_requests_partial',
            'total_requests_abandoned',
            'total_requests_lawsuit',
            'requests_processing_days',
            'total_pages',
            'total_users',
            'total_agencies',
            'total_fees',
            'pro_users',
            'pro_user_names',
            'total_page_views',
            'daily_requests_pro',
            'daily_requests_basic',
            'daily_requests_beta',
            'daily_requests_proxy',
            'daily_requests_admin',
            'daily_requests_org',
            'daily_articles',
            'total_tasks',
            'total_unresolved_tasks',
            'total_generic_tasks',
            'total_unresolved_generic_tasks',
            'total_orphan_tasks',
            'total_unresolved_orphan_tasks',
            'total_snailmail_tasks',
            'total_unresolved_snailmail_tasks',
            'total_rejected_tasks',
            'total_unresolved_rejected_tasks',
            'total_staleagency_tasks',
            'total_unresolved_staleagency_tasks',
            'total_flagged_tasks',
            'total_unresolved_flagged_tasks',
            'total_newagency_tasks',
            'total_unresolved_newagency_tasks',
            'total_response_tasks',
            'total_unresolved_response_tasks',
            'total_faxfail_tasks',
            'total_unresolved_faxfail_tasks',
            'total_payment_tasks',
            'total_unresolved_payment_tasks',
            'total_crowdfundpayment_tasks',
            'total_unresolved_crowdfundpayment_tasks',
            'daily_robot_response_tasks',
            'public_notes',
            'admin_notes',
            'total_active_org_members',
            'total_active_orgs',
            'sent_communications_email',
            'sent_communications_fax',
            'sent_communications_mail',
            'total_users_filed',
            'flag_processing_days',
            'unresolved_snailmail_appeals',
            'total_crowdfunds',
            'total_crowdfunds_pro',
            'total_crowdfunds_basic',
            'total_crowdfunds_beta',
            'total_crowdfunds_proxy',
            'total_crowdfunds_admin',
            'open_crowdfunds',
            'open_crowdfunds_pro',
            'open_crowdfunds_basic',
            'open_crowdfunds_beta',
            'open_crowdfunds_proxy',
            'open_crowdfunds_admin',
            'closed_crowdfunds_0',
            'closed_crowdfunds_0_25',
            'closed_crowdfunds_25_50',
            'closed_crowdfunds_50_75',
            'closed_crowdfunds_75_100',
            'closed_crowdfunds_100_125',
            'closed_crowdfunds_125_150',
            'closed_crowdfunds_150_175',
            'closed_crowdfunds_175_200',
            'closed_crowdfunds_200',
            'total_crowdfund_payments',
            'total_crowdfund_payments_loggedin',
            'total_crowdfund_payments_loggedout',
            'public_projects',
            'private_projects',
            'unapproved_projects',
            'crowdfund_projects',
            'project_users',
            'project_users_pro',
            'project_users_basic',
            'project_users_beta',
            'project_users_proxy',
            'project_users_admin',
            'total_exemptions',
            'total_invoked_exemptions',
            'total_example_appeals',
            'machine_requests',
            'machine_requests_success',
            'machine_requests_denied',
            'machine_requests_draft',
            'machine_requests_submitted',
            'machine_requests_awaiting_ack',
            'machine_requests_awaiting_response',
            'machine_requests_awaiting_appeal',
            'machine_requests_fix_required',
            'machine_requests_payment_required',
            'machine_requests_no_docs',
            'machine_requests_partial',
            'machine_requests_abandoned',
            'machine_requests_lawsuit',
        )
