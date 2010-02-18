from django.template import loader, Context
from django.db import models
import inspect

#GUI Models
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

    #Get all the widgets belonging to this dashboard
    def get_widgets(self):
        # TODO: Make this not query the entire database, THEN filter.
        #       Just query for the right widgets.
        return [w for w in Widget.objects.filter(belongTo = self)]

    #Add a new widget to this dashboard. Y coordinate calculation needs to be written. X coordinate if right needs to be updated
    def addWidget(self, column):
        assert column in ['left','right']
        #TODO: Add code to calculate Y-coordinates
        if column == 'left':
            x = 0
        elif column == 'right':
            x = 1
        return self.widget_set.create(creator = self.user, x = x, y = 0)

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
        widgetclasses = [c for c in globals().values() if inspect.isclass(c) and hasattr(c, "parent_widget")]
        for nextc in widgetclasses:
            query_result = [s for s in nextc.objects.filter(parent_widget = self)]
            try:
                return query_result[0]
            except:
                pass

    def add_typed_widget(self, graphtype, wzoom, sdate, edate, unitone, unittwo):
        if graphtype == "barGraph":
            pass
        elif graphtype == "lineGraph":
            linewidget = LineWidget(parent_widget = self, zoom = wzoom, startdate = sdate, enddate = edate, sliderstartdate = sdate, sliderenddate = edate, firstunit = unitone, secondunit = unittwo)
            linewidget.save()
            return linewidget
        elif graphtype == "table":
            pass
        else:
            ticker = TickerWidget(parent_widget = self, firstunit = unitone)
            ticker.save()
            return ticker
                         
    def add_query(self, querytable, option, property):
        newquery = Query(self, table, option, property)
        newquery.save
        return newquery

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

    def remove_widget(self):
        'Remove this widget and its queries from the database'
        raise NotImplementedError
        
    def get_specialization(self):
        # First, identify all classes with a 'parent_widget'
        # attribute in this module
        specs = []
        for c in globals().itervalues():
            if inspect.isclass(c) and issubclass(c, models.Model) and hasattr(c, 'parent_widget'):
                specs.append(c)
        print specs
        # Find out which of these is this particular specialization
        for spec in specs:
            o = spec.objects.filter(parent_widget__pk=self.pk)
            if len(o) > 1:
                raise Exception('Database integrity error. Found more than one %s with the same parent Widget.' % str(type(spec)))
            elif len(o) == 1:
                return o[0]
        raise Exception("Found no specialization for %s" % (unicode(self)))
    
    #refer to self as belongTo,x,y
    def __unicode__(self):
        return "Widget (belonging to " + str(self.belongTo) + "):" + " ".join([str(q) for q in self.get_queries()]) + " " + str(self.pk)

class LineWidget(models.Model):
    """A widget containing a line graph of data.
    Has a one-to-one relationship with a non-typed widget.
    """
    parent_widget = models.OneToOneField(Widget, primary_key = True)
    zoom = models.CharField(max_length = 10) #miliseconds/hundred pixels
    startdate = models.DateTimeField() #start date updates to current day -15 zoom units if null
    enddate = models.DateTimeField() #end date updates to current day if null
    sliderstartdate = models.DateTimeField() #earliest date that can be selected by the widget's slider
    sliderenddate = models.DateTimeField() #latest date that can be selected by the widget's slider
    latestentry = models.DateTimeField()
    firstunit = models.CharField(max_length = 20)
    secondunit = models.CharField(max_length = 20)
    def get_html(self):
        t = loader.get_template('linewidget.html')
        c = Context({ 'widget_pk': self.pk })
        print t.render(c)
        return t.render(c)
    def __unicode__(self):
        return "LineWidget " + str(self.parent_widget.pk)

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

    def get_html(self):
        queries = self.parent_widget.get_queries()
        if len(queries) > 1:
            raise Exception("%s has more than one query" % unicode(self))
        query = queries[0]
            
        try:
            return u'<strong>%s.%s:</strong> %s' % (query.table, query.first_order_option, query.run().next())
        except StopIteration:
            return u'<strong>No data for %s.%s!</strong>' % (query.table, query.first_order_option)
    def __unicode__(self):
        return u'<TickerWidget %d>' % self.pk 
    
class Kit(WidgetOwner):
    """A collection of widgets that can all be added to the dashboard at once. Kits store multiple widgets by storing each widget's
    ID into a list
    """
    name = models.CharField(max_length=30)
    creator = models.CharField(max_length=50)
    dateCreated = models.DateTimeField('created')

#
# DATA
#

class DataEntry(models.Model):
    """A base class for all data entries. Contains a date at which the entry was recorded
    """
    time = models.DateTimeField()
    
class StockPrice(DataEntry):
    """Stores a price of a share of Edison International's (EIX) stock on the NYSE market at one time.
    Recorded in US$/share
    """
    symbol = models.CharField(max_length=4)
    price = models.FloatField()
        
    @staticmethod
    def first_order_options():
        '''
        Return an ordered list of
        values commonly used for
        sub-selection of bonds
        for visualization.
        
        >>> StockPrice.first_order_options()
        ['EIX']
        '''
        # TODO: Return some nonsense
        return ['EIX', 'APPL', 'GOOG', 'EMG', 'OMG', 'CATS']
    @staticmethod
    def objects_by_first_order_option(p):
        """Returns a dictionary of all entries in this class' table that pass the filter p for first order options
        """
        print 'getting Stockprices where symbol is %s' % p
        return StockPrice.objects.filter(symbol=p).values()
    @staticmethod
    def get_units():
        """Returns the units that stock prices are recorded in (dollars)
        """
        return "dollars"
    def __unicode__(self):
        return self.symbol + " " + str(self.time)

class BondPrice(DataEntry):
    """The daily trading price for EME and subsidiary bonds.
    Recorded in US$
    """
    price = models.FloatField()
    company = models.CharField(max_length = 50)
    def __unicode__(self):
        return " ".join([self.company, str(self.time)])
    @staticmethod
    def get_units():
        """Returns the units that bond prices are recorded in (dollars)
        """
        return "dollars"
    
class PowerOutput(DataEntry):
    """A statistic for the electricity generated in one day by one of EMG's generation units.
    Recorded in megawatts/hour
    """
    genunit = models.CharField(max_length = 50)
    output = models.FloatField()

    def __unicode__(self):
        return " ".join([self.genunit, str(self.time)])
    @staticmethod
    def get_units():
        """Returns the units that power output readings are recorded in (Megawatts/hour)
        """
        return "MW/hr"

class ElectricityPrice(DataEntry):
    """The market price for electricity at designated ISO zone/hub.
    Recorded in US$/megawatt/hour
    """
    price = models.FloatField()
    iso = models.CharField(max_length = 20)

    def __unicode__(self):
        return " ".join([self.iso, str(self.time)])
    @staticmethod
    def get_units():
        """Returns the units that electricity prices are recorded in (dollars/megawatts/hour)
        """
        return "dollars"

class NaturalGasPrice(DataEntry):
    """The market price for natural gas at the specified delivery hub.
    Recorded in US$/MMBTU
    """
    price = models.FloatField()
    iso = models.CharField(max_length = 20)

    def __unicode__(self):
        return " ".join([self.iso, str(self.time)])
    @staticmethod
    def get_units():
        """Returns the units that gas prices are recorded in (dollars/MMBTU)
        """
        return "dollars"

class CoalPrice(DataEntry):
    """The market price for coal by coal type.
    Recorded in US$/short ton
    """
    price = models.FloatField()
    coaltype = models.CharField(max_length = 20)

    def __unicode__(self):
        return " ".join([self.coaltype, str(self.time)])
    @staticmethod
    def get_units():
        """Returns the units that coal prices are recorded in (dollars/ston)
        """
        return "dollars"

class GeneratorAvalablility(DataEntry):
    """The operational availability status of generation units.
    Recorded as choices.
    """
    AVAILABILITY_CHOICES = (
        ('M', 'Monitoring the problem'),
        ('D', 'Derating'),
        ('BF', 'One boiler forced off'),
        ('F', 'Forced outage'),
        ('P', 'Planned outage')
    )
    genunit = models.CharField(max_length = 50)
    unittype = models.CharField(max_length = 20)
    availability = models.CharField(max_length = 2, choices = AVAILABILITY_CHOICES)

    def __unicode__(self):
        return " ".join([self.genunit, str(self.time)])
    @staticmethod
    def get_units():
        """Returns the units that availability readings are recorded in (availability)
        """
        return "availability"    

class SubsidiaryBalance(DataEntry):
    """The cash position of the designated EMG subsidiary
    Recorded in US$
    """
    balance = models.FloatField()
    company = models.CharField(max_length = 50)

    def __unicode__(self):
        return " ".join([self.company, str(self.time)])
    @staticmethod
    def get_units():
        """Returns the units that subsidiary balances are recorded in (dollars)
        """
        return "dollars"

class AvailableCapital(DataEntry):
    """The available funds from EMG company, working capital facilities, and borrows against those facilities
    Recorded in US$
    """
    pass

class LettersOfCredit(DataEntry):
    """The letter of credit commitments in place using EMG company working capital facilities.
    """
    pass

class ProfitLoss(DataEntry):
    """The daily results for EMMT's trading activities based on prices earned for power delivered.
    Recorded in US$
    """
    profit = models.FloatField()
    expenditures = models.FloatField()
    netprofit = models.FloatField()

    def __unicode__(self):
        return str(self.time)
    @staticmethod
    def get_units():
        """Returns the units that P&L figures are recorded in (dollars)
        """
        return "dollars"

class MoodyRating(DataEntry):
    """EME and subsidiary company ratings by Moody's.
    Elements still need to be reviewed.
    """
    pass

class SPRating(DataEntry):
    """EME and subsidiary company ratings by Moody's.
    Elements still need to be reviewed.
    """
    pass

class GrossMargin(DataEntry):
    """The margin earned for daily power output sold via trading by EMMT
    Recorded in US$
    """
    margin = models.FloatField()

    def __unicode__(self):
        return str(self.time)
    @staticmethod
    def get_units():
        """Returns the units that gross margin figures are recorded in (dollars)
        """
        return "dollars"
        
#
# Auxiliary Data
#
class StockSymbolDescription(models.Model):
    symbol = models.CharField(max_length=4)
    company_name = models.CharField(max_length=200)
        
if __name__ == '__main__':
    import doctest
    doctest.testmod()
