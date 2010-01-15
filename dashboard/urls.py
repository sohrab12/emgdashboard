from django.conf.urls.defaults import *
urlpatterns = patterns('emgdashboard.dashboard.views',
    (r'^graph_chunk$', 'graph_view')
)