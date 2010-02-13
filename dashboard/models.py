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
