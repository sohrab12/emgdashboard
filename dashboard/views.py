from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
import Image, ImageFont, ImageDraw
from django.conf import settings
from datetime import datetime, timedelta
from models import *
from django.template import RequestContext
 
def widget_properties(request, widget_id):
    #Get the properties of the widget to render the widgetframe template with
    widget = get_object_or_404(Widget, pk=widget_id)
 
    #Calculate the dates that the slider can be set to based on start time, end time, and zoom.
    #Append these values to a list
    typedwidget = widget.widget_type()
    earliesttime = typedwidget.sliderstartdate
    latesttime = typedwidget.sliderenddate
    zoom = typedwidget.zoom
    dates = []
 
    #Calculate dates
    if(zoom == "hours"):
        #Tempduration = number of hours between the first and last dates
        tempduration = int((latesttime+timedelta(hours=1)-earliesttime).days * 24)
        #For each hour, increment earliestdate by one hour and add it to the list
        dates = [earliesttime + timedelta(hours=i) for i in range(tempduration)]
    elif(zoom == "days"):
        tempduration = int((latesttime+timedelta(days=1)-earliesttime).days)
        dates = [earliesttime + timedelta(days=i) for i in range(tempduration)]
    elif(zoom == "weeks"):
        tempduration = int((latesttime+timedelta(weeks=1)-earliesttime).days / 7)
        dates = [earliesttime + timedelta(weeks=i) for i in range(tempduration)]
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
            dates.insert(0, datetime(tempyear, tempmonth, 1, 0, 0, 0))
            tempmonth-=1
            if(tempmonth<1):
                tempmonth=12
                tempyear-=1
    else: #zoom == years
        tempduration = latesttime.year-earliesttime.year + 1
        tempyear = latesttime.year
        for i in range(tempduration):
            dates.insert(0, datetime(tempyear, 1, 1, 0, 0, 0))
            tempyear-=1
    return render_to_response('widgetframe.html', {'widget':widget, 'typedwidget':typedwidget, 'dates': dates})
        
def line_graph_view(request, widget_id):
    """Renders a line graph from data passed via an HttpRequest
A request must include the following parameters:
width: the width in pixels of the graph window
height: the height in pixels of the graph window
lefttime: the earliest time that will appear on the x-axis
righttime: the latest time that will appear on the x-axis
modeli: the table in the database to retrieve information from. Request can contain multiple modeli's,
but each must be numbered sequentially(model1, model2, model3, etc.)
modelioption: the value to filter database queries by (assumed to be the value of the first order option).
Requests can contain multiple modelioption's, but each must correspond to a modeli (model1option, model2option, etc.)
zoom: the value of the zoom, passed as a string. Zoom can be hours, days, weeks, months, or years
topy: The maximum y value of the graph
bottomy: the minimum y value of the graph
graphplace: the number of the chunk to return in response.
graphchunks: the total number of chunks to split the graph into.
"""
    #Vertical Margins for the widget's display
    KEY_MARGIN = 30
    TOP_MARGIN = 5
    BOTTOM_MARGIN = KEY_MARGIN+0
    XLABEL_MARGIN = 30
 
    #Horizontal Margins for the widget's display
    LEFT_MARGIN = 2
    RIGHT_MARGIN = 2
    YLABEL_MARGIN = 35
 
    #Axis value counts
    XAXIS_COUNT = 3
    YAXIS_COUNT = 9
 
    # Current y range under display
    #TODO: Check min, max values against YTOP and YBOTTOM
 
    line_widget = LineWidget.objects.get(parent_widget = widget_id)
    try:
        maxyvalue = int(request.GET['ytop'])
        minyvalue = int(request.GET['ybottom'])
        mainunits = line_widget.firstunit
    except:
        maxyvalue = 30
        minyvalue = 0
 
    # Current y range under display for second axis
    #TODO: Check min, max values against YTOP and YBOTTOM
    try:
        altmaxyvalue = int(request.GET['ytop'])
        altminyvalue = int(request.GET['ybottom'])
        altunits = line_widget.secondunit
    except:
        altmaxyvalue = None
        altminyvalue = None
 
    #Number of chunks to return the image in
    try:
        chunk_place = int(request.GET['chunkplace'])
        chunk_count = int(request.GET['chunkcount'])
    except:
        chunk_place = 1
        chunk_count = 3
 
    #Image size
    try:
        image_width = int(request.GET['width'])
        image_height = int(request.GET['height'])
    except:
        image_width = 600
        image_height = 400
    
    #Create a new image to display, as well as an ImageDraw object
    if chunk_place == 0 or chunk_place == -1:
        im = Image.new('RGBA', (YLABEL_MARGIN, image_height), (255, 255, 255)) # Create a blank image
    else:
        im = Image.new('RGBA', (image_width, image_height), (255, 255, 255)) # Create a blank image
    draw = ImageDraw.Draw(im) # Create a draw object
 
    #Determine values for the y-scale
    yspan = maxyvalue-minyvalue
    #If the two values are the same, set the span to 1 to avoid math errors in evaluating the y-axis scale
    if yspan == 0:
        yspan = 1
    yincrement = yspan/YAXIS_COUNT
    yaxisvalues = []
    for i in range(YAXIS_COUNT):
        yaxisvalues.append(maxyvalue - yincrement*i)
    yscale = (im.size[1]-(TOP_MARGIN+BOTTOM_MARGIN+XLABEL_MARGIN))/(yspan)
 
    
    altyaxisvalues = []
    #Determine values for second y-scale if one exists
    if(altmaxyvalue):
        altyspan = altmaxyvalue-altminyvalue
        #If the two values are the same, set the span to 1 to avoid math errors in evaluating the y-axis scale
        if altyspan == 0:
            altyspan = 1
        altyincrement = altyspan/YAXIS_COUNT
        for i in range(YAXIS_COUNT):
            altyaxisvalues.append(altmaxyvalue - altyincrement*i)
        altyscale = (im.size[1]-(TOP_MARGIN+BOTTOM_MARGIN+XLABEL_MARGIN))/(altyspan)
 
    #If this request's chunk_place is 0, we don't need to make any calls to the database. Just render the appropriate axis and return.
    #If the chunk_place is 0, render the y-axis for the widget and return it as a response
    if chunk_place == 0:
        draw.line((LEFT_MARGIN, TOP_MARGIN, LEFT_MARGIN, im.size[1] - XLABEL_MARGIN - BOTTOM_MARGIN), fill = "black")
        increment = (im.size[1]-TOP_MARGIN - BOTTOM_MARGIN - XLABEL_MARGIN)/len(yaxisvalues)
        for i in range(len(yaxisvalues)):
            draw.text((LEFT_MARGIN+2, increment*i + TOP_MARGIN), "%.2f" % yaxisvalues[i], fill = "black")
            draw.line((LEFT_MARGIN, increment*i + TOP_MARGIN, LEFT_MARGIN + 10, increment*i + TOP_MARGIN), fill = "black")
        draw.line((LEFT_MARGIN, im.size[1]-XLABEL_MARGIN-BOTTOM_MARGIN, YLABEL_MARGIN+LEFT_MARGIN, im.size[1]-XLABEL_MARGIN-BOTTOM_MARGIN), fill="black")
        response = HttpResponse(mimetype="image/png")
        im.save(response, "PNG")
        return response
 
    #If the chunk_place is -1, render the second y-axis for the widget and return it as a response
    if chunk_place == -1:
        draw.line((im.size[0]-RIGHT_MARGIN, TOP_MARGIN, im.size[0]-RIGHT_MARGIN, im.size[1] - XLABEL_MARGIN - BOTTOM_MARGIN), fill = "black")
        increment = (im.size[1]-TOP_MARGIN - BOTTOM_MARGIN - XLABEL_MARGIN)/len(altyaxisvalues)
        for i in range(len(altyaxisvalues)):
            draw.text((im.size[0]-RIGHT_MARGIN-32, increment*i + TOP_MARGIN), "%.2f" % altyaxisvalues[i], fill = "black")
            draw.line((im.size[0]-RIGHT_MARGIN, increment*i + TOP_MARGIN, im.size[0]-RIGHT_MARGIN - 10, increment*i + TOP_MARGIN), fill = "black")
        draw.line((im.size[0]-RIGHT_MARGIN, im.size[1]-XLABEL_MARGIN-BOTTOM_MARGIN, im.size[0]-RIGHT_MARGIN-YLABEL_MARGIN, im.size[1]-XLABEL_MARGIN-BOTTOM_MARGIN), fill="black")
        response = HttpResponse(mimetype="image/png")
        im.save(response, "PNG")
        return response
        
 
    #Otherwise, we continue.
    #Retrieve the left-most and right-most timestry:
    try:
        earliesttime = line_widget.startdate
        latesttime = line_widget.enddate
    except:
        earliesttime = datetime(2010,01,01,00,00,00)
        latesttime = datetime(2010,02,01,00,00,00)
    #If the two dates are the same, set the earliest time back by a day, to avoid math errors when calculating the x-axis scale
    if earliesttime == latesttime:
        earliesttime = earliesttime - timedelta(days=1)
    #Milliseconds between the latest and earliest time
    duration = (latesttime-earliesttime).days*24*60*60*1000 + (latesttime-earliesttime).seconds*1000 + int((latesttime-earliesttime).microseconds/1000)
    try:
        zoom = line_widget.zoom
    except:
        zoom = "months"
    xaxisvalues = [] #The dates to display on the x-axis
 
    #Get the the queries that belong to this model
    parent_widget = Widget.objects.get(pk=widget_id)
    queries = parent_widget.get_queries()
    #Run each query
    query_results = []
    for query in queries:
        query_set = query.run()
        #Filter query results by time, selecting only those that fall within the requested times
        filtered_results = [(float(entry[0]), entry[1], globals()[query.table].get_units(), query.table, query.first_order_option) for entry in query_set if earliesttime <= entry[1] <= latesttime]
        query_results.append(filtered_results)
    #Determine times to label x-axis with
    if(zoom == "hours"):
        tempduration = int((latesttime+timedelta(hours=1)-earliesttime).days * 24)
        xaxisvalues = [earliesttime + timedelta(hours=i) for i in range(tempduration)]
    elif(zoom == "days"):
        tempduration = int((latesttime+timedelta(days=1)-earliesttime).days)
        xaxisvalues = [earliesttime + timedelta(days=i) for i in range(tempduration)]
    elif(zoom == "weeks"):
        tempduration = int((latesttime+timedelta(weeks=1)-earliesttime).days / 7)
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
    
    #Draw x axis
    draw.line((0, im.size[1]-XLABEL_MARGIN-BOTTOM_MARGIN, im.size[0]-RIGHT_MARGIN, im.size[1]-XLABEL_MARGIN-BOTTOM_MARGIN), fill="black")
    increment = (im.size[0]-RIGHT_MARGIN-LEFT_MARGIN)/len(xaxisvalues)
    if(zoom == "years"):
        for i in range(len(xaxisvalues)):
            draw.text((LEFT_MARGIN + increment*(i), im.size[1]-BOTTOM_MARGIN-25), str(xaxisvalues[i].year), fill = "black")
            draw.line((LEFT_MARGIN + increment*(i) - 1, im.size[1]-XLABEL_MARGIN-BOTTOM_MARGIN, LEFT_MARGIN + increment*(i) - 1, im.size[1]-XLABEL_MARGIN-BOTTOM_MARGIN-10), fill = "black")
    elif(zoom == "months"):
        for i in range(len(xaxisvalues)):
            draw.text((LEFT_MARGIN + increment*(i), im.size[1]-BOTTOM_MARGIN-25), "%s/%s" % (str(xaxisvalues[i].month), str(xaxisvalues[i].year)), fill = "black")
            draw.line((LEFT_MARGIN + increment*(i) - 1, im.size[1]-XLABEL_MARGIN-BOTTOM_MARGIN, LEFT_MARGIN + increment*(i) - 1, im.size[1]-XLABEL_MARGIN-BOTTOM_MARGIN-10), fill = "black")
    else:
        for i in range(len(xaxisvalues)):
            draw.text((LEFT_MARGIN + increment*(i), im.size[1]-BOTTOM_MARGIN-25), "%s/%s/%s" % (str(xaxisvalues[i].month), str(xaxisvalues[i].day), str(xaxisvalues[i].year)), fill = "black")
            draw.text((LEFT_MARGIN + increment*(i), im.size[1]-BOTTOM_MARGIN-15), "%02d:%02d:%02d" % (xaxisvalues[i].hour, xaxisvalues[i].minute, xaxisvalues[i].second), fill = "black")
            draw.line((LEFT_MARGIN + increment*(i) - 1, im.size[1]-XLABEL_MARGIN-BOTTOM_MARGIN, LEFT_MARGIN + increment*(i) - 1, im.size[1]-XLABEL_MARGIN-BOTTOM_MARGIN-10), fill = "black")
 
    
    #Defining xscale as we defined yscale resolves to 0 in most cases. Therefore, it is resolved differently.
    #The numerator of xscale is defined below, and is only divided by the denominator when xpos is evaluated
    #in the iteration below
    xscale = im.size[0]-(LEFT_MARGIN+RIGHT_MARGIN+YLABEL_MARGIN)
 
    #For each model, draw the data points, only if that model has data points
    key_pos = 0
    for result_set in query_results:
     
            #Sort the list by time to be parsed
            result_set.sort(lambda x, y: cmp(x[1], y[1]))
            #If the units of this set are equal to the first unit, plot the points along the left y-axis.
            try:
                if result_set[0][2] == mainunits:
                    #Iterate through the query set, rendering each data point
                    for datapoint in result_set:
                        timelapse = datapoint[1]-earliesttime
                        xpos = ((timelapse.days*24*60*60*1000 + timelapse.seconds*1000 + int(timelapse.microseconds/1000)) * xscale /duration)+ LEFT_MARGIN
                        ypos = (maxyvalue-datapoint[0])*yscale + TOP_MARGIN
                        draw.rectangle((xpos - 1, ypos - 1, xpos + 1, ypos + 1), fill="red")
                    #Iterate through the query set, drawing a line between each pair of points
                    for i in range(len(result_set)-1):
                        timelapse = result_set[i][1]-earliesttime
                        xpos1 = ((timelapse.days*24*60*60*1000 + timelapse.seconds*1000 + int(timelapse.microseconds/1000)) * xscale /duration)+ LEFT_MARGIN
                        ypos1 = (maxyvalue-result_set[i][0])*yscale + TOP_MARGIN
                        timelapse = result_set[i+1][1]-earliesttime
                        xpos2 = ((timelapse.days*24*60*60*1000 + timelapse.seconds*1000 + int(timelapse.microseconds/1000)) * xscale /duration)+ LEFT_MARGIN
                        ypos2 = (maxyvalue-result_set[i+1][0])*yscale + TOP_MARGIN
                        draw.line((xpos1, ypos1, xpos2, ypos2), fill = "red")
                #If the units are not equal to the first unit, plot them along the second axis
                else:
                    for datapoint in result_set:
                        timelapse = datapoint[1]-earliesttime
                        xpos = ((timelapse.days*24*60*60*1000 + timelapse.seconds*1000 + int(timelapse.microseconds/1000)) * xscale /duration)+ LEFT_MARGIN
                        ypos = (altmaxyvalue-datapoint[0])*altyscale + TOP_MARGIN
                        draw.rectangle((xpos - 1, ypos - 1, xpos + 1, ypos + 1), fill="red")
                    #Iterate through the query set, drawing a line between each pair of points
                    for i in range(len(result_set)-1):
                        timelapse = result_set[i][1]-earliesttime
                        xpos1 = ((timelapse.days*24*60*60*1000 + timelapse.seconds*1000 + int(timelapse.microseconds/1000)) * xscale /duration)+ LEFT_MARGIN
                        ypos1 = (altmaxyvalue-result_set[i][0])*altyscale + TOP_MARGIN
                        timelapse = result_set[i+1][1]-earliesttime
                        xpos2 = ((timelapse.days*24*60*60*1000 + timelapse.seconds*1000 + int(timelapse.microseconds/1000)) * xscale /duration)+ LEFT_MARGIN
                        ypos2 = (altmaxyvalue-result_set[i+1][0])*altyscale + TOP_MARGIN
                        draw.line((xpos1, ypos1, xpos2, ypos2), fill = "red")
                #Draw the key for the widget
                query_count = len(queries)
                draw.text((LEFT_MARGIN, (im.size[1]-BOTTOM_MARGIN) + (BOTTOM_MARGIN/query_count)*key_pos), result_set[0][4], fill = "black")
                draw.line((LEFT_MARGIN + 20, (im.size[1]-BOTTOM_MARGIN) + (BOTTOM_MARGIN/query_count)*key_pos + 5, LEFT_MARGIN + 30, (im.size[1]-BOTTOM_MARGIN) + (BOTTOM_MARGIN/query_count)*key_pos + 5), fill = "red")
                key_pos+=1
            #The query returned no results, so draw nothing.
            except:
                pass
        
    del draw
    
    #Create and return response with image
    #TODO: Cut into 3 shingles, return json file if max y value is above top y point
    chunk_width = (im.size[0]-YLABEL_MARGIN)/chunk_count
    chunk = im.crop(((chunk_place-1)*chunk_width, 0, chunk_place*chunk_width, im.size[1]))
    response = HttpResponse(mimetype="image/png")
    chunk.save(response, "PNG")
    return response
 
 
def addWidget(request):
    #Get the dashboard to add a widget to.
    dashboard_id = request.GET["dashboardID"]
    dashboard = objects.Dashboard.get(pk=dashboard_id)
    new_widget = dashboard.addWidget(0)
 
    #Add a typed widget corresponding to the new generic widget
    graphtype = request.GET["graphType"]
    zoom = request.GET["zoom"]
    earliesttime = datetime(2010,01,01,00,00,00)
    latesttime = datetime(2010,02,01,00,00,00)
    firstunit = "dollars"
    secondunit = "null"
    new_widget.add_typed_widget(graphtype, zoom, earliesttime, latesttime, firstunit, secondunit)
 
    #Make all the queries that need to be added to the database for the new widget
    queries = request.GET["queryInfo"]
    for query in queries:
        new_widget.add_query(query[0], query[1], query[2])
    return HttpResponseRedirect('/dashboard')

def extract_times(indate):
    """Takes a string representing a time stamp from the template, and scans it into a datetime object
    """
    vals = indate.split(" ")
    datevals = vals[0].split("-")
    year = int(datevals[0])
    month = int(datevals[1])
    day = int(datevals[2])
    timevals = vals[1].split(":")
    hour = int(timevals[0])
    min = int(timevals[1])
    sec = int(timevals[2])
    return datetime(year, month, day, hour, min, sec)

def slide_times(request):
    """Change the widget's start time and end time to reflect the values chosen by the slider
    """
    widget = Widget.objects.get(pk = request.POST["pk"])
    typed_widget = widget.widget_type()
    zoom = typed_widget.zoom
    #Get the start and end date strings from the request
    startstring = request.POST["start"]
    endstring = request.POST["end"]
    #Assign new start and end times to the widget in the database.
    typed_widget.startdate = extract_times(startstring)
    typed_widget.enddate = extract_times(endstring)
    typed_widget.save()
    return HttpResponse("Worked")

#Remove this widget and its queries from the database
def remove_widget(request):
    return HttpResponse("Working")

def index(request, dashboard_id):
    #p = get_object_or_404(StockPrice, pk=1)
    dash = get_object_or_404(Dashboard, pk=dashboard_id)
    stockList = StockPrice.objects.all().order_by('-symbol')
    widgets = Widget.objects.filter(belongTo=dash)
    no_widgets = (len(widgets) == 0)
    left_widget_bodies = [w.get_specialization().get_html() for w in widgets if w.x == 0]
    right_widget_bodies = [w.get_specialization().get_html() for w in widgets if w.x == 1]
    return render_to_response('index.html', {'stockList': stockList,
                                             'dashboard': dash,
                                             'no_widgets': no_widgets,
                                             'left_widget_bodies': left_widget_bodies,
                                             'right_widget_bodies': right_widget_bodies})
 
def export_widget(request):
    import xlwt # importing inside the view so that other functions work
                # on hosts without xlwt
    widget_ids = request.GET.values()
    for widget_id in widget_ids:
        widget = get_object_or_404(Widget, pk=widget_id)
        wb = xlwt.Workbook()
        for query in widget.get_queries():
            table = query.table
            rowcounter = -1
            ws = wb.add_sheet(str(query.property)+' Test Sheet')
            for table in globals()[query.table].objects.all().order_by('-symbol'):
                if (query.property == table.symbol):
                    #sym = table.symbol
                    rowcounter += 1
                    ws.write(rowcounter, 0, table.symbol)
                    ws.write(rowcounter, 1, table.price)
        response = HttpResponse(mimetype='application/vnd.ms-excel')
        filename = "test.xls"
        #filename = "%stest.xls" %sym
        response['Content-Disposition'] = 'attachment; filename='+filename
        #response['Content-Type'] = 'application/vnd.ms-excel'
        wb.save(response)
        return response
 
def export_pdf(request):
    from cStringIO import StringIO
    from reportlab.pdfgen import canvas # importing inside the view so that other functions work
                                        # on hosts without reportlab
 
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import *
    from reportlab.lib import colors
 
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=somefilename.pdf'
 
    # Our container for 'Flowable' objects
    elements = []
 
    # A large collection of style sheets pre-made for us
    styles = getSampleStyleSheet()
 
    # A basic document for us to write to a response
    doc = SimpleDocTemplate(response)
 
    elements.append(Paragraph("Stockprices",
     styles['Title']))
 
    # Get database data
    widget_ids = request.GET.values()
    for widget_id in widget_ids:
        widget = get_object_or_404(Widget, pk=widget_id)
        data = []
        for query in widget.get_queries():
            tabl = query.table
            for tabl in globals()[query.table].objects.all().order_by('-symbol'):
                if (query.property == tabl.symbol):
                    data.append([tabl.symbol, tabl.price])
 
    ts = [('ALIGN', (1,1), (-1,-1), 'CENTER'),
         ('LINEABOVE', (0,0), (-1,0), 1, colors.purple),
         #('LINEBELOW', (0,0), (-1,0), 1, colors.purple),
         #('FONT', (0,0), (-1,0), 'Times-Bold'),
         #('LINEABOVE', (0,-1), (-1,-1), 1, colors.purple),
         ('LINEBELOW', (0,-1), (-1,-1), 0.5, colors.purple,
          1, None, None, 4,1),
         ('LINEBELOW', (0,-1), (-1,-1), 1, colors.red),
         ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
         ('BOX', (0,0), (-1,-1), 0.25, colors.black)
         #('FONT', (0,-1), (-1,-1), 'Times-Bold')
          ]
    # Create the table with the necessary style, and add it to the
    # elements list.
    table = Table(data, style=ts)
    elements.append(table)
    # Write the document to response
    doc.build(elements)
    return response