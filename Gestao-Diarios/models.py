from django.db import models

class Turma(models.Model):
    nome = models.CharField(max_length=120)

    def __str__(self):
        return self.nome

class Professor(models.Model):
    nome = models.CharField(max_length=120)

    def __str__(self):
        return self.nome


class Disciplina(models.Model):
    nome = models.CharField(max_length=60)
    creditos = models.IntegerField(choices=((2, 2), (3,3), (4,4), (5,5)))
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s" % (str(self.turma), str(self.nome))

class Diario (models.Model):
    numero = models.CharField(primary_key=True, max_length=10)
    professor = models.ForeignKey(Professor, null=True,on_delete=models.SET_NULL)
    disciplina = models.OneToOneField(Disciplina)

    def __str__(self):
        return "%s - %s - %s" % (self.numero, self.disciplina, self.professor)

DAYS_OF_WEEK = (
    (0, 'Segunda'),
    (1, 'Terca'),
    (2, 'Quarta'),
    (3, 'Quinta'),
    (4, 'Sexta'),
    (5, 'Sabado'),
    (6, 'Domingo'),
)

class HorarioAula(models.Model):
    dia = models.CharField(max_length=1, choices=DAYS_OF_WEEK)
    numero_de_aulas = models.IntegerField(default=0)
    diario = models.ForeignKey(Diario, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %d" % (DAYS_OF_WEEK[int(self.dia)][1], self.numero_de_aulas)

class Aula(models.Model):
    diario = models.ForeignKey(Diario, on_delete=models.CASCADE)
    data = models.DateField()
    prevista = models.BooleanField(default=False)
    registrada = models.BooleanField(default=False)
    resolvido = models.BooleanField(default=False)
    numero_de_aulas_prevista = models.IntegerField(default=0)
    numero_de_aulas = models.IntegerField(default=0)


    def __str__(self):
        return "%s - %s - %s" % (str(self.data), str(self.numero_de_aulas_prevista), self.diario)
