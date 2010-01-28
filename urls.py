from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),    
    (r'^dashboard/', include('emgdashboard.dashboard.urls')),     
    (r'^mymedia/(?P<path>.*)$', 'django.views.static.serve',  
     {'document_root': settings.MEDIA_ROOT}), 
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
)