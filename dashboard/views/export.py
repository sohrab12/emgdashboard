from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from ..models import Widget

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