from django.conf.urls.defaults import *

urlpatterns = patterns('emgdashboard.dashboard.views',
    (r'^graph_chunk$', 'line_graph_view'),
    (r'^addWidget/$', 'addWidget')
)