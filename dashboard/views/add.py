from django.http import HttpResponseRedirect

def addWidget(request):
    return HttpResponseRedirect('/dashboard')