from django.http import HttpResponse
from ..models import TickerWidget

def ticker_widget(request, ticker_widget_id):
    ticker_widget = TickerWidget.objects.get(parent_widget=ticker_widget_id)
    query = ticker_widget.get_query()
    try:
        return HttpResponse('<b>%s.%s:</b> %s' % (query.table, query.first_order_option, query.run().next()))
    except StopIteration:
        return HttpResponse('<b>No data for %s.%s!</b>' % (query.table, query.first_order_option))