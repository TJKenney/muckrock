"""
URL mappings for the Organization application
"""

# Django
from django.conf.urls import url

# MuckRock
from muckrock.organization import views

urlpatterns = [
    url(r'^$', views.OrganizationListView.as_view(), name='org-index'),
    url(
        r'^create/$', views.OrganizationCreateView.as_view(), name='org-create'
    ),
    url(
        r'^(?P<slug>[\w-]+)/$',
        views.OrganizationDetailView.as_view(),
        name='org-detail'
    ),
    url(
        r'^(?P<slug>[\w-]+)/activate/$',
        views.OrganizationActivateView.as_view(),
        name='org-activate'
    ),
    url(
        r'^(?P<slug>[\w-]+)/update/$',
        views.OrganizationUpdateView.as_view(),
        name='org-update'
    ),
    url(
        r'^(?P<slug>[\w-]+)/deactivate/$',
        views.deactivate_organization,
        name='org-deactivate'
    ),
    url(
        r'^(?P<slug>[\w-]+)/delete/$',
        views.OrganizationDeleteView.as_view(),
        name='org-delete'
    ),
]
