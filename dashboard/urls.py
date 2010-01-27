from django.conf.urls.defaults import *
from django.conf import settings





urlpatterns = patterns('emgdashboard.dashboard.views',
    (r'^$', 'index'),
    (r'^graph_chunk$', 'line_graph_view'),
    (r'^addWidget/$', 'addWidget'),

)