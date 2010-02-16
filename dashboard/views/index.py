from django.shortcuts import render_to_response
from ..models import StockPrice

def index(request):
    stock_list = StockPrice.objects.all().order_by('-symbol')
    return render_to_response('index.html', {'stockList': stock_list})