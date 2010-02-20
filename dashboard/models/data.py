from django.db import models

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
        
class StockSymbolDescription(models.Model):
    symbol = models.CharField(max_length=4)
    company_name = models.CharField(max_length=200)