from .models import *
from datetime import datetime, timedelta

linesTag = {"CABECALHO": 14, "PROFESSOR":18, "DIA": 22, "MES": 26, "NA": 30}

def all_days_of_weekday_by_week(fromDate, weekday, weeks):
   fromDate += timedelta(days = weekday - fromDate.weekday())
   for i in range(weeks):
      yield fromDate
      fromDate += timedelta(days = 7)

def all_days_of_weekday_by_date(fromDate, weekday, endDate):
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
    format = "%d/%m/%Y"
    doc = split_file_pages(file)
    for page in doc[:]:
        numero_diario = page[linesTag["PROFESSOR"]].split()[-1]
        diario = Diario.objects.get(pk=numero_diario)

        for line in page:
            if (line[:2].isdigit()):
                report = line.split()
                if(len(report) >= 3):
                    data = datetime.strptime(report[0], format)
                    try:
                        aula = diario.aula_set.get(data=data)
                        aula.numero_de_aulas = int(report[1])
                        aula.registrada = True
                        aula.save()
                    except Aula.DoesNotExist:
                        Aula.objects.create(diario=diario, registrada=True, data=data,
                                            numero_de_aulas=int(report[1]))

def setup_diarios(file):
    doc = split_file_pages(file)
    for page in doc:
        credits = {"(30H/30HA)": 2, "(45H/45HA)": 3, "(60H/60HA)": 4, "(75H/75HA)": 5}

        professorLine = page[linesTag["PROFESSOR"]]
        professor, created = Professor.objects.get_or_create(nome=professorLine.strip())

        cabecalhoLine = page[linesTag["CABECALHO"]]
        cabecalhoSplitted = cabecalhoLine.strip().split()

        divisor_point = 5
        if (not all(dado.isdigit() for dado in cabecalhoSplitted[-3:])):
            divisor_point = 4
        nome_disciplina = " ".join(cabecalhoSplitted[:-divisor_point])
        creditos = credits[cabecalhoSplitted[-divisor_point]]
        nome_turma = cabecalhoSplitted[-(divisor_point - 1)]
        numero_diario = cabecalhoSplitted[-(divisor_point - 2)]

        turma, created = Turma.objects.get_or_create(nome=nome_turma)

        disciplina, created = Disciplina.objects.get_or_create(nome=nome_disciplina, creditos=creditos, turma=turma)
        Diario.objects.get_or_create(numero=numero_diario, professor=professor, disciplina=disciplina)

        #Dias = page[linesTag["DIA"]].split()[1:]
        #Meses = page[linesTag["MES"]].split()[4:-2]
        #NAs = page[linesTag["NA"]].split()[1:]

        #for i in range(len(NAs)):
        #    data = date(YEAR, int(Meses[i]), int(Dias[i]))
        #    aula = Aula(diario, data, int(NAs[i]))
        #    print(data.weekday())


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

        horarios = line_split[2]
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

