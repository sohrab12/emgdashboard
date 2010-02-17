from django.models import HttpResponse
from django.db import models
import inspect
import datetime

class WidgetOwner(models.Model):
    """A superclass of dashboards and kits, any entity that has widgets tied to it.
    """
    pass

class Dashboard(WidgetOwner):
    """A user's dashboard, including the last time the user logged into it. All widgets reference a dashboard as a foreign key.
    """
    user = models.CharField(max_length = 50)
    lastLogin = models.DateTimeField('last login')

    #refer to self by user
    def __unicode__(self):
        return "%s's Dashboard" % self.user

    #Add a new widget to this dashboard. Y coordinate calculation needs to be written. X coordinate if right needs to be updated
    def addWidget(self, newquery, column):
        #Create query for the new widget
        #query = Query(value = "select %s from %s 
        #TODO: Add code to calculate Y-coordinates
        self.widget_set.create(creator = self.user, x = column, y = 0)

class Widget(models.Model):
    """A single sub-display that stores a query to be submitted to the database, and handles the displaying of the resulting data.
    """
    belongTo = models.ForeignKey(WidgetOwner)
    creator = models.CharField(max_length=50)
    created = models.DateTimeField('created')
    updated = models.DateTimeField('last update')
    x = models.PositiveIntegerField()
    y = models.PositiveIntegerField()

    def widget_type(self):
        widgetclasses = [c for c in globals().values() if inspect.isclass(c) and hasattr(c, "parentwidget")]
        for nextc in widgetclasses:
            query_result = [s for s in nextc.objects.filter(parentwidget = self)]
            try:
                return query_result[0]
            except:
                pass

    #Gets all the queries associated with this widget    
    def get_queries(self):
        return [q for q in Query.objects.filter(belongTo = self)]

    def slide_times(self, starttime, endtime):
        """Change the widget's start time and end time to reflect the values chosen by the slider
        """
        typed_widget = self.widget_type()
        zoom = typed_widget.zoom
        #Get the start and end date strings from the request
        startstring = starttime
        endstring = endtime

        #Parse the time strings according to the widget's zoom    
        if(zoom == "hours"):
            #Start date
            #if timestamp is PM, add 12 hours to it unless noon
            if (startstring.split(" ")[2] == "PM") and (startstring.split(" ")[1] != "12"):
                hours = int(startstring.split(" ")[1]) + 12
            #If midnight, set to zero
            elif (startstring.split(" ")[2] == "AM") and (startstring.split(" ")[1] == "12"):
                hours = 0
            #Otherwise, take it as is.
            else:
                hours = int(startstring.split(" ")[1])

            thedate = startstring.split(" ")[0]
            year = int(thedate.split("/")[2])
            month = int(thedate.split("/")[0])
            day = int(thedate.split("/")[1])
            newstart = datetime(year, month, day, hours, 0, 0)

            #End date
            #if timestamp is PM, add 12 hours to it unless noon
            if endstring.split(" ")[2] == "PM" and endstring.split(" ")[1] != "12":
                hours = int(endstring.split(" ")[1]) + 12
            #If midnight, set to zero
            elif endstring.split(" ")[2] == "AM" and endstring.split(" ")[1] == "12":
                hours = 0
            #Otherwise, take it as is.
            else:
                hours = int(endstring.split(" ")[1])

            thedate = endstring.split(" ")[0]
            year = int(thedate.split("/")[2])
            month = int(thedate.split("/")[0])
            day = int(thedate.split("/")[1])
            newend = datetime(year, month, day, hours, 59, 59)
        elif(zoom == "days" or zoom == "weeks"):
            #Start date
            thedate = startstring.split(" ")[0]
            year = int(thedate.split("/")[2])
            month = int(thedate.split("/")[0])
            day = int(thedate.split("/")[1])
            newstart = datetime(year, month, day, 0, 0, 0)

            #End date
            thedate = endstring.split(" ")[0]
            year = int(thedate.split("/")[2])
            month = int(thedate.split("/")[0])
            day = int(thedate.split("/")[1])
            newend = datetime(year, month, day, 23, 59, 59)
        elif(zoom == "months"):
            #Start date
            thedate = startstring.split(" ")[0]
            year = int(thedate.split("/")[1])
            month = int(thedate.split("/")[0])
            newstart = datetime(year, month, 1, 0, 0, 0)

            #End date
            thedate = endstring.split(" ")[0]
            year = int(thedate.split("/")[1])
            month = int(thedate.split("/")[0])
            newend = datetime(year, month, 28, 23, 59, 59)
        else: #zoom == years
            #Start date
            year = int(startstring.split(" ")[0])
            newstart = datetime(year, 1, 1, 0, 0, 0)

            #End date
            year = int(endstring.split(" ")[0])
            newend = datetime(year, 12, 31, 23, 59, 59)

        #Assign new start and end times to the widget in the database.
        try:
            typed_widget.startdate = newstart
            typed_widget.enddate = newend
            typed_widget.save()
        except:
            return HttpResponse("Could not alter widget")
        return HttpResponse("Worked")

    #Remove this widget and its queries from the database
    def remove_widget(request):
        return HttpResponse("Working")
    
    #refer to self as belongTo,x,y
    def __unicode__(self):
        return "Widget " + str(self.belongTo) + ":" + " ".join([str(q) for q in self.get_queries()]) + " " + str(self.pk)

class LineWidget(models.Model):
    """A widget containing a line graph of data.
    Has a one-to-one relationship with a non-typed widget.
    """
    parentwidget = models.OneToOneField(Widget, primary_key = True)
    zoom = models.CharField(max_length = 10) #miliseconds/hundred pixels
    startdate = models.DateTimeField() #start date updates to current day -15 zoom units if null
    enddate = models.DateTimeField() #end date updates to current day if null
    sliderstartdate = models.DateTimeField() #earliest date that can be selected by the widget's slider
    sliderenddate = models.DateTimeField() #latest date that can be selected by the widget's slider
    latestentry = models.DateTimeField()
    firstunit = models.CharField(max_length = 20)
    secondunit = models.CharField(max_length = 20)

    def __unicode__(self):
        return "LineWidget " + str(self.parentwidget.pk)

class Query(models.Model):
    """A query to be submitted to the database. Each query references a widget as a foreign key."""
    belongTo = models.ForeignKey(Widget)
    table = models.CharField(max_length=50) #The database table this query searches
    first_order_option = models.CharField(max_length=50) #The string to match to filter the table
    property = models.CharField(max_length=50) #The field we want to run the query for
    #Run the query, searching the table for entries that have the desired first order option. Then return the value
    #for the property field
    def run(self):
        print 'constructing generator w/ table=%s and property=%s' % (self.table, self.property)
        for o in globals()[self.table].objects_by_first_order_option(self.first_order_option):
            yield (o.__getitem__(self.property), o.__getitem__("time"))
    def __unicode__(self):
        return str(self.table)+" "+str(self.property)
        
class TickerWidget(models.Model):
    """
    A widget that displays the latest value
    of a single data series.
    """
    parent_widget = models.OneToOneField(Widget, primary_key=True)
    def get_query(self):
        return Query.objects.get(belongTo=self.parent_widget)
    def __unicode__(self):
        return '<TickerWidget query='+unicode(self.get_query())+'>'     
    
class Kit(WidgetOwner):
    """A collection of widgets that can all be added to the dashboard at once. Kits store multiple widgets by storing each widget's
    ID into a list
    """
    name = models.CharField(max_length=30)
    creator = models.CharField(max_length=50)
    dateCreated = models.DateTimeField('created')