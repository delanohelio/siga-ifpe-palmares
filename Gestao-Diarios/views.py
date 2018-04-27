from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from datetime import datetime
from django.utils.encoding import smart_str

from .models import *
from . import setup

def index(request):
    list_disciplinas = Disciplina.objects.order_by('-id')[:5]
    context = {
        'list_disciplinas': list_disciplinas
    }
    return render(request, 'Gestao-Diarios/index.html', context)

def detail(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    return render(request, 'Gestao-Diarios/detail.html', {'disciplina': disciplina})

def setup_diarios(request):
    file = request.FILES['myfile']
    path = default_storage.save('tmp/file_diarios.pdf', ContentFile(file.read()))
    tmp_file = os.path.join(settings.MEDIA_ROOT, path)
    file = open(tmp_file, "rb")
    setup.setup_diarios(file)
    return HttpResponse("Ok")

def setup_horarios(request):
    file = request.FILES['myfile']
    path = default_storage.save('tmp/file_horarios.txt', ContentFile(file.read()))
    tmp_file = os.path.join(settings.MEDIA_ROOT, path)
    file = open(tmp_file)
    setup.setup_horarios(file)
    return HttpResponse("Ok")

def setup_aulas_registradas(request):
    file = request.FILES['myfile']
    path = default_storage.save('tmp/file_aulas.pdf', ContentFile(file.read()))
    tmp_file = os.path.join(settings.MEDIA_ROOT, path)
    file = open(tmp_file, "rb")
    setup.setup_aulas_ministradas(file)
    return HttpResponse("Ok")

def setup_aulas_previstas(request):
    format = "%Y-%m-%d"
    setup.setup_aulas_previstas(datetime.strptime(request.GET["data_inicio"], format), int(request.GET["semanas"]))
    return HttpResponse("Ok")

def setup_aulas_previstas2(request):
    format = "%Y-%m-%d"
    setup.setup_aulas_previstas2(datetime.strptime(request.GET["data_inicio"], format), datetime.strptime(request.GET["data_fim"], format))
    return HttpResponse("Ok")

def setup_extract_data(request):
    file = request.FILES['myfile']
    path = default_storage.save('tmp/file_aulas.txt', ContentFile(file.read()))
    tmp_file = os.path.join(settings.MEDIA_ROOT, path)
    file = open(tmp_file, encoding="utf8")
    report = setup.extract_data(file)

    file_name = "data.csv"
    path_to_file = os.path.join(settings.MEDIA_ROOT, "tmp/" + file_name)
    file_result = open(path_to_file, 'w+')
    file_result.write(report)
    file_result.close()

    if os.path.exists(path_to_file):
        with open(path_to_file, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path_to_file)
            return response
    raise HttpResponse("error")

def remove_aulas(request):
    format = "%Y-%m-%d"
    data = datetime.strptime(request.GET["data"], format)
    Aula.objects.filter(data=data).delete()
    return HttpResponse("Ok")

def clear_aulas(request):
    Aula.objects.all().delete()
    return HttpResponse("Ok")

def clear_data(request):
    Turma.objects.all().delete()
    Professor.objects.all().delete()
    Disciplina.objects.all().delete()
    Diario.objects.all().delete()
    HorarioAula.objects.all().delete()
    Aula.objects.all().delete()
    return HttpResponse("Ok")