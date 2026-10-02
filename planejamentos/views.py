from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

from cadastros.models import (
    Disciplina, 
    Professor,
    SerieAno,
    Competencia,
    Habilidade,
    SerieDisciplina,
    HabilidadeCurriculoDigital,
)

from .forms import PlanejamentoMensalForm
from .models import PlanejamentoMensal


@login_required
def lista_planejamentos(request):
    planejamentos = (
        PlanejamentoMensal.objects
        .filter(professor__usuario=request.user)
        .select_related(
            "escola",
            "serie",
            "serie__etapa",
            "disciplina",
        )
        .order_by("-ano", "-mes", "disciplina__nome")
    )

    return render(
        request,
        "planejamentos/lista_planejamentos.html",
        {
            "planejamentos": planejamentos,
        },
    )

@login_required
def novo_planejamento(request):

    try:
        professor = request.user.professor
    except Professor.DoesNotExist:
        return render(
            request,
            "planejamentos/erro.html",
            {
                "mensagem":
                    "Este usuário não possui um professor vinculado."
            },
        )

    if request.method == "POST":

        form = PlanejamentoMensalForm(
            request.POST,
            professor=professor,
        )

        if form.is_valid():

            planejamento = form.save(
                commit=False
            )

            planejamento.professor = professor
            planejamento.status = (
                PlanejamentoMensal.Status.RASCUNHO
            )

            planejamento.save()

            form.save_m2m()

            return redirect(
                "lista_planejamentos"
            )

    else:

        form = PlanejamentoMensalForm(
            professor=professor
        )

    return render(
        request,
        "planejamentos/novo_planejamento.html",
        {
            "form": form,
        },
    )


@login_required
def carregar_disciplinas(request):

    serie_id = request.GET.get("serie")

    disciplinas = (
        Disciplina.objects
        .filter(
            series__serie_id=serie_id,
            series__ativa=True,
        )
        .distinct()
        .order_by("nome")
    )

    dados = [
        {
            "id": disciplina.id,
            "nome": disciplina.nome,
        }
        for disciplina in disciplinas
    ]

    return JsonResponse(
        {
            "disciplinas": dados
        }
    )

@login_required
def carregar_dados_curriculares(request):

    serie_id = request.GET.get("serie")
    disciplina_id = request.GET.get("disciplina")

    try:
        serie = (
            SerieAno.objects
            .select_related("etapa")
            .get(pk=serie_id)
        )

        disciplina = (
            Disciplina.objects
            .select_related("area_conhecimento")
            .get(pk=disciplina_id)
        )

    except (
        SerieAno.DoesNotExist,
        Disciplina.DoesNotExist,
        ValueError,
        TypeError,
    ):
        return JsonResponse(
            {
                "erro": "Série ou disciplina inválida."
            },
            status=400,
        )


    # =====================================================
    # ENSINO FUNDAMENTAL
    # =====================================================
    #
    # A etapa da série é quem determina EF ou EM.
    #
    # No banco:
    #   etapa 1 = Ensino Fundamental - Anos Finais
    #   etapa 2 = Ensino Médio
    #
    # Não usamos a área da disciplina para identificar
    # a etapa, pois disciplinas do EF também podem possuir
    # área do conhecimento.
    # =====================================================

    if serie.etapa.nome == "Ensino Fundamental - Anos Finais":

        competencias = (
            Competencia.objects
            .filter(
                etapa=serie.etapa,
                disciplina=disciplina,
                ativa=True,
            )
            .order_by("ordem", "id")
        )

        curriculo_digital = (
            HabilidadeCurriculoDigital.objects
            .filter(
                etapa=serie.etapa,
                serie=serie,
                ativa=True,
            )
            .order_by("ordem", "codigo")
        )

        tipo = "EF"


    # =====================================================
    # ENSINO MÉDIO
    # =====================================================

    elif serie.etapa.nome == "Ensino Médio":

        competencias = (
            Competencia.objects
            .filter(
                etapa=serie.etapa,
                area_conhecimento=disciplina.area_conhecimento,
                ativa=True,
            )
            .order_by("ordem", "id")
        )

        curriculo_digital = (
            HabilidadeCurriculoDigital.objects
            .filter(
                etapa=serie.etapa,
                serie__isnull=True,
                ativa=True,
            )
            .order_by("ordem", "codigo")
        )

        tipo = "EM"


    # =====================================================
    # ETAPA NÃO RECONHECIDA
    # =====================================================

    else:

        return JsonResponse(
            {
                "erro": "Etapa de ensino não reconhecida."
            },
            status=400,
        )


    # =====================================================
    # RESPOSTA
    # =====================================================

    return JsonResponse(
        {
            "tipo": tipo,

            "competencias": [
                {
                    "id": competencia.id,
                    "codigo": competencia.codigo,
                    "descricao": competencia.descricao,
                }
                for competencia in competencias
            ],

            "curriculo_digital": [
                {
                    "id": habilidade.id,
                    "codigo": habilidade.codigo,
                    "descricao": habilidade.descricao,
                }
                for habilidade in curriculo_digital
            ],
        }
    )

@login_required
def carregar_habilidades(request):

    serie_id = request.GET.get("serie")
    disciplina_id = request.GET.get("disciplina")

    try:
        serie = (
            SerieAno.objects
            .select_related("etapa")
            .get(pk=serie_id)
        )

        disciplina = (
            Disciplina.objects
            .select_related("area_conhecimento")
            .get(pk=disciplina_id)
        )

    except (
        SerieAno.DoesNotExist,
        Disciplina.DoesNotExist,
        ValueError,
        TypeError,
    ):
        return JsonResponse(
            {"erro": "Série ou disciplina inválida."},
            status=400,
        )

    # Verifica se a disciplina pertence à série.

    if not SerieDisciplina.objects.filter(
        serie=serie,
        disciplina=disciplina,
        ativa=True,
    ).exists():

        return JsonResponse(
            {"erro": "Disciplina indisponível para a série."},
            status=400,
        )

    # ==================================================
    # ENSINO FUNDAMENTAL
    # ==================================================

    if serie.etapa.nome == "Ensino Fundamental - Anos Finais":

        habilidades = (
            Habilidade.objects
            .filter(
                etapa_origem=serie.etapa,
                disciplina=disciplina,
                ativa=True,
            )
            .select_related("serie_origem")
            .order_by("ordem", "codigo", "id")
        )

    # ==================================================
    # ENSINO MÉDIO
    # ==================================================

    elif serie.etapa.nome == "Ensino Médio":

        competencias_ids = request.GET.getlist(
            "competencias"
        )

        competencias_validas = (
            Competencia.objects
            .filter(
                pk__in=competencias_ids,
                etapa=serie.etapa,
                area_conhecimento=(
                    disciplina.area_conhecimento
                ),
                ativa=True,
            )
        )

        habilidades = (
            Habilidade.objects
            .filter(
                etapa_origem=serie.etapa,
                competencia__in=competencias_validas,
                ativa=True,
            )
            .select_related(
                "competencia",
                "serie_origem",
            )
            .order_by(
                "competencia__ordem",
                "ordem",
                "codigo",
                "id",
            )
        )

    else:

        return JsonResponse(
            {"erro": "Etapa de ensino não reconhecida."},
            status=400,
        )

    # ==================================================
    # RESPOSTA
    # ==================================================

    dados = []

    for habilidade in habilidades:

        dados.append({
            "id": habilidade.id,
            "codigo": habilidade.codigo,
            "descricao": habilidade.descricao,
            "serie_origem": (
                habilidade.serie_origem.nome
                if habilidade.serie_origem
                else ""
            ),
            "competencia_id": (
                habilidade.competencia_id
            ),
        })

    return JsonResponse({
        "habilidades": dados
    })