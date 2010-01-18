from django.http import HttpResponse

def graph_view(request):
    return HttpResponse(request.GET['x'])