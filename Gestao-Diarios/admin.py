from django.contrib import admin
from .models import *


class DiarioAdmin(admin.ModelAdmin):
    list_display = ('disciplina','professor')
    list_filter = ('professor', 'disciplina')

class HorarioAulaAdmin(admin.ModelAdmin):
    list_filter = ('diario',)

def make_resolved(modeladmin, request, queryset):
    queryset.update(resolvido=True)
make_resolved.short_description = "Marcar como resolvido"

class AulaAdmin(admin.ModelAdmin):
    list_display = ['data','numero_de_aulas', 'diario','prevista', 'registrada', 'resolvido', 'getDiferente']
    list_filter = ('prevista', 'registrada', 'resolvido', 'diario', )
    ordering = ('diario', 'data',)
    actions = [make_resolved]

    def getDiferente(self, obj):
        return obj.numero_de_aulas_prevista == obj.numero_de_aulas

    getDiferente.boolean = True
    getDiferente.short_description = "Registro Coerente"

admin.site.register(Curso)
admin.site.register(Turma)
admin.site.register(Professor)
admin.site.register(Disciplina)
admin.site.register(Diario, DiarioAdmin)
admin.site.register(Aula, AulaAdmin)
admin.site.register(HorarioAula, HorarioAulaAdmin)

