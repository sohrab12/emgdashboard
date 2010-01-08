from django.db import models
from datetime import datetime

#GUI Models
class Dashboard(models.Model):
    """A user's dashboard, including the last time the user logged into it. All widgets reference a dashboard as a foreign key.
    """
    user = models.CharField(max_length = 50)
    sharedWidgets = []
    lastLogin = models.DateTimeField('last login')

    #Add a new widget to this dashboard. Y coordinate calculation needs to be written. X coordinate if right needs to be updated
    def addWidget(self, newquery, column):
        xval = 0 if column == 'left' else 30
        self.widget_set.create(creator = self.user, query = newquery, dateCreated = models.datetime.now(),
                               dateUpdated = models.datetime.now(), xCoordinates = , yCoordinates = 0)
        
class Query:
    """A query that a widget stores and periodically submits to the database.
    Can access one or more tables in the database. Verification needed.
    """
    pass

class Widget(models.Model):
    """A single sub-display that stores a query to be submitted to the database, and handles the displaying of the resulting data.
    """
    belongTo = models.ForeignKey(Dashboard)
    creator = models.CharField(max_length=50)
    query = models.CharField(max_length=200)
    dateCreated = models.DateTimeField('created')
    dateUpdated = models.DateTimeField('last update')
    xCoordinates = models.positiveIntegerField()
    yCoordinates = models.positiveIntegerField()
    

class Kit(models.Model):
    """A collection of widgets that can all be added to the dashboard at once. Kits store multiple widgets by storing each widget's
    ID into a list
    """
    name = models.CharField(max_length=30)
    creator = models.CharField(max_length=50)
    dateCreated = models.DateTimeField('created')
    widgetList = [] 
    
#Data models

class DataEntry(models.Model):
    """A base class for all data entries. Contains a date at which the entry was recorded
    """
    recorded = models.DateTimeField('recorded')

class Price(DataEntry):
    """Super-class for different price models in the database
    """
    price = models.FloatField(max_digits = 6, decimal_places = 2)

class StockPrice(Price):
    """Stores a price of a share of Edison International's (EIX) stock on the NYSE market at one time.
    Recorded in US$/share
    """
    pass

class BondPrice(Price):
    """The daily trading price for EME and subsidiary bonds.
    Recorded in US$
    """
    company = models.CharField(max_length = 50)
    
class PowerOutput(Price):
    """A statistic for the electricity generated in one day by one of EMG's generation units.
    Recorded in megawatts/hour
    """
    genunit = models.CharField(max_length = 50)
    unittype = models.CharField(max_length = 20)

class ElectricityPrice(Price):
    """The market price for electricity at designated ISO zone/hub.
    Recorded in US$/megawatt/hour
    """
    iso = models.CharField(max_length = 20)

class NaturalGasPrice(Price):
    """The market price for natural gas at the specified delivery hub.
    Recorded in US$/MMBTU
    """
    iso = models.CharField(max_length = 20)

class CoalPrice(Price):
    """The market price for coal by coal type.
    Recorded in US$/short ton
    """
    coaltype = models.CharField(max_length = 20)

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

class SubsidiaryBalance(DataEntry):
    """The cash position of the designated EMG subsidiary
    Recorded in US$
    """
    balance = models.FloatField(max_digits = 6, decimal_places = 2)
    company = models.CharField(max_length = 50)

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
    profit = models.FloatField(max_digits = 16, decimal_places = 2)
    expenditures = models.FloatField(max_digits = 16, decimal_places = 2)
    netprofit = models.FloatField(max_digits = 16, decimal_places = 2)

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
    margin = models.FloatField(max_digits = 16, decimal_places = 2)