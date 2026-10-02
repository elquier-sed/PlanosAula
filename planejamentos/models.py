from django.core.exceptions import ValidationError
from django.db import models

from cadastros.models import (
    Escola,
    Professor,
    SerieAno,
    Disciplina,
    Competencia,
    Habilidade,
    HabilidadeCurriculoDigital,
    CompetenciaComumItinerario,
    ObjetivoAprendizagemIFAGeral,
    ObjetivoAprendizagemIFAEspecifico,
    CriterioAvaliacaoCurriculoDigitalEM,
    InstrumentoAvaliacao,
    RecursoPedagogico,
    Referencia,
    SerieDisciplina
)


class PlanejamentoMensal(models.Model):

    class Status(models.TextChoices):
        RASCUNHO = "RASCUNHO", "Rascunho"
        FINALIZADO = "FINALIZADO", "Finalizado"

    # =========================================================
    # IDENTIFICAÇÃO
    # =========================================================

    professor = models.ForeignKey(
        Professor,
        on_delete=models.PROTECT,
        related_name="planejamentos",
        verbose_name="Professor"
    )

    escola = models.ForeignKey(
        Escola,
        on_delete=models.PROTECT,
        related_name="planejamentos",
        verbose_name="Escola"
    )

    serie = models.ForeignKey(
        SerieAno,
        on_delete=models.PROTECT,
        related_name="planejamentos",
        verbose_name="Série/Ano"
    )

    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.PROTECT,
        related_name="planejamentos",
        verbose_name="Disciplina"
    )

    mes = models.PositiveSmallIntegerField(
        verbose_name="Mês"
    )

    ano = models.PositiveSmallIntegerField(
        verbose_name="Ano"
    )

    quantidade_aulas = models.PositiveSmallIntegerField(
        verbose_name="Quantidade de Aulas"
    )

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.RASCUNHO,
        verbose_name="Status"
    )

    # =========================================================
    # COMPETÊNCIAS E HABILIDADES
    # =========================================================

    competencias = models.ManyToManyField(
        Competencia,
        blank=True,
        related_name="planejamentos",
        verbose_name="Competências"
    )

    habilidades = models.ManyToManyField(
        Habilidade,
        blank=True,
        related_name="planejamentos",
        verbose_name="Habilidades"
    )

    outras_habilidades = models.TextField(
        blank=True,
        verbose_name="Outras Habilidades"
    )

    habilidades_curriculo_digital = models.ManyToManyField(
        HabilidadeCurriculoDigital,
        blank=True,
        related_name="planejamentos",
        verbose_name="Habilidades do Currículo Digital"
    )

    outras_habilidades_curriculo_digital = models.TextField(
        blank=True,
        verbose_name="Outras Habilidades do Currículo Digital"
    )

    # =========================================================
    # CONTEÚDO E METODOLOGIA
    # =========================================================

    objetos_conhecimento = models.TextField(
        blank=True,
        verbose_name="Objetos de Conhecimento"
    )

    metodologia = models.TextField(
        blank=True,
        verbose_name="Caminho Metodológico"
    )

    # =========================================================
    # RECOMPOSIÇÃO DA APRENDIZAGEM
    # Aplicável quando necessário, especialmente LP/Matemática
    # =========================================================

    habilidades_recomposicao = models.TextField(
        blank=True,
        verbose_name="Habilidades para Recomposição"
    )

    caminho_metodologico_recomposicao = models.TextField(
        blank=True,
        verbose_name="Caminho Metodológico da Recomposição"
    )

    # =========================================================
    # RECURSOS / AVALIAÇÃO / REFERÊNCIAS
    # =========================================================

    recursos_pedagogicos = models.ManyToManyField(
        RecursoPedagogico,
        blank=True,
        related_name="planejamentos",
        verbose_name="Recursos Pedagógicos"
    )

    outro_recurso_pedagogico = models.TextField(
        blank=True,
        verbose_name="Outro Recurso Pedagógico"
    )

    criterios_avaliacao_em = models.ManyToManyField(
        CriterioAvaliacaoCurriculoDigitalEM,
        blank=True,
        related_name="planejamentos",
        verbose_name="Critérios de Avaliação - Currículo Digital EM"
    )

    instrumentos_avaliacao = models.ManyToManyField(
        InstrumentoAvaliacao,
        blank=True,
        related_name="planejamentos",
        verbose_name="Instrumentos de Avaliação"
    )

    outro_instrumento_avaliacao = models.TextField(
        blank=True,
        verbose_name="Outro Instrumento de Avaliação"
    )

    referencias = models.ManyToManyField(
        Referencia,
        blank=True,
        related_name="planejamentos",
        verbose_name="Referências"
    )

    outra_referencia = models.TextField(
        blank=True,
        verbose_name="Outra Referência"
    )

    # =========================================================
    # ITINERÁRIOS FORMATIVOS - ENSINO MÉDIO
    # =========================================================

    nome_projeto_integrador = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nome do Projeto Integrador"
    )

    competencias_comuns_ifa = models.ManyToManyField(
        CompetenciaComumItinerario,
        blank=True,
        related_name="planejamentos",
        verbose_name="Competências Comuns dos Itinerários Formativos"
    )

    objetivos_ifa_gerais = models.ManyToManyField(
        ObjetivoAprendizagemIFAGeral,
        blank=True,
        related_name="planejamentos",
        verbose_name="Objetivos Gerais de Aprendizagem IFA"
    )

    objetivos_ifa_especificos = models.ManyToManyField(
        ObjetivoAprendizagemIFAEspecifico,
        blank=True,
        related_name="planejamentos",
        verbose_name="Objetivos Específicos de Aprendizagem IFA"
    )

    caminho_metodologico_projeto = models.TextField(
        blank=True,
        verbose_name="Caminho Metodológico do Projeto Integrador"
    )

    quantidade_aulas_ifa = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Quantidade de Aulas IFA"
    )

    # =========================================================
    # CONTROLE
    # =========================================================

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Planejamento Mensal"
        verbose_name_plural = "Planejamentos Mensais"

        ordering = [
            "-ano",
            "-mes",
            "escola",
            "serie",
            "disciplina",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "professor",
                    "escola",
                    "serie",
                    "disciplina",
                    "mes",
                    "ano",
                ],
                name="planejamento_mensal_unico"
            )
        ]

    def clean(self):
        super().clean()

        if self.mes and not 1 <= self.mes <= 12:
            raise ValidationError({
                "mes": "Informe um mês entre 1 e 12."
            })

        if self.ano and not 2000 <= self.ano <= 2100:
            raise ValidationError({
                "ano": "Informe um ano válido."
            })

        if (
            self.professor_id
            and self.escola_id
            and not self.professor.escolas.filter(
                pk=self.escola_id
            ).exists()
        ):
            raise ValidationError({
                "escola":
                    "Esta escola não está vinculada ao professor."
            })

        if (
            self.serie_id
            and self.disciplina_id
            and not SerieDisciplina.objects.filter(
                serie_id=self.serie_id,
                disciplina_id=self.disciplina_id,
                ativa=True,
            ).exists()
        ):
            raise ValidationError({
                "disciplina":
                    "Esta disciplina não está disponível para a série/ano selecionada."
            })

    def __str__(self):
        return (
            f"{self.professor} - "
            f"{self.disciplina} - "
            f"{self.serie} - "
            f"{self.mes:02d}/{self.ano}"
        )