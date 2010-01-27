from django.db import models
from datetime import datetime

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
        return self.user

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

    #refer to self as belongTo,x,y
    def __unicode__(self):
        return str(self.belongTo) + str(self.x) + str(self.y)

class LineWidget(models.Model):
    """A widget containing a line graph of data.
    Has a one-to-one relationship with a non-typed widget.
    """
    parentwidget = models.OneToOneField(Widget, primary_key = True)
    zoom = models.PositiveIntegerField() #miliseconds/hundred pixels
    startdate = models.DateTimeField() #start date updates to current day if null
    enddate = models.DateTimeField() #end date updates to current day if null
    latestentry = models.DateTimeField()
    model1 = models.CharField(max_length = 60) #First table to query
    model1_prop = models.CharField(max_length = 60) #Filter for first query
    model2 = models.CharField(max_length = 60)
    model2_prop = models.CharField(max_length = 60)
    
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
    symbol = models.CharField(max_length = 4)
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
        return StockPrice.all_symbols
    def objects_by_first_order_option(self, p):
        """Return all entries in this class' table that pass the filter p for first order options
        """
        return (s for s in StockPrice.objects.filter(symbol = p))
    def __unicode__(self):
        return str(self.time)

class BondPrice(DataEntry):
    """The daily trading price for EME and subsidiary bonds.
    Recorded in US$
    """
    price = models.FloatField()
    company = models.CharField(max_length = 50)
    def __unicode__(self):
        return " ".join([self.company, str(self.time)])
    
class PowerOutput(DataEntry):
    """A statistic for the electricity generated in one day by one of EMG's generation units.
    Recorded in megawatts/hour
    """
    genunit = models.CharField(max_length = 50)
    output = models.FloatField()

    def __unicode__(self):
        return " ".join([self.genunit, str(self.time)])   

class ElectricityPrice(DataEntry):
    """The market price for electricity at designated ISO zone/hub.
    Recorded in US$/megawatt/hour
    """
    price = models.FloatField()
    iso = models.CharField(max_length = 20)

    def __unicode__(self):
        return " ".join([self.iso, str(self.time)])                        

class NaturalGasPrice(DataEntry):
    """The market price for natural gas at the specified delivery hub.
    Recorded in US$/MMBTU
    """
    price = models.FloatField()
    iso = models.CharField(max_length = 20)

    def __unicode__(self):
        return " ".join([self.iso, str(self.time)])    

class CoalPrice(DataEntry):
    """The market price for coal by coal type.
    Recorded in US$/short ton
    """
    price = models.FloatField()
    coaltype = models.CharField(max_length = 20)

    def __unicode__(self):
        return " ".join([self.coaltype, str(self.time)])    

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

class SubsidiaryBalance(DataEntry):
    """The cash position of the designated EMG subsidiary
    Recorded in US$
    """
    balance = models.FloatField()
    company = models.CharField(max_length = 50)

    def __unicode__(self):
        return " ".join([self.company, str(self.time)])    

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
        
if __name__ == '__main__':
    import doctest
    doctest.testmod()
