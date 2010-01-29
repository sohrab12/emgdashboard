from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
import Image, ImageFont, ImageDraw
from django.conf import settings
from datetime import datetime, timedelta
from models import *
from django.template import RequestContext
 
def widget_properties(request, widget_id):
    widget=get_object_or_404(LineWidget, pk=widget_id)
    return render_to_response('widgetframe.html', {'widget':widget})
 
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
topy: The maximum y value of the graph
bottomy: the minimum y value of the graph
graphplace: the number of the chunk to return in response.
graphchunks: the total number of chunks to split the graph into.
"""
    #Vertical Margins for the widget's display
    TOP_MARGIN = 20
    BOTTOM_MARGIN = 20
    XLABEL_MARGIN = 30
 
    #Horizontal Margins for the widget's display
    LEFT_MARGIN = 0
    RIGHT_MARGIN = 0
    YLABEL_MARGIN = 0
 
    #Axis value counts
    XAXIS_COUNT = 5
    YAXIS_COUNT = 9
 
    # Current y range under display
    #TODO: Check min, max values against YTOP and YBOTTOM
    try:
        ytop = int(request.GET['ytop'])
        ybottom = int(request.GET['ybottom'])
    except:
        ytop = 10
        ybottom = 0
 
    #Number of chunks to return the image in
    try:
        chunk_place = int(request.GET['chunkplace'])
        chunk_count = int(request.GET['chunkcount'])
    except:
        chunk_place = 1
        chunk_count = 1
 
        #Image
    try:
        image_width = int(request.GET['width'])
        image_height = int(request.GET['height'])
    except:
        image_width = 600
        image_height = 400
    
    #Create a new image to display, as well as an ImageDraw object
    im = Image.new('RGBA', (image_width, image_height), (255, 255, 255)) # Create a blank image
    draw = ImageDraw.Draw(im) # Create a draw object
 
    #Retrieve the left-most and right-most times
    try:
        #Separate the left date's date and time
        leftdate = request.GET['lefttime'].split(" ")[0].split("-")
        lefttime = request.GET['lefttime'].split(" ")[1].split(":")
        #Parse the left date
        leftyear = int(leftdate[0])
        leftmonth = int(leftdate[1])
        leftday = int(leftdate[2])
        #Parse the left time
        lefthour = int(lefttime[0])
        leftmin = int(lefttime[1])
        leftsec = int(lefttime[2])

        #Separate the right date's date and time
        rightdate = request.GET['righttime'].split(" ")[0].split("-")
        righttime = request.GET['righttime'].split(" ")[1].split(":")
        #Parse the right date
        rightyear = int(rightdate[0])
        rightmonth = int(rightdate[1])
        rightday = int(rightdate[2])
        #Parse the right time
        righthour = int(righttime[0])
        rightmin = int(righttime[1])
        rightsec = int(righttime[2])

        earliesttime = datetime(leftyear, leftmonth, leftday, lefthour, leftmin, leftsec)        
        latesttime = datetime(rightyear, rightmonth, rightday, righthour, rightmin, rightsec)
    except:
        earliesttime = datetime(2010,01,01,00,00,00)
        latesttime = datetime(2010,02,01,00,00,00)
    #If the two dates are the same, set the earliest time back by a day, to avoid math errors when calculating the x-axis scale
    if earliesttime == latesttime:
        earliesttime = earliesttime - timedelta(days=1)
    #Milliseconds between the latest and earliest time
    duration = (latesttime-earliesttime).days*24*60*60*1000 + (latesttime-earliesttime).seconds*1000 + int((latesttime-earliesttime).microseconds/1000)
    try:
        zoom = request.GET['zoom']
    except:
        zoom = "hours"
    xaxisvalues = [] #The dates to display on the x-axis
 
    #Get the models and propertys to query
    models = []
    for i in range(1000):
        if i > 0:
            try:
                model = request.GET['model' + str(i)]
                modelprop = request.GET['model' + str(i) + 'prop']
                models.append((model, modelprop))
            except:
                break
 
    #Submit the query and capture the resulting QuerySet
    query_results = []
    for modelset in models:
        query_model = globals()[modelset[0]]()
        query_set = query_model.objects_by_first_order_option(modelset[1])
        #Filter query results by time, selecting only those that fall within the requested times
        filtered_results = [(float(entry.price), entry.time) for entry in query_set if earliesttime <= entry.time <= latesttime]
        query_results.append(filtered_results)

    #If there are no results, return an HttpResponse with a blank graph
    """
    if len(query_results) == 0:
        draw.line((YLABEL_MARGIN+LEFT_MARGIN, im.size[1]-XLABEL_MARGIN, im.size[0]-RIGHT_MARGIN, im.size[1]-XLABEL_MARGIN), fill="black")
        draw.line((YLABEL_MARGIN+LEFT_MARGIN, im.size[1]-XLABEL_MARGIN, YLABEL_MARGIN+LEFT_MARGIN, im.size[1]-XLABEL_MARGIN-10), fill="black")
        draw.line((im.size[0]-RIGHT_MARGIN, im.size[1]-XLABEL_MARGIN, im.size[0]-RIGHT_MARGIN, im.size[1]-XLABEL_MARGIN-10), fill="black")
        if(zoom == "years"):
            draw.text((YLABEL_MARGIN+LEFT_MARGIN, im.size[1]-25), str(earliesttime.year), fill="black")
            draw.text((im.size[0]-RIGHT_MARGIN, im.size[1]-25), str(latesttime.year), fill="black")
        elif(zoom == "months"):
            draw.text((YLABEL_MARGIN+LEFT_MARGIN, im.size[1]-25), "%s/%s" % (str(earliesttime.month), str("%s/%s" % (str(xaxisvalues[i].month), str(earliesttime.year)).year)), fill="black")
            draw.text((im.size[0]-RIGHT_MARGIN, im.size[1]-25),"%s/%s" % (str(latesttime.month), str(latesttime.year)), fill="black")
        else:
            draw.text((YLABEL_MARGIN+LEFT_MARGIN, im.size[1]-25), str(earliesttime.date), fill="black")
            draw.text((YLABEL_MARGIN+LEFT_MARGIN, im.size[1]-15), str(earliesttime.time), fill="black")
            draw.text((im.size[0]-RIGHT_MARGIN, im.size[1]-25), str(latesttime.date), fill="black")
            draw.text((im.size[0]-RIGHT_MARGIN, im.size[1]-15), str(latesttime.time), fill="black")
        chunk_width = im.size[0]/chunk_count
        chunk = im.crop(((chunk_place-1)*chunk_width, 0, chunk_place*chunk_width, im.size[1]))
        response = HttpResponse(mimetype="image/png")
        chunk.save(response, "PNG")
        return response
    """
 
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
    else: #zoom == years
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
 
    xaxisvalues.reverse()
    #Draw axes
    #x axis
    draw.line((YLABEL_MARGIN+LEFT_MARGIN, im.size[1]-XLABEL_MARGIN, im.size[0]-RIGHT_MARGIN, im.size[1]-XLABEL_MARGIN), fill="black")
    increment = (im.size[0]-RIGHT_MARGIN-LEFT_MARGIN)/len(xaxisvalues)
    if(zoom == "years"):
        for i in range(len(xaxisvalues)):
            draw.text((im.size[0]-increment*i + YLABEL_MARGIN, im.size[1]-25), str(xaxisvalues[i].year), fill = "black")
            draw.line((im.size[0]-increment*i-1 + YLABEL_MARGIN, im.size[1]-XLABEL_MARGIN, im.size[0]-increment*i-1 + YLABEL_MARGIN, im.size[1]-XLABEL_MARGIN-10), fill = "black")
    elif(zoom == "months"):
        for i in range(len(xaxisvalues)):
            draw.text((im.size[0]-increment*i + YLABEL_MARGIN, im.size[1]-25), "%s/%s" % (str(xaxisvalues[i].month), str(xaxisvalues[i].year)), fill = "black")
            draw.line((im.size[0]-increment*i-1 + YLABEL_MARGIN, im.size[1]-XLABEL_MARGIN, im.size[0]-increment*i-1 + YLABEL_MARGIN, im.size[1]-XLABEL_MARGIN-10), fill = "black")
    else:
        for i in range(len(xaxisvalues)):
            draw.text((im.size[0]-increment*i + YLABEL_MARGIN, im.size[1]-25), "%s/%s/%s" % (str(xaxisvalues[i].month), str(xaxisvalues[i].day), str(xaxisvalues[i].year)), fill = "black")
            draw.text((im.size[0]-increment*i + YLABEL_MARGIN, im.size[1]-15), "%02d:%02d:%02d" % (xaxisvalues[i].hour, xaxisvalues[i].minute, xaxisvalues[i].second), fill = "black")
            draw.line((im.size[0]-increment*i-1 + YLABEL_MARGIN, im.size[1]-XLABEL_MARGIN, im.size[0]-increment*i-1 + YLABEL_MARGIN, im.size[1]-XLABEL_MARGIN-10), fill = "black")
 
 
 
 
    
    
    #y axis
    """
draw.line((YLABEL_MARGIN, 0, YLABEL_MARGIN, im.size[1] - XLABEL_MARGIN), fill = "black")
increment = im.size[1]/len(yaxisvalues)
for i in range(len(yaxisvalues)):
draw.text((0, increment*i), "%.2f" % yaxisvalues[i], fill = "black")
draw.line((YLABEL_MARGIN, increment*i, YLABEL_MARGIN + 10, increment*i), fill = "black")
"""
    
    #Defining xscale as we defined yscale resolves to 0 in most cases. Therefore, it is resolved differently.
    #The numerator of xscale is defined below, and is only divided by the denominator when xpos is evaluated
    #in the iteration below
    xscale = im.size[0]-(LEFT_MARGIN+RIGHT_MARGIN+YLABEL_MARGIN)
 
    #For each model, determine its y scale, then draw the data points, only if that model has data points
    for result_set in query_results:
        if len(result_set) !=0:
            #Determine the y-axis values
            yvalues = result_set
            yvalues.sort(lambda x, y: cmp(x[0], y[0]))
            minyvalue = min(yvalues)[0]
            maxyvalue = max(yvalues)[0]
            yspan = maxyvalue-minyvalue
            #If the two values are the same, set the span to 1 to avoid math errors in evaluating the y-axis scale
            if yspan == 0:
                yspan = 1
            yincrement = yspan/YAXIS_COUNT
            yaxisvalues = []
            for i in range(YAXIS_COUNT):
                yaxisvalues.append(maxyvalue - yincrement*i)
            
     
            #Determine scale
            yscale = (im.size[1]-(TOP_MARGIN+BOTTOM_MARGIN+XLABEL_MARGIN))/(yspan)
     
            #Sort the list by time to be parsed
            result_set.sort(lambda x, y: cmp(x[1], y[1]))
     
            #Iterate through the query set, rendering each data point
            for datapoint in result_set:
                timelapse = datapoint[1]-earliesttime
                xpos = ((timelapse.days*24*60*60*1000 + timelapse.seconds*1000 + int(timelapse.microseconds/1000)) * xscale /duration)+ LEFT_MARGIN + YLABEL_MARGIN
                ypos = (maxyvalue-datapoint[0])*yscale + TOP_MARGIN
                draw.rectangle((xpos - 1, ypos - 1, xpos + 1, ypos + 1), fill="red")
            #Iterate through the query set, drawing a line between each pair of points
            for i in range(len(result_set)-1):
                timelapse = result_set[i][1]-earliesttime
                xpos1 = ((timelapse.days*24*60*60*1000 + timelapse.seconds*1000 + int(timelapse.microseconds/1000)) * xscale /duration)+ LEFT_MARGIN + YLABEL_MARGIN
                ypos1 = (maxyvalue-result_set[i][0])*yscale + TOP_MARGIN
                timelapse = result_set[i+1][1]-earliesttime
                xpos2 = ((timelapse.days*24*60*60*1000 + timelapse.seconds*1000 + int(timelapse.microseconds/1000)) * xscale /duration)+ LEFT_MARGIN + YLABEL_MARGIN
                ypos2 = (maxyvalue-result_set[i+1][0])*yscale + TOP_MARGIN
                draw.line((xpos1, ypos1, xpos2, ypos2), fill = "red")
        
    del draw
    
    #Create and return response with image
    #TODO: Cut into 3 shingles, return json file if max y value is above top y point
    chunk_width = im.size[0]/chunk_count
    chunk = im.crop(((chunk_place-1)*chunk_width, 0, chunk_place*chunk_width, im.size[1]))
    response = HttpResponse(mimetype="image/png")
    chunk.save(response, "PNG")
    return response
 
 
def addWidget(request):
    return HttpResponseRedirect('/dashboard')

def index(request):
    return render_to_response('index.html')

def export_widget(request):
    widget_ids = request.GET.values()
    for widget_id in widget_ids:
        widget = get_object_or_404(Widget, pk=widget_id)
        response = HttpResponse(widget.widget_type())
        #response = HttpResponse(widget.widget_type)
        return response
