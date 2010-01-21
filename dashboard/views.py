from django.http import HttpResponse
import Image, ImageFont, ImageDraw
from django.conf import settings
import DateTime

def graph_view(request):
    #Load the image to be displayed, resize it to the parameters
    im = Image.open("C:/Users/Alex/Documents/Inf 191/emgdashboard/dashboard/Awesome.png")
    try:
        #Retrieve the size of the image, assuming width and height are separate parameters
        width = int(request.GET['width'])
        height = int(request.GET['height'])
        size = (width, height)

        #Retrieve the left-most and right-most times
        left-most = DateTime.datetime(request.GET['lefttime'])
        right-most = DateTime.datetimeP(request.GET['righttime'])

        #Get the model and property to query
        mode
    except:
        size = im.size
    im = im.resize(size)

    #Create and return response with image
    response = HttpResponse(mimetype="image/png")
    im.save(response, "PNG")
    return response