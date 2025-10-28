from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from weasyprint import HTML
from io import BytesIO
from openpyxl import Workbook
from project.models import Project
from catalog.models import Material, ManoObra, Herramienta, Equipo, Riesgo, Calidad, Ambiental, Hidrologica
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

def demo_pdf(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Para Materiales ---------------------------------------------------
    
    qm = (Material.objects
          .filter(project=project)
          .select_related('unit')
          .order_by('name'))
    
    # Renderizar HTML con la lista de materiales
    html_string = render_to_string(
        'demo_pdf.html',
        {
            'nombre': 'ian',
            'apellido': 'adonay',
            'project': project,
            'materiales': qm,  # <-- aquí mandas la lista al HTML
        }
    )
    # base_url para que resuelva /static/ cuando lo uses
    pdf_bytes = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    return _pdf_response(pdf_bytes, filename="demo_weasyprint.pdf")

def catalogo_pdf(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    qm = (Material.objects
          .filter(project=project)
          .select_related('unit')
          .order_by('name'))
    
    qmo = (ManoObra.objects
          .filter(project=project)
          .order_by('name'))
    
    qhrr = (Herramienta.objects
          .filter(project=project)
          .order_by('name'))
    
    qeqp = (Equipo.objects
          .filter(project=project)
          .order_by('name'))
    
    qrsg = (Riesgo.objects
          .filter(project=project)
          .order_by('name'))
    
    qcld = (Calidad.objects
          .filter(project=project)
          .order_by('name'))
    
    qmbt = (Ambiental.objects
          .filter(project=project)
          .order_by('name'))
    
    qhdg = (Hidrologica.objects
          .filter(project=project)
          .order_by('name'))
    
    # Renderizar HTML con la lista de materiales
    html_string = render_to_string(
        'catalogo_pdf.html',
        {
            'nombre': 'ian',
            'apellido': 'adonay',
            'project': project,
            'materiales': qm,
            'manoobra': qmo,
            'herramienta': qhrr,
            'equipo': qeqp,
            'riesgo': qrsg,
            'calidad': qcld,
            'ambiental': qmbt,
            'hidrologica': qhdg,
        }
    )
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
