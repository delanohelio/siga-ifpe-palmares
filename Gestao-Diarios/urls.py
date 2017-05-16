from django.conf.urls import url

from . import views

app_name = 'coord'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^setup_diarios/$', views.setup_diarios, name='setup_diarios'),
    url(r'^setup_horarios/$', views.setup_horarios, name='setup_horarios'),
    url(r'^gerar_previstas/$', views.setup_aulas_previstas, name='gerar_previstas'),
    url(r'^gerar_previstas2/$', views.setup_aulas_previstas2, name='gerar_previstas2'),
    url(r'^inserir_aulas/$', views.setup_aulas_registradas, name='inserir_aulas'),
    url(r'^remove_aulas/$', views.remove_aulas, name='remove_aulas'),
    url(r'^clear_aulas/$', views.clear_aulas, name='clear_aulas'),
    url(r'^clear/$', views.clear_data, name='clear'),
    url(r'^(?P<disciplina_id>[0-9]+)/$', views.detail, name='detail'),
]