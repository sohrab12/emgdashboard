from django.conf.urls.defaults import *
from django.conf import settings





urlpatterns = patterns('emgdashboard.dashboard.views',
    (r'^$', 'index'),
    (r'^graph_chunk/(?P<widget_id>\d+)$', 'line_graph_view'),
    (r'^addWidget/$', 'addWidget'),
    (r'^export_widgets$', 'export_widget'),
    (r'^linewidget/(?P<widget_id>\d+)$', 'widget_properties'),
    (r'^tickerwidget/(?P<ticker_widget_id>\d+)$', 'ticker_widget'),
    (r'^slidewidgettimes', 'slide_times'),
    (r'^removewidget$', 'remove_widget'))