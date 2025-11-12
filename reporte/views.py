from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now, localdate
from datetime import datetime
from weasyprint import HTML
from io import BytesIO
from openpyxl import Workbook
from project.models import Project
from catalog.models import Material, ManoObra, Herramienta, Equipo, Riesgo, Calidad, Ambiental, Hidrologica
from activity.models import Activity, Header
from schedule.models import Schedule
from django.db.models import Prefetch, Q

def report_center_pdf(request, pk: int):
    project = get_object_or_404(Project, pk=pk)

    context = {
        'project': project,
    }

    return render(request, 'report_center_pdf.html', context)

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
    
    # Renderizar HTML con la lista
    html_string = render_to_string(
        'catalogo_pdf.html',
        {
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

    pdf_bytes = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    return _pdf_response(pdf_bytes, filename="Reporte de Catalogo.pdf")

def libromayor_pdf(request, pk):
    project = get_object_or_404(Project, pk=pk)
    activity = Activity.objects.filter(project=project)

    activity_m = (Activity.objects.filter(project=project).prefetch_related('memoryMaterial_activity__material__unit').order_by('name'))
    activity_mo = (Activity.objects.filter(project=project).prefetch_related('MemoryManoObra_activity__manoobra'))
    activity_hrr = (Activity.objects.filter(project=project).prefetch_related('MemoryHerramienta_activity__herramienta'))
    activity_eqp = (Activity.objects.filter(project=project).prefetch_related('MemoryEquipo_activity__equipo'))
    activity_rsg = (Activity.objects.filter(project=project).prefetch_related('memoryRiesgos_activity__riesgo'))
    activity_cld = (Activity.objects.filter(project=project).prefetch_related('memoryCalidad_activity__calidad'))
    activity_mbt = (Activity.objects.filter(project=project).prefetch_related('memoryAmbiental_activity__ambiental'))
    activity_hdg = (Activity.objects.filter(project=project).prefetch_related('memoryHidrologica_activity__hidrologica'))

    with_materials = []
    with_manoonta = []
    with_herramienta = []
    with_equipo = []
    with_riesgo = []
    with_calidad = []
    with_ambiental = []
    with_hidrologica = []

    total_m = 0
    total_mo = 0
    total_hrr = 0
    total_eqp = 0
    total_rsg = 0
    total_cld = 0
    total_mbt = 0
    total_hdg = 0

    for am in activity_m:
        if am.memoryMaterial_activity.exists():
            with_materials.append(am)
        for elmt1 in am.memoryMaterial_activity.all():
            total_m += elmt1.material.price * elmt1.quantity

    for amo in activity_mo:
        if amo.MemoryManoObra_activity.exists():
            with_manoonta.append(amo)
        for elmt2 in amo.MemoryManoObra_activity.all():
            total_mo += (elmt2.manoobra.jornada / (1 - elmt2.prestaciones)) / elmt2.rendimiento

    for ahrr in activity_hrr:
        if ahrr.MemoryHerramienta_activity.exists():
            with_herramienta.append(ahrr)
        for elmt3 in ahrr.MemoryHerramienta_activity.all():
            total_hrr += elmt3.herramienta.costodia * elmt3.rendimiento

    for aeqp in activity_eqp:
        if aeqp.MemoryEquipo_activity.exists():
            with_equipo.append(aeqp)
        for elmt4 in aeqp.MemoryEquipo_activity.all():
            total_eqp += elmt4.equipo.costodia * elmt4.rendimiento

    for arsg in activity_rsg:
        if arsg.memoryRiesgos_activity.exists():
            with_riesgo.append(arsg)
        for elmt5 in arsg.memoryRiesgos_activity.all():
            total_rsg += elmt5.costo

    for acld in activity_cld:
        if acld.memoryCalidad_activity.exists():
            with_calidad.append(acld)
        for elmt6 in acld.memoryCalidad_activity.all():
            total_cld += elmt6.cantidad * elmt6.calidad.precio

    for ambt in activity_mbt:
        if ambt.memoryAmbiental_activity.exists():
            with_ambiental.append(ambt)
        for elmt7 in ambt.memoryAmbiental_activity.all():
            total_mbt += elmt7.valor

    for ahdg in activity_hdg:
        if ahdg.memoryHidrologica_activity.exists():
            with_hidrologica.append(ahdg)
        for elmt8 in ahdg.memoryHidrologica_activity.all():
            total_hdg += elmt8.costo

    # Renderizar HTML con la lista
    html_string2 = render_to_string(
        'libromayor_pdf.html',
        {
            'project':project,
            'activity':activity,
            'activity_m': activity_m,
            'with_materials': with_materials,
            'total_m': total_m,
            'activity_mo': activity_mo,
            'with_manoonta': with_manoonta,
            'total_mo': total_mo,
            'activity_hrr': activity_hrr,
            'with_herramienta': with_herramienta,
            'total_hrr': total_hrr,
            'activity_eqp': activity_eqp,
            'with_equipo': with_equipo,
            'total_eqp': total_eqp,
            'activity_rsg': activity_rsg,
            'with_riesgo': with_riesgo,
            'total_rsg': total_rsg,
            'activity_cld': activity_cld,
            'with_calidad': with_calidad,
            'total_cld': total_cld,
            'activity_mbt': activity_mbt,
            'with_ambiental': with_ambiental,
            'total_mbt': total_mbt,
            'activity_hdg': activity_hdg,
            'with_hidrologica': with_hidrologica,
            'total_hdg': total_hdg,
        }
    )

    pdf_bytes = HTML(string=html_string2, base_url=request.build_absolute_uri('/')).write_pdf()
    return _pdf_response(pdf_bytes, filename="Reporte de Libro Mayor.pdf")

def activities_pdf(request, pk):
    project = get_object_or_404(Project, pk=pk)

    activities_qs = (
        Activity.objects
        .filter(project=project)
        .prefetch_related(
            Prefetch("header_activity", queryset=Header.objects.all()),
            # Traemos el cronograma (uno por actividad según tu UniqueConstraint)
            Prefetch("schedule_activity", queryset=Schedule.objects.all())
        )
        .order_by("name")
    )

    # ---------------------------------------------------
    
    # Renderizar HTML con la lista de Actividades
    html_string = render_to_string(
        'activities_pdf.html',
        {
            'project': project,
            'activities': activities_qs,  # <-- aquí mandas la lista al HTML
        }
    )
    # base_url para que resuelva /static/ cuando lo uses
    pdf_bytes = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    return _pdf_response(pdf_bytes, filename="Reporte de Actividades.pdf")

def fecha_pdf(request, pk):
    project = get_object_or_404(Project, pk=pk)

    fecha_str = request.GET.get("fecha")
    if fecha_str:
        try:
            fecha_consulta = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            fecha_consulta = now().date()  # valor por defecto si hay error
    else:
        fecha_consulta = now().date()


    activities_qs = (
        Activity.objects
        .filter(project=project,
            schedule_activity__start_date__lte=fecha_consulta,
            schedule_activity__end_date__gte=fecha_consulta
        )
        .prefetch_related(
            Prefetch("header_activity", queryset=Header.objects.all()),
            Prefetch("schedule_activity", queryset=Schedule.objects.all())
        )
        .order_by("name")
    )

    # ---------------------------------------------------
    
    # Renderizar HTML con la lista de Actividades
    html_string = render_to_string(
        'fecha_pdf.html',
        {
            'project': project,
            'activities': activities_qs,  # <-- aquí mandas la lista al HTML
            'fecha_consulta': fecha_consulta,
        }
    )
    # base_url para que resuelva /static/ cuando lo uses
    pdf_bytes = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    return _pdf_response(pdf_bytes, filename="Reporte del.pdf")

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
