from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
import Image, ImageFont, ImageDraw
from django.conf import settings
from datetime import datetime, timedelta
from models import *

"""
def graph_view(request):
    #Load the image to be displayed, resize it to the parameters
    im = Image.open("C:/Users/Alex/Documents/Inf 191/emgdashboard/dashboard/Awesome.png")
    try:
        #Retrieve the size of the image, assuming width and height are separate parameters
        width = int(request.GET['width'])
        height = int(request.GET['height'])
        size = (width, height)

        #Retrieve the left-most and right-most times
        earliesttime = DateTime.datetime(request.GET['lefttime'])
        latesttime = DateTime.datetimeP(request.GET['righttime'])

        #Get the model and property to query
        model1 = String(request.GET['model1'])
        model1prop = String(request.GET['model1prop'])
    except:
        size = im.size

    query_model = globals()[model1]()
    queryset = query_model.objects_by_first_order_option(model1prop) 
    im = im.resize(size)

    #Create and return response with image
    response = HttpResponse(mimetype="image/png")
    im.save(response, "PNG")
    return response
"""

def line_graph_view(request):
    """Renders a line graph from data passed via an HttpRequest
    A request must include the following parameters:
        width: the width in pixels of the graph window
        height: the height in pixels of the graph window
        lefttime: the earliest time that will appear on the x-axis
        righttime: the latest time that will appear on the x-axis
        modeli: the table in the database to retrieve information from. Request can contain multiple modeli's,
            but each must be numbered sequentially(model1, model2, model3, etc.)
        modeliprop: the value to filter database queries by (assumed to be the value of the first order option).
            Requests can contain multiple modeliprop's, but each must correspond to a modeli (model1prop, model2prop, etc.)
        zoom: the value of the zoom, passed as a string. Zoom can be hours, days, weeks, months, or years
    """
    #Vertical Margins for the widget's display
    TOP_MARGIN = 20
    BOTTOM_MARGIN = 20
    XLABEL_MARGIN = 30

    #Horizontal Margins for the widget's display
    LEFT_MARGIN = 20
    RIGHT_MARGIN = 20
    YLABEL_MARGIN = 33

    #Canvas Dimensions
    CANVASX = 600
    CANVASY = 400

    #Axis value counts
    XAXIS_COUNT = 5
    YAXIS_COUNT = 9

    # Current y range under display
    #TODO: Check min, max values against YTOP and YBOTTOM
    YTOP = 10
    YBOTTOM = 0
    
    #Create a new image to display, as well as an ImageDraw object
    im = Image.new('RGBA', (CANVASX, CANVASY), (0, 0, 0, 0)) # Create a blank image
    draw = ImageDraw.Draw(im) # Create a draw object
    
    #Retrieve the size of the image, assuming width and height are separate parameters
    width = 600
    height = 400
    size = (width, height)

    #Retrieve the left-most and right-most times
    earliesttime = datetime(2010,01,01,00,00,00)
    latesttime = datetime(2010,02,01,00,00,00)
    #Milliseconds between the latest and earliest time
    duration = (latesttime-earliesttime).days*24*60*60*1000 + (latesttime-earliesttime).seconds*1000 + int((latesttime-earliesttime).microseconds/1000)
    zoom = "hours"
    xaxisvalues = [] #The dates to display on the x-axis

    #Get the model and property to query
    model1 = 'StockPrice'
    model1prop = 'EIX'

    #Submit the query and capture the resulting QuerySet
    query_model = globals()[model1]()
    query_set = query_model.objects_by_first_order_option(model1prop)

    #Filter query results by time, selecting only those that fall within the requested times
    filtered_results = [(float(entry.price), entry.time) for entry in query_set if earliesttime <= entry.time <= latesttime]


    #Determine times to label x-axis with 
    if(zoom == "hours"):
        tempduration = int((latesttime+timedelta(hours=1)-earliesttime).days * 24) + 1
        xaxisvalues = [earliesttime + timedelta(hours=i) for i in range(tempduration)]
    elif(zoom == "days"):
        tempduration = (latesttime+timedelta(days=1)-earliesttime).days + 1
        xaxisvalues = [earliesttime + timedelta(days=i) for i in range(tempduration)]
    elif(zoom == "weeks"):
        tempduration = int((latesttime+timedelta(weeks=1)-earliesttime).days / 7) + 1
        xaxisvalues = [earliesttime + timedelta(weeks=i) for i in range(tempduration)]
    elif(zoom == "months"):
        #If the latest month is after or the same as the earliest month, count the difference between the months, plus
        #12 times the number of intervening years
        if(latesttime.month >= earliesttime.month):
            tempduration = (latesttime.year-earliesttime.year)*12 + latesttime.month-earliesttime.month
        #If the latest month is before the earliest month, on a later year, count 12 times the number of years minus 1,
        #the months to the latest date since the start of the latest year, and the months from the starting month to the end of that year
        else:
            tempduration = (latesttime.year-earliesttime.year-1)*12 + latesttime.month + (12 - earliesttime.month)
        tempduration+=1
        tempyear = latesttime.year
        tempmonth = latesttime.month
        #For each month in the duration, create a new date time, calculating the month and the year
        for i in range(tempduration):
            xaxisvalues.insert(0, datetime(tempyear, tempmonth, 1, 0, 0, 0))
            tempmonth-=1
            if(tempmonth<1):
                tempmonth=12
                tempyear-=1
    else:  #zoom == years
        tempduration = latesttime.year-earliesttime.year + 1
        tempyear = latesttime.year
        for i in range(tempduration):
            xaxisvalues.insert(0, datetime(tempyear, 1, 1, 0, 0, 0))
            tempyear-=1

        
    #If there are too many x-axis values, scale
    if(len(xaxisvalues)>XAXIS_COUNT):
        xaxisvalues = []
        xincrement = timedelta(milliseconds = duration/XAXIS_COUNT)
        incrementdate = latesttime
        for i in range(XAXIS_COUNT):
            xaxisvalues.insert(0, incrementdate)
            incrementdate = incrementdate - xincrement

    #Determine the y-axis values
    yvalues = filtered_results
    yvalues.sort()
    minyvalue = yvalues[0][0]
    maxyvalue = yvalues[len(filtered_results)-1][0]
    yspan = maxyvalue-minyvalue
    yincrement = yspan/YAXIS_COUNT
    yaxisvalues = []
    for i in range(YAXIS_COUNT):
        yaxisvalues.append(maxyvalue - yincrement*i)

    
    #Draw axes
    #x axis
    draw.line((YLABEL_MARGIN, im.size[1]-XLABEL_MARGIN, im.size[0], im.size[1]-30), fill="black")
    increment = im.size[0]/len(xaxisvalues)
    if(zoom == "years"):
        for i in range(len(xaxisvalues)):
            draw.text((increment*i + YLABEL_MARGIN, im.size[1]-25), str(xaxisvalues[i].year), fill = "black")
            draw.line((increment*i + YLABEL_MARGIN, im.size[1]-XLABEL_MARGIN, increment*i + YLABEL_MARGIN, im.size[1]-XLABEL_MARGIN-10), fill = "black")
    elif(zoom == "months"):
        for i in range(len(xaxisvalues)):
            draw.text((increment*i + YLABEL_MARGIN, im.size[1]-25), "%s/%s" % (str(xaxisvalues[i].month), str(xaxisvalues[i].year)), fill = "black")
            draw.line((increment*i + YLABEL_MARGIN, im.size[1]-XLABEL_MARGIN, increment*i + YLABEL_MARGIN, im.size[1]-XLABEL_MARGIN-10), fill = "black")
    else:
        for i in range(len(xaxisvalues)):
            draw.text((increment*i + YLABEL_MARGIN, im.size[1]-25), "%s/%s/%s" % (str(xaxisvalues[i].month), str(xaxisvalues[i].day), str(xaxisvalues[i].year)), fill = "black")
            draw.text((increment*i + YLABEL_MARGIN, im.size[1]-15), "%02d:%02d:%02d" % (xaxisvalues[i].hour, xaxisvalues[i].minute, xaxisvalues[i].second), fill = "black")
            draw.line((increment*i + YLABEL_MARGIN, im.size[1]-XLABEL_MARGIN, increment*i + YLABEL_MARGIN, im.size[1]-XLABEL_MARGIN-10), fill = "black")

    #y axis
    draw.line((YLABEL_MARGIN, 0, YLABEL_MARGIN, im.size[1] - XLABEL_MARGIN), fill = "black")
    increment = im.size[1]/len(yaxisvalues)
    for i in range(len(yaxisvalues)):
        draw.text((0, increment*i), "%.2f" % yaxisvalues[i], fill = "black")
        draw.line((YLABEL_MARGIN, increment*i, YLABEL_MARGIN + 10, increment*i), fill = "black")

    #Determine scale
    yscale = (im.size[1]-(TOP_MARGIN+BOTTOM_MARGIN+XLABEL_MARGIN))/(yspan)
    
    #Defining xscale as we defined yscale resolves to 0 in most cases. Therefore, it is resolved differently.
    #The numerator of xscale is defined below, and is only divided by the denominator when xpos is evaluated
    #in the iteration below
    xscale = im.size[0]-(LEFT_MARGIN+RIGHT_MARGIN+YLABEL_MARGIN)
    #Sort the list by time to be parsed
    filtered_results.sort(lambda x, y: cmp(x[1], y[1]))
    #Iterate through the query set, rendering each data point
    for datapoint in filtered_results:
        timelapse = latesttime-datapoint[1]
        xpos = ((timelapse.days*24*60*60*1000 + timelapse.seconds*1000 + int(timelapse.microseconds/1000)) * xscale /duration)+ LEFT_MARGIN + YLABEL_MARGIN
        ypos = (maxyvalue-datapoint[0])*yscale + TOP_MARGIN
        draw.rectangle((xpos - 1, ypos - 1, xpos + 1, ypos + 1), fill="red")
    #Iterate through the query set, drawing a line between each pair of points
    for i in range(len(filtered_results)-1):
        timelapse = latesttime-filtered_results[i][1]
        xpos1 = ((timelapse.days*24*60*60*1000 + timelapse.seconds*1000 + int(timelapse.microseconds/1000)) * xscale /duration)+ LEFT_MARGIN + YLABEL_MARGIN
        ypos1 = (maxyvalue-filtered_results[i][0])*yscale + TOP_MARGIN
        timelapse = latesttime-filtered_results[i+1][1]
        xpos2 = ((timelapse.days*24*60*60*1000 + timelapse.seconds*1000 + int(timelapse.microseconds/1000)) * xscale /duration)+ LEFT_MARGIN + YLABEL_MARGIN
        ypos2 = (maxyvalue-filtered_results[i+1][0])*yscale + TOP_MARGIN
        draw.line((xpos1, ypos1, xpos2, ypos2), fill = "red")
        
    del draw
    im = im.resize(size)

    #Create and return response with image
    #TODO: Cut into 3 shingles, return json file if max y value is above top y point
    response = HttpResponse(mimetype="image/png")
    im.save(response, "PNG")
    return response        


def addWidget(request):
    #return render_to_response('htmlTemplate/index.html')
    return HttpResponseRedirect('../')
    #return render_to_response('index.html')

def index(request):
    return render_to_response('index.html')
    