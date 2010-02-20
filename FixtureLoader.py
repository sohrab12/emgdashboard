# FixtureLoader.py
# loads exampledata2.json into database

# fixture stuff
from dashboard.models import *
from django.core import management
from django.db.models import get_app

management.call_command('flush', verbosity=0, interactive=False)
d = Dashboard.objects.all()
print d
management.call_command('loaddata', 'exampledata.json', verbosity=0)
print d
print Dashboard.objects.get(user="Subject 1")
w = Widget.objects.all()
print w
l = LineWidget.objects.all()
print l
print l[0].zoom
print l[0].parentwidget
print l[0].parentwidget.creator

e = DataEntry.objects.all()
print e
s = StockPrice.objects.all()
print s

