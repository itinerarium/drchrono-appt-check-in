from django.conf.urls import include, url
from django.views.generic import TemplateView

import views

urlpatterns = [
    # login page
    url(r'^$', views.home, name='home'),
    # doctor view
    url(r'^doctor$', views.doctor, name='doctor'),

    # kiosk views
    ## error page
    url(r'^(?P<instance_guid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/error$', views.error, name='error'),
    ## kiosk homepage
    url(r'^(?P<instance_guid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/kiosk$', views.kiosk, name='kiosk'),
    ## confirm identity page
    url(r'^(?P<instance_guid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/checkin$', views.checkin, name='checkin'),
    ## demographic update page
    url(r'^(?P<instance_guid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/update$', views.update, name='update'),
    ## handle demographic update and check in
    url(r'^(?P<instance_guid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/complete$', views.complete, name='complete'),
    ## log out page (unused?)
    url(r'^logout$', views.leave, name='logout'),

    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
