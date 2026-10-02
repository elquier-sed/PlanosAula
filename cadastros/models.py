from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User


class EtapaEnsino(models.Model):
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Etapa de Ensino"
    )

    class Meta:
        verbose_name = "Etapa de Ensino"
        verbose_name_plural = "Etapas de Ensino"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class SerieAno(models.Model):
    etapa = models.ForeignKey(
        EtapaEnsino,
        on_delete=models.PROTECT,
        related_name="series",
        verbose_name="Etapa de Ensino"
    )

    nome = models.CharField(
        max_length=100,
        verbose_name="Série/Ano"
    )

    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )

    class Meta:
        verbose_name = "Série/Ano"
        verbose_name_plural = "Séries/Anos"
        ordering = ["etapa", "ordem"]

        constraints = [
            models.UniqueConstraint(
                fields=["etapa", "nome"],
                name="serie_unica_por_etapa"
            )
        ]

    def __str__(self):
        return f"{self.nome} - {self.etapa.nome}"


class AreaConhecimento(models.Model):
    nome = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Área do Conhecimento"
    )

    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )

    ativa = models.BooleanField(
        default=True,
        verbose_name="Ativa"
    )

    class Meta:
        verbose_name = "Área do Conhecimento"
        verbose_name_plural = "Áreas do Conhecimento"
        ordering = ["ordem", "nome"]

    def __str__(self):
        return self.nome


class Disciplina(models.Model):
    nome = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Disciplina"
    )

    area_conhecimento = models.ForeignKey(
        AreaConhecimento,
        on_delete=models.PROTECT,
        related_name="disciplinas",
        null=True,
        blank=True,
        verbose_name="Área do Conhecimento"
    )

    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )

    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"
        ordering = ["ordem", "nome"]

    def __str__(self):
        return self.nome


class SerieDisciplina(models.Model):
    serie = models.ForeignKey(
        SerieAno,
        on_delete=models.PROTECT,
        related_name="disciplinas",
        verbose_name="Série/Ano"
    )

    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.PROTECT,
        related_name="series",
        verbose_name="Disciplina"
    )

    ativa = models.BooleanField(
        default=True,
        verbose_name="Ativa"
    )

    class Meta:
        verbose_name = "Disciplina por Série"
        verbose_name_plural = "Disciplinas por Série"
        ordering = ["serie", "disciplina"]

        constraints = [
            models.UniqueConstraint(
                fields=["serie", "disciplina"],
                name="disciplina_unica_por_serie"
            )
        ]

    def __str__(self):
        return f"{self.serie} - {self.disciplina}"


class Competencia(models.Model):
    etapa = models.ForeignKey(
        EtapaEnsino,
        on_delete=models.PROTECT,
        related_name="competencias",
        verbose_name="Etapa de Ensino"
    )

    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.PROTECT,
        related_name="competencias",
        null=True,
        blank=True,
        verbose_name="Disciplina"
    )

    area_conhecimento = models.ForeignKey(
        AreaConhecimento,
        on_delete=models.PROTECT,
        related_name="competencias",
        null=True,
        blank=True,
        verbose_name="Área do Conhecimento"
    )

    codigo = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Código"
    )

    descricao = models.TextField(
        verbose_name="Competência"
    )

    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )

    ativa = models.BooleanField(
        default=True,
        verbose_name="Ativa"
    )

    class Meta:
        verbose_name = "Competência"
        verbose_name_plural = "Competências"
        ordering = ["etapa", "ordem", "id"]

    def clean(self):
        super().clean()

        if self.disciplina and self.area_conhecimento:
            raise ValidationError(
                "A competência deve estar vinculada a uma disciplina "
                "ou a uma área do conhecimento, e não às duas."
            )

        if not self.disciplina and not self.area_conhecimento:
            raise ValidationError(
                "Informe uma disciplina ou uma área do conhecimento "
                "para a competência."
            )

    def __str__(self):
        if self.codigo:
            return f"{self.codigo} - {self.descricao[:80]}"
        return self.descricao[:100]


class Habilidade(models.Model):
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.PROTECT,
        related_name="habilidades",
        null=True,
        blank=True,
        verbose_name="Disciplina"
    )

    competencia = models.ForeignKey(
        Competencia,
        on_delete=models.PROTECT,
        related_name="habilidades",
        null=True,
        blank=True,
        verbose_name="Competência"
    )

    etapa_origem = models.ForeignKey(
        EtapaEnsino,
        on_delete=models.PROTECT,
        related_name="habilidades_origem",
        verbose_name="Etapa de Origem"
    )

    serie_origem = models.ForeignKey(
        SerieAno,
        on_delete=models.PROTECT,
        related_name="habilidades_origem",
        null=True,
        blank=True,
        verbose_name="Série/Ano de Origem"
    )

    codigo = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Código"
    )

    descricao = models.TextField(
        verbose_name="Habilidade"
    )

    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )

    ativa = models.BooleanField(
        default=True,
        verbose_name="Ativa"
    )

    class Meta:
        verbose_name = "Habilidade"
        verbose_name_plural = "Habilidades"
        ordering = [
            "etapa_origem",
            "ordem",
            "id",
        ]

    def clean(self):
        super().clean()

        # A habilidade deve pertencer a uma disciplina (EF)
        # OU a uma competência (EM).
        if self.disciplina and self.competencia:
            raise ValidationError(
                "A habilidade deve estar vinculada a uma disciplina "
                "ou a uma competência, e não às duas."
            )

        if not self.disciplina and not self.competencia:
            raise ValidationError(
                "Informe uma disciplina ou uma competência "
                "para a habilidade."
            )

        # A série informada precisa pertencer à etapa selecionada.
        if (
            self.serie_origem
            and self.serie_origem.etapa_id != self.etapa_origem_id
        ):
            raise ValidationError({
                "serie_origem":
                    "A série/ano de origem deve pertencer à etapa de origem."
            })

    def __str__(self):
        if self.codigo:
            return f"{self.codigo} - {self.descricao[:80]}"
        return self.descricao[:100]

    
class CompetenciaComumItinerario(models.Model):
    codigo = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Código"
    )

    descricao = models.TextField(
        verbose_name="Competência Comum do Itinerário Formativo"
    )

    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )

    ativa = models.BooleanField(
        default=True,
        verbose_name="Ativa"
    )

    class Meta:
        verbose_name = "Competência Comum do Itinerário Formativo"
        verbose_name_plural = "Competências Comuns dos Itinerários Formativos"
        ordering = ["ordem", "id"]

    def __str__(self):
        if self.codigo:
            return f"{self.codigo} - {self.descricao[:80]}"
        return self.descricao[:100]

class CriterioAvaliacaoCurriculoDigitalEM(models.Model):
    descricao = models.TextField(
        verbose_name="Critério de Avaliação"
    )

    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    class Meta:
        verbose_name = "Critério de Avaliação - Currículo Digital EM"
        verbose_name_plural = "Critérios de Avaliação - Currículo Digital EM"
        ordering = ["ordem", "id"]

    def __str__(self):
        return self.descricao[:100]


class InstrumentoAvaliacao(models.Model):
    descricao = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Instrumento de Avaliação"
    )

    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    class Meta:
        verbose_name = "Instrumento de Avaliação"
        verbose_name_plural = "Instrumentos de Avaliação"
        ordering = ["ordem", "descricao"]

    def __str__(self):
        return self.descricao


class RecursoPedagogico(models.Model):
    descricao = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Recurso Pedagógico"
    )

    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    class Meta:
        verbose_name = "Recurso Pedagógico"
        verbose_name_plural = "Recursos Pedagógicos"
        ordering = ["ordem", "descricao"]

    def __str__(self):
        return self.descricao


class Referencia(models.Model):
    descricao = models.TextField(
        verbose_name="Referência"
    )

    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )

    ativa = models.BooleanField(
        default=True,
        verbose_name="Ativa"
    )

    class Meta:
        verbose_name = "Referência"
        verbose_name_plural = "Referências"
        ordering = ["ordem", "id"]

    def __str__(self):
        return self.descricao[:100]


class ObjetivoAprendizagemIFAGeral(models.Model):
    descricao = models.TextField(
        verbose_name="Objetivo Geral de Aprendizagem IFA"
    )

    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    class Meta:
        verbose_name = "Objetivo Geral de Aprendizagem IFA"
        verbose_name_plural = "Objetivos Gerais de Aprendizagem IFA"
        ordering = ["ordem", "id"]

    def __str__(self):
        return self.descricao[:100]


class ObjetivoAprendizagemIFAEspecifico(models.Model):
    objetivo_geral = models.ForeignKey(
        ObjetivoAprendizagemIFAGeral,
        on_delete=models.PROTECT,
        related_name="objetivos_especificos",
        verbose_name="Objetivo Geral"
    )

    descricao = models.TextField(
        verbose_name="Objetivo Específico de Aprendizagem IFA"
    )

    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    class Meta:
        verbose_name = "Objetivo Específico de Aprendizagem IFA"
        verbose_name_plural = "Objetivos Específicos de Aprendizagem IFA"
        ordering = [
            "objetivo_geral__ordem",
            "ordem",
            "id",
        ]

    def __str__(self):
        return self.descricao[:100]


class Escola(models.Model):
    nome = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Escola"
    )

    municipio = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Município"
    )

    ativa = models.BooleanField(
        default=True,
        verbose_name="Ativa"
    )

    class Meta:
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Professor(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="professor",
        verbose_name="Usuário"
    )

    escolas = models.ManyToManyField(
        Escola,
        related_name="professores",
        blank=True,
        verbose_name="Escolas"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"
        ordering = ["usuario__first_name", "usuario__last_name"]

    def __str__(self):
        nome = self.usuario.get_full_name()

        if nome:
            return nome

        return self.usuario.username    


class HabilidadeCurriculoDigital(models.Model):
    etapa = models.ForeignKey(
        EtapaEnsino,
        on_delete=models.PROTECT,
        related_name="habilidades_curriculo_digital",
        verbose_name="Etapa de Ensino"
    )

    serie = models.ForeignKey(
        SerieAno,
        on_delete=models.PROTECT,
        related_name="habilidades_curriculo_digital",
        null=True,
        blank=True,
        verbose_name="Série/Ano"
    )

    codigo = models.CharField(
        max_length=50,
        verbose_name="Código"
    )

    descricao = models.TextField(
        verbose_name="Habilidade"
    )

    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )

    ativa = models.BooleanField(
        default=True,
        verbose_name="Ativa"
    )

    class Meta:
        verbose_name = "Habilidade do Currículo Digital"
        verbose_name_plural = "Habilidades do Currículo Digital"

        ordering = [
            "etapa",
            "serie",
            "ordem",
            "codigo",
        ]

    def clean(self):
        super().clean()

        if (
            self.serie_id
            and self.etapa_id
            and self.serie.etapa_id != self.etapa_id
        ):
            raise ValidationError({
                "serie":
                    "A série/ano deve pertencer à etapa de ensino informada."
            })

    def __str__(self):
        if self.codigo:
            return f"{self.codigo} - {self.descricao[:80]}"

        return self.descricao[:100]