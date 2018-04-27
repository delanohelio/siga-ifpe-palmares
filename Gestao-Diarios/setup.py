from datetime import datetime, timedelta
from PyPDF2 import PdfFileReader
import re

from .models import *

CREDITS = {"30H/30HA": 2, "45H/45HA": 3, "60H/60HA": 4, "75H/75HA": 5}

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end], end
    except ValueError:
        return ""

def get_spans_patters( s, pattern):
    span1 = None
    span2 = None
    first = re.search(pattern, s)
    if first is not None:
        span1 = first.span()
        last = re.search(pattern, s[span1[1]:])
        if last is not None:
            span2 = (last.span()[0] + span1[1], last.span()[1] + span1[1])

    return span1, span2

def all_days_of_weekday_by_week(fromDate, weekday, weeks):
   if (fromDate.weekday() > weekday):
       fromDate += timedelta(days=7)
   fromDate += timedelta(days = weekday - fromDate.weekday())
   for i in range(weeks):
      yield fromDate
      fromDate += timedelta(days = 7)

def all_days_of_weekday_by_date(fromDate, weekday, endDate):
    if (fromDate.weekday() > weekday):
        fromDate += timedelta(days=7)
    fromDate += timedelta(days=weekday - fromDate.weekday())
    while fromDate <= endDate:
        yield fromDate
        fromDate += timedelta(days=7)

def split_file_pages(file):
    doc = []
    page = []
    for line in file:
        if(line.find("Page") != -1):
            if(len(page) > 0): #Primeira Pagina
                doc.append(page)
            page = []
        page.append(line)
    doc.append(page)
    return doc

#TODO Refactor
def setup_aulas_previstas2(fromDate, endDate):
    diarios = Diario.objects.all()
    for diario in diarios:
        horarios = diario.horarioaula_set.all()
        for horario in horarios:
            datas = all_days_of_weekday_by_date(fromDate, int(horario.dia), endDate)
            for data in datas:
                Aula.objects.create(diario=diario, prevista=True, data=data,
                                    numero_de_aulas_prevista=horario.numero_de_aulas)
def setup_aulas_previstas(fromDate, weeks):
    diarios = Diario.objects.all()
    for diario in diarios:
        horarios = diario.horarioaula_set.all()
        for horario in horarios:
            datas = all_days_of_weekday_by_week(fromDate,int(horario.dia),weeks)
            for data in datas:
                Aula.objects.create(diario=diario, prevista=True, data=data, numero_de_aulas_prevista=horario.numero_de_aulas)


def setup_aulas_ministradas(file):
    pdf = PdfFileReader(file)
    format = "%d/%m/%Y"
    for pageNumber in range(pdf.getNumPages()):
        page = pdf.getPage(pageNumber)
        content = page.extractText()
        numero_diario, end = find_between(content, "Diário:", "Unidade")
        diario = Diario.objects.get(pk=numero_diario)
        content = content[end:]
        aulas_str, _ = find_between(content, "AulasDataConteúdo", "Página")
        while True:
            span1, span2 = get_spans_patters(aulas_str, "[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]")
            aula_str = ""
            if span2 is not None:
                aula_str = aulas_str[span1[1]:span2[0]]
            else:
                aula_str = aulas_str[span1[1]:]
            data = aulas_str[span1[0]:span1[1]]
            data_obj = datetime.strptime(data, format)
            conteudo = aula_str[1:]
            if conteudo != "":
                try:
                    aula = diario.aula_set.get(data=data_obj)
                    aula.numero_de_aulas = int(aula_str[0])
                    aula.registrada = True
                    aula.save()
                except Aula.DoesNotExist:
                    Aula.objects.create(diario=diario, registrada=True, data=data_obj,
                                        numero_de_aulas=int(aula_str[0]))

            if span1 is None or span2 is None:
                break

            aulas_str = aulas_str[span2[0]:]


def setup_diarios(file):
    pdf = PdfFileReader(file)
    for pageNumber in range(pdf.getNumPages()):
        page = pdf.getPage(pageNumber)
        content = page.extractText()
        nome_disciplina, end = find_between(content, "Comp. Curricular:", "Diário")
        credito, _ = find_between(nome_disciplina, "(", ")")
        credito = CREDITS[credito]
        content = content[end:]
        numero_diario, end = find_between(content, "Diário:", "Per. Letivo")
        content = content[end:]
        nome_professor, end = find_between(content, "Professor(es):", "Turma")
        content = content[end:]
        nome_turma, end = find_between(content, "Turma:", "Período")
        content = content[end:]
        nome_curso, end = find_between(content, "Curso:", "Aulas")

        curso, _ = Curso.objects.get_or_create(nome=nome_curso);
        turma, _ = Turma.objects.get_or_create(nome=nome_turma, curso=curso);

        disciplina, _ = Disciplina.objects.get_or_create(nome=nome_disciplina, creditos=credito, turma=turma)
        professor, _ = Professor.objects.get_or_create(nome=nome_professor);
        diario, _ = Diario.objects.get_or_create(numero=numero_diario, professor=professor, disciplina=disciplina, curso=curso)

def setup_horarios(file):
    format = "%H:%M"
    tempo_aula = timedelta(minutes=45)
    dia_semana = {"Seg": 0, "Ter": 1, "Qua": 2, "Qui": 3, "Sex": 4}
    line = file.readline() #cabecalho
    line = file.readline()
    while line != "":
        line_split = line.split(";")

        numero_diario = line_split[0][1:-1]
        diario = Diario.objects.get(pk=numero_diario)
        horarios = line_split[1]
        horariosSplitted = horarios[2:-2].split()
        horario = {}
        for i in range(0, len(horariosSplitted), 2):

            dia = horariosSplitted[i]
            if (not dia in horario):
                horario[dia] = 0

            times = horariosSplitted[i + 1].split("~")
            time1 = datetime.strptime(times[0], format)
            time2 = datetime.strptime(times[1], format)

            aulas = round((time2 - time1) / tempo_aula)
            horario[dia] += aulas

        diario.horarioaula_set.clear()
        for dia in horario:
            HorarioAula.objects.create(dia=dia_semana[dia], numero_de_aulas=horario[dia],diario=diario)

        line = file.readline()

def extract_data(file):
    doc = split_file_pages(file)
    linesTag = []
    report = ""
    for page in doc:
        credits = {"(30H/30HA)": 2, "(45H/45HA)": 3, "(60H/60HA)": 4, "(75H/75HA)": 5}

        professor = page[linesTag["PROFESSOR"]].strip()

        cabecalhoLine = page[linesTag["CABECALHO"]]
        cabecalhoSplitted = cabecalhoLine.strip().split()

        divisor_point = 5
        if (not all(dado.isdigit() for dado in cabecalhoSplitted[-3:])):
            divisor_point = 4
        nome_disciplina = " ".join(cabecalhoSplitted[:-divisor_point])
        creditos = credits[cabecalhoSplitted[-divisor_point]]
        nome_turma = cabecalhoSplitted[-(divisor_point - 1)]
        numero_diario = cabecalhoSplitted[-(divisor_point - 2)]
        aulas_ministradas = cabecalhoSplitted[-1]

        report += "%s;%s;%s;%s;%s;%s;%s\n" % (numero_diario, professor, nome_disciplina, nome_turma, str(creditos*20), creditos, aulas_ministradas)

    return report

        # Dias = page[linesTag["DIA"]].split()[1:]
        # Meses = page[linesTag["MES"]].split()[4:-2]
        # NAs = page[linesTag["NA"]].split()[1:]

        # for i in range(len(NAs)):
        #    data = date(YEAR, int(Meses[i]), int(Dias[i]))
        #    aula = Aula(diario, data, int(NAs[i]))
        #    print(data.weekday())


#run()
#dias = all_days_of_weekday_by_week(date(YEAR, 2, 6), 0, 10)
#for dia in dias:
#    print(dia)

