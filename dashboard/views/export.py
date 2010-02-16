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
        
def export_pdf(request):
    from reportlab.lib.styles import getSampleStyleSheet # importing inside the view so that other functions work
                                                         # on hosts without reportlab
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
                    data.append([tabl.symbol,   tabl.price])

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