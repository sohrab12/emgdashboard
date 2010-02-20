from django.conf.urls.defaults import *
from django.conf import settings





urlpatterns = patterns('emgdashboard.dashboard.views',
    (r'^(?P<dashboard_id>\d+)$', 'index'),
    (r'^graph_chunk/(?P<widget_id>\d+)$', 'line_graph_view'),
    (r'^addWidget/$', 'addWidget'),
    (r'^export_widgets$', 'export_widget'),
    (r'^export_pdf$', 'export_pdf'),
    (r'^slidewidgettimes', 'slide_times'),
    (r'^removewidget$', 'remove_widget'))