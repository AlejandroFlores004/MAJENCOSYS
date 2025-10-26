from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO
from openpyxl import Workbook

def demo_pdf(request, pk):
    html_string = render_to_string('demo_pdf.html', {'nombre': 'Azucena'})
    # base_url para que resuelva /static/ cuando lo uses
    pdf_bytes = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    return _pdf_response(pdf_bytes, filename="demo_weasyprint.pdf")

def _pdf_response(pdf_bytes: bytes, filename: str):
    resp = HttpResponse(pdf_bytes, content_type='application/pdf')
    resp['Content-Disposition'] = f'inline; filename="{filename}"'
    return resp

def demo_excel(request, pk):
    wb = Workbook()
    ws = wb.active
    ws.title = "Datos"
    ws.append(["ID", "Nombre", "Valor"])
    ws.append([1, "Fila 1", 123.45])
    ws.append([2, "Fila 2", 678.90])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    resp = HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp['Content-Disposition'] = 'attachment; filename="demo.xlsx"'
    return resp
