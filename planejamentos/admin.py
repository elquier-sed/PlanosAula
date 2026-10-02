from django.contrib import admin

from .models import PlanejamentoMensal


@admin.register(PlanejamentoMensal)
class PlanejamentoMensalAdmin(admin.ModelAdmin):

    # =========================================================
    # LISTAGEM
    # =========================================================

    list_display = (
        "id",
        "professor",
        "escola",
        "serie",
        "disciplina",
        "competencia_habilidades_curriculo",
        "mes",
        "ano",
        "quantidade_aulas",
        "status",
        "atualizado_em",
    )

    list_filter = (
        "status",
        "ano",
        "mes",
        "serie__etapa",
        "serie",
        "disciplina",
        "escola",
    )

    search_fields = (
        "professor__usuario__first_name",
        "professor__usuario__last_name",
        "professor__usuario__username",
        "escola__nome",
        "disciplina__nome",
        "serie__nome",
        "nome_projeto_integrador",
    )

    ordering = (
        "-ano",
        "-mes",
        "escola",
        "serie",
        "disciplina",
    )

    list_select_related = (
        "professor",
        "professor__usuario",
        "escola",
        "serie",
        "serie__etapa",
        "disciplina",
    )

    # =========================================================
    # CAMPOS COM AUTOCOMPLETE
    # =========================================================

    autocomplete_fields = (
        "professor",
        "escola",
        "serie",
        "disciplina",
        "competencias",
        "habilidades",
        "habilidades_curriculo_digital",
        "recursos_pedagogicos",
        "criterios_avaliacao_em",
        "instrumentos_avaliacao",
        "referencias",
        "competencias_comuns_ifa",
        "objetivos_ifa_gerais",
        "objetivos_ifa_especificos",
    )

    # =========================================================
    # ORGANIZAÇÃO DO FORMULÁRIO
    # =========================================================

    fieldsets = (
        (
            "Identificação do Planejamento",
            {
                "fields": (
                    "professor",
                    "escola",
                    ("mes", "ano"),
                    "serie",
                    "disciplina",
                    "quantidade_aulas",
                    "status",
                )
            },
        ),

        (
            "Competências e Habilidades",
            {
                "fields": (
                    "competencias",
                    "habilidades",
                    "outras_habilidades",
                    "habilidades_curriculo_digital",
                    "outras_habilidades_curriculo_digital",
                )
            },
        ),

        (
            "Conteúdo e Metodologia",
            {
                "fields": (
                    "objetos_conhecimento",
                    "metodologia",
                )
            },
        ),

        (
            "Recomposição da Aprendizagem",
            {
                "fields": (
                    "habilidades_recomposicao",
                    "caminho_metodologico_recomposicao",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),

        (
            "Recursos, Avaliação e Referências",
            {
                "fields": (
                    "recursos_pedagogicos",
                    "outro_recurso_pedagogico",
                    "criterios_avaliacao_em",
                    "instrumentos_avaliacao",
                    "outro_instrumento_avaliacao",
                    "referencias",
                    "outra_referencia",
                )
            },
        ),

        (
            "Itinerários Formativos - Ensino Médio",
            {
                "fields": (
                    "nome_projeto_integrador",
                    "competencias_comuns_ifa",
                    "objetivos_ifa_gerais",
                    "objetivos_ifa_especificos",
                    "caminho_metodologico_projeto",
                    "quantidade_aulas_ifa",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),

        (
            "Controle",
            {
                "fields": (
                    "criado_em",
                    "atualizado_em",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

    @admin.display(
        description="Etapa"
    )
    def competencia_habilidades_curriculo(self, obj):
        return obj.serie.etapa