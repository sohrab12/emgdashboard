from django.http import HttpResponse

# Create your views here.

def graph_view(request):
    return HttpResponse(request.GET['x'])