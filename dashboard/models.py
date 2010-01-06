from django.db import models
from datetime import datetime


class Dashboard(models.Model):
    #leftColumnWidgets = []
    #rightColumnWidgets = []
    sharedWidgets = []
    lastLogin = models.datetime.now()
  
    def add(self, widget, column):
        self.leftColumnWidgets.append(widget)
  

class Widget(models.Model):
    name = models.CharField(max_length=30)
    belongTo = models.ForeignKey(Dashboard)
    creator = models.CharField(max_length=50)
    dateCreated = models.datetime.now()
    dateUpdated = models.datetime.now()
    xCoordinates = models.positiveIntegerField()
    yCoordinates = models.positiveIntegerField()
    

class Kit(models.Model):
    name = models.CharField(max_length=30)
    creator = models.CharField(max_length=50)
    dateCreated = models.datetime.now()
    dateUpdated = models.datetime.now()
    widgetList = [] 
    
