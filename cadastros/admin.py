from django.contrib import admin

from .models import (
    EtapaEnsino,
    SerieAno,
    AreaConhecimento,
    Disciplina,
    SerieDisciplina,
    Competencia,
    Habilidade,
    HabilidadeCurriculoDigital,
    CompetenciaComumItinerario,
    CriterioAvaliacaoCurriculoDigitalEM,
    InstrumentoAvaliacao,
    RecursoPedagogico,
    Referencia,
    ObjetivoAprendizagemIFAGeral,
    ObjetivoAprendizagemIFAEspecifico,
    Escola,
    Professor,
)


@admin.register(EtapaEnsino)
class EtapaEnsinoAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)


@admin.register(SerieAno)
class SerieAnoAdmin(admin.ModelAdmin):
    list_display = ("nome", "etapa", "ordem")
    list_filter = ("etapa",)
    search_fields = ("nome", "etapa__nome")
    ordering = ("etapa", "ordem", "nome")


@admin.register(AreaConhecimento)
class AreaConhecimentoAdmin(admin.ModelAdmin):
    list_display = ("nome", "ordem", "ativa")
    list_filter = ("ativa",)
    search_fields = ("nome",)
    ordering = ("ordem", "nome")


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "area_conhecimento",
        "ordem",
    )

    list_filter = (
        "area_conhecimento",
    )

    search_fields = (
        "nome",
        "area_conhecimento__nome",
    )

    autocomplete_fields = (
        "area_conhecimento",
    )

    ordering = (
        "ordem",
        "nome",
    )


@admin.register(SerieDisciplina)
class SerieDisciplinaAdmin(admin.ModelAdmin):
    list_display = (
        "serie",
        "disciplina",
        "ativa",
    )

    list_filter = (
        "ativa",
        "serie__etapa",
        "serie",
        "disciplina",
    )

    search_fields = (
        "serie__nome",
        "serie__etapa__nome",
        "disciplina__nome",
    )

    autocomplete_fields = (
        "serie",
        "disciplina",
    )

    ordering = (
        "serie",
        "disciplina",
    )


@admin.register(Competencia)
class CompetenciaAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "descricao_resumida",
        "etapa",
        "disciplina",
        "area_conhecimento",
        "ativa",
        "ordem",
    )

    list_filter = (
        "ativa",
        "etapa",
        "disciplina",
        "area_conhecimento",
    )

    search_fields = (
        "codigo",
        "descricao",
        "disciplina__nome",
        "area_conhecimento__nome",
        "etapa__nome",
    )

    autocomplete_fields = (
        "etapa",
        "disciplina",
        "area_conhecimento",
    )

    ordering = (
        "etapa",
        "ordem",
        "codigo",
    )

    @admin.display(description="Competência")
    def descricao_resumida(self, obj):
        if len(obj.descricao) > 100:
            return f"{obj.descricao[:100]}..."
        return obj.descricao


@admin.register(Habilidade)
class HabilidadeAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "descricao_resumida",
        "etapa_origem",
        "disciplina",
        "competencia",
        "serie_origem",
        "ativa",
        "ordem",
    )

    list_filter = (
        "ativa",
        "etapa_origem",
        "disciplina",
        "competencia",
        "serie_origem",
    )

    search_fields = (
        "codigo",
        "descricao",
        "disciplina__nome",
        "competencia__descricao",
        "competencia__area_conhecimento__nome",
        "etapa_origem__nome",
        "serie_origem__nome",
    )

    autocomplete_fields = (
        "disciplina",
        "competencia",
        "etapa_origem",
        "serie_origem",
    )

    ordering = (
        "etapa_origem",
        "ordem",
        "codigo",
    )

    @admin.display(description="Habilidade")
    def descricao_resumida(self, obj):
        if len(obj.descricao) > 100:
            return f"{obj.descricao[:100]}..."
        return obj.descricao


@admin.register(HabilidadeCurriculoDigital)
class HabilidadeCurriculoDigitalAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "descricao_resumida",
        "etapa",
        "serie",
        "ativa",
        "ordem",
    )

    list_filter = (
        "ativa",
        "etapa",
        "serie",
    )

    search_fields = (
        "codigo",
        "descricao",
        "etapa__nome",
        "serie__nome",
    )

    autocomplete_fields = (
        "etapa",
        "serie",
    )

    ordering = (
        "etapa",
        "serie",
        "ordem",
        "codigo",
    )

    @admin.display(description="Habilidade")
    def descricao_resumida(self, obj):
        if len(obj.descricao) > 100:
            return f"{obj.descricao[:100]}..."

        return obj.descricao


@admin.register(CompetenciaComumItinerario)
class CompetenciaComumItinerarioAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "descricao_resumida",
        "ordem",
        "ativa",
    )

    list_filter = (
        "ativa",
    )

    search_fields = (
        "codigo",
        "descricao",
    )

    ordering = (
        "ordem",
        "codigo",
    )

    @admin.display(description="Competência")
    def descricao_resumida(self, obj):
        if len(obj.descricao) > 120:
            return f"{obj.descricao[:120]}..."
        return obj.descricao

@admin.register(CriterioAvaliacaoCurriculoDigitalEM)
class CriterioAvaliacaoCurriculoDigitalEMAdmin(admin.ModelAdmin):
    list_display = (
        "descricao_resumida",
        "ordem",
        "ativo",
    )
    list_filter = (
        "ativo",
    )
    search_fields = (
        "descricao",
    )
    ordering = (
        "ordem",
        "id",
    )

    @admin.display(description="Critério de Avaliação")
    def descricao_resumida(self, obj):
        if len(obj.descricao) > 120:
            return f"{obj.descricao[:120]}..."
        return obj.descricao


@admin.register(InstrumentoAvaliacao)
class InstrumentoAvaliacaoAdmin(admin.ModelAdmin):
    list_display = (
        "descricao",
        "ordem",
        "ativo",
    )
    list_filter = (
        "ativo",
    )
    search_fields = (
        "descricao",
    )
    ordering = (
        "ordem",
        "descricao",
    )


@admin.register(RecursoPedagogico)
class RecursoPedagogicoAdmin(admin.ModelAdmin):
    list_display = (
        "descricao",
        "ordem",
        "ativo",
    )
    list_filter = (
        "ativo",
    )
    search_fields = (
        "descricao",
    )
    ordering = (
        "ordem",
        "descricao",
    )


@admin.register(Referencia)
class ReferenciaAdmin(admin.ModelAdmin):
    list_display = (
        "descricao_resumida",
        "ordem",
        "ativa",
    )
    list_filter = (
        "ativa",
    )
    search_fields = (
        "descricao",
    )
    ordering = (
        "ordem",
        "id",
    )

    @admin.display(description="Referência")
    def descricao_resumida(self, obj):
        if len(obj.descricao) > 120:
            return f"{obj.descricao[:120]}..."
        return obj.descricao


class ObjetivoAprendizagemIFAEspecificoInline(admin.TabularInline):
    model = ObjetivoAprendizagemIFAEspecifico
    extra = 1
    fields = (
        "descricao",
        "ordem",
        "ativo",
    )
    ordering = (
        "ordem",
        "id",
    )


@admin.register(ObjetivoAprendizagemIFAGeral)
class ObjetivoAprendizagemIFAGeralAdmin(admin.ModelAdmin):
    list_display = (
        "descricao_resumida",
        "ordem",
        "ativo",
    )
    list_filter = (
        "ativo",
    )
    search_fields = (
        "descricao",
    )
    ordering = (
        "ordem",
        "id",
    )
    inlines = (
        ObjetivoAprendizagemIFAEspecificoInline,
    )

    @admin.display(description="Objetivo Geral")
    def descricao_resumida(self, obj):
        if len(obj.descricao) > 120:
            return f"{obj.descricao[:120]}..."
        return obj.descricao


@admin.register(ObjetivoAprendizagemIFAEspecifico)
class ObjetivoAprendizagemIFAEspecificoAdmin(admin.ModelAdmin):
    list_display = (
        "descricao_resumida",
        "objetivo_geral",
        "ordem",
        "ativo",
    )
    list_filter = (
        "ativo",
        "objetivo_geral",
    )
    search_fields = (
        "descricao",
        "objetivo_geral__descricao",
    )
    autocomplete_fields = (
        "objetivo_geral",
    )
    ordering = (
        "objetivo_geral__ordem",
        "ordem",
        "id",
    )

    @admin.display(description="Objetivo Específico")
    def descricao_resumida(self, obj):
        if len(obj.descricao) > 120:
            return f"{obj.descricao[:120]}..."
        return obj.descricao


@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "municipio",
        "ativa",
    )

    list_filter = (
        "ativa",
        "municipio",
    )

    search_fields = (
        "nome",
        "municipio",
    )

    ordering = (
        "nome",
    )


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = (
        "nome_professor",
        "username",
        "email",
        "ativo",
    )

    list_filter = (
        "ativo",
        "escolas",
    )

    search_fields = (
        "usuario__first_name",
        "usuario__last_name",
        "usuario__username",
        "usuario__email",
    )

    autocomplete_fields = (
        "usuario",
    )

    filter_horizontal = (
        "escolas",
    )

    ordering = (
        "usuario__first_name",
        "usuario__last_name",
    )

    @admin.display(description="Professor")
    def nome_professor(self, obj):
        nome = obj.usuario.get_full_name()

        if nome:
            return nome

        return obj.usuario.username

    @admin.display(description="Usuário")
    def username(self, obj):
        return obj.usuario.username

    @admin.display(description="E-mail")
    def email(self, obj):
        return obj.usuario.email