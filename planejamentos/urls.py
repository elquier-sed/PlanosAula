from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.lista_planejamentos,
        name="lista_planejamentos",
    ),

    path(
        "novo/",
        views.novo_planejamento,
        name="novo_planejamento",
    ),

    path(
        "ajax/disciplinas/",
        views.carregar_disciplinas,
        name="carregar_disciplinas",
    ),

    path(
        "ajax/dados-curriculares/",
        views.carregar_dados_curriculares,
        name="carregar_dados_curriculares",
    ),

    path(
        "ajax/habilidades/",
        views.carregar_habilidades,
        name="carregar_habilidades",
    ),
    
]