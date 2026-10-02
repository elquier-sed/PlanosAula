from django import forms
from django.utils import timezone

from cadastros.models import (
    Escola,
    SerieAno,
    Disciplina,
    Competencia,
    Habilidade,
    HabilidadeCurriculoDigital,
    RecursoPedagogico,
    CriterioAvaliacaoCurriculoDigitalEM,
    InstrumentoAvaliacao,
    Referencia,
)

from .models import PlanejamentoMensal


class PlanejamentoMensalForm(forms.ModelForm):

    competencias = forms.ModelMultipleChoiceField(
        queryset=Competencia.objects.none(),
        required=False,
        label="Competências",
        widget=forms.CheckboxSelectMultiple,
    )

    habilidades_curriculo_digital = forms.ModelMultipleChoiceField(
        queryset=HabilidadeCurriculoDigital.objects.none(),
        required=False,
        label="Habilidades do Currículo Digital",
        widget=forms.CheckboxSelectMultiple,
    )

    habilidades = forms.ModelMultipleChoiceField(
        queryset=Habilidade.objects.none(),
        required=False,
        label="Habilidades",
        widget=forms.CheckboxSelectMultiple,
    )

    recursos_pedagogicos = forms.ModelMultipleChoiceField(
        queryset=RecursoPedagogico.objects.none(),
        required=False,
        label="Recursos Pedagógicos",
        widget=forms.CheckboxSelectMultiple,
    )

    criterios_avaliacao_em = forms.ModelMultipleChoiceField(
        queryset=CriterioAvaliacaoCurriculoDigitalEM.objects.none(),
        required=False,
        label="Critérios de Avaliação - Currículo Digital",
        widget=forms.CheckboxSelectMultiple,
    )

    instrumentos_avaliacao = forms.ModelMultipleChoiceField(
        queryset=InstrumentoAvaliacao.objects.none(),
        required=False,
        label="Instrumentos de Avaliação",
        widget=forms.CheckboxSelectMultiple,
    )

    referencias = forms.ModelMultipleChoiceField(
        queryset=Referencia.objects.none(),
        required=False,
        label="Referências",
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = PlanejamentoMensal

        fields = (
            "escola",
            "mes",
            "ano",
            "serie",
            "disciplina",
            "quantidade_aulas",
            "competencias",
            "habilidades",
            "outras_habilidades",            
            "habilidades_curriculo_digital",
            "outras_habilidades_curriculo_digital",
            "objetos_conhecimento",
            "metodologia",
            "habilidades_recomposicao",
            "caminho_metodologico_recomposicao",
            "recursos_pedagogicos",
            "outro_recurso_pedagogico",
            "criterios_avaliacao_em",
            "instrumentos_avaliacao",
            "outro_instrumento_avaliacao",
            "referencias",
            "outra_referencia",
        )

        widgets = {
            "mes": forms.Select(
                choices=[
                    (1, "Janeiro"),
                    (2, "Fevereiro"),
                    (3, "Março"),
                    (4, "Abril"),
                    (5, "Maio"),
                    (6, "Junho"),
                    (7, "Julho"),
                    (8, "Agosto"),
                    (9, "Setembro"),
                    (10, "Outubro"),
                    (11, "Novembro"),
                    (12, "Dezembro"),
                ]
            ),

            "ano": forms.NumberInput(
                attrs={
                    "readonly": True,                    
                }
            ),

            "quantidade_aulas": forms.NumberInput(
                attrs={
                    "min": 1,
                }
            ),

            "outras_habilidades": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": (
                        "Informe outras habilidades, caso necessário."
                    ),
                }
            ),

            "outras_habilidades_curriculo_digital": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": (
                        "Informe outras habilidades do Currículo Digital, "
                        "caso necessário."
                    ),
                }
            ),

            "objetos_conhecimento": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Informe os objetos de conhecimento "
                        "trabalhados neste planejamento."
                    ),
                }
            ),

            "metodologia": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": (
                        "Descreva o caminho metodológico, as estratégias, "
                        "atividades e procedimentos que serão utilizados."
                    ),
                }
            ),

            "habilidades_recomposicao": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Informe as habilidades que serão trabalhadas "
                        "na recomposição da aprendizagem."
                    ),
                }
            ),

            "caminho_metodologico_recomposicao": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": (
                        "Descreva o caminho metodológico que será utilizado "
                        "na recomposição da aprendizagem."
                    ),
                }
            ),

            "outro_recurso_pedagogico": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": (
                        "Informe outros recursos pedagógicos, "
                        "caso necessário."
                    ),
                }
            ),

            "outro_instrumento_avaliacao": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": (
                        "Informe outros instrumentos de avaliação, "
                        "caso necessário."
                    ),
                }
            ),

            "outra_referencia": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": (
                        "Informe outra referência, caso necessário."
                    ),
                }
            ),
        }

    def __init__(self, *args, professor=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.professor = professor

        ano_atual = timezone.localdate().year

        if not self.instance.pk:
            self.fields["ano"].initial = ano_atual

        # =====================================================
        # ESCOLAS
        # Somente escolas vinculadas ao professor.
        # =====================================================

        if professor:
            self.fields["escola"].queryset = (
                professor.escolas
                .filter(ativa=True)
                .order_by("nome")
            )
        else:
            self.fields["escola"].queryset = (
                Escola.objects.none()
            )
        self.fields["escola"].empty_label = "Selecione uma escola"

        # =====================================================
        # SÉRIES
        # =====================================================

        self.fields["serie"].queryset = (
            SerieAno.objects
            .select_related("etapa")
            .order_by(
                "etapa__nome",
                "ordem",
            )
        )
        self.fields["serie"].empty_label = "Selecione uma série/ano"

        # =====================================================
        # DISCIPLINAS
        # Inicialmente nenhuma.
        # =====================================================

        self.fields["disciplina"].queryset = (
            Disciplina.objects.none()
        )
        self.fields["disciplina"].empty_label = "Selecione uma disciplina"

        self.fields["competencias"].queryset = (
            Competencia.objects.none()
        )

        self.fields["habilidades"].queryset = (
            Habilidade.objects.none()
        )

        self.fields["habilidades_curriculo_digital"].queryset = (
            HabilidadeCurriculoDigital.objects.none()
        )

        self.fields["recursos_pedagogicos"].queryset = (
            RecursoPedagogico.objects
            .filter(ativo=True)
            .order_by("ordem", "descricao")
        )

        self.fields["criterios_avaliacao_em"].queryset = (
            CriterioAvaliacaoCurriculoDigitalEM.objects
            .filter(ativo=True)
            .order_by("ordem", "descricao")
        )

        self.fields["instrumentos_avaliacao"].queryset = (
            InstrumentoAvaliacao.objects
            .filter(ativo=True)
            .order_by("ordem", "descricao")
        )

        self.fields["referencias"].queryset = (
            Referencia.objects
            .filter(ativa=True)
            .order_by("ordem", "descricao")
        )

        if "serie" in self.data and "disciplina" in self.data:

            try:
                serie_id = int(self.data.get("serie"))
                disciplina_id = int(self.data.get("disciplina"))

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

                # =============================================
                # ENSINO FUNDAMENTAL
                # =============================================

                if serie.etapa.nome == "Ensino Fundamental - Anos Finais":

                    self.fields["competencias"].queryset = (
                        Competencia.objects
                        .filter(
                            etapa=serie.etapa,
                            disciplina=disciplina,
                            ativa=True,
                        )
                        .order_by("ordem")
                    )

                    self.fields["habilidades"].queryset = (
                        Habilidade.objects
                        .filter(
                            etapa_origem=serie.etapa,
                            disciplina=disciplina,
                            ativa=True,
                        )
                        .order_by("ordem", "codigo", "id")
                    )

                    self.fields[
                        "habilidades_curriculo_digital"
                    ].queryset = (
                        HabilidadeCurriculoDigital.objects
                        .filter(
                            etapa=serie.etapa,
                            serie=serie,
                            ativa=True,
                        )
                        .order_by("ordem")
                    )

                # =============================================
                # ENSINO MÉDIO
                # =============================================

                elif serie.etapa.nome == "Ensino Médio":

                    self.fields["competencias"].queryset = (
                        Competencia.objects
                        .filter(
                            etapa=serie.etapa,
                            area_conhecimento=(
                                disciplina.area_conhecimento
                            ),
                            ativa=True,
                        )
                        .order_by("ordem")
                    )

                    competencias_selecionadas = (
                        self.data.getlist("competencias")
                    )

                    competencias_validas = (
                        self.fields["competencias"]
                        .queryset
                        .filter(
                            pk__in=competencias_selecionadas
                        )
                    )

                    self.fields["habilidades"].queryset = (
                        Habilidade.objects
                        .filter(
                            etapa_origem=serie.etapa,
                            competencia__in=competencias_validas,
                            ativa=True,
                        )
                        .order_by(
                            "competencia__ordem",
                            "ordem",
                            "codigo",
                            "id",
                        )
                    )

                    self.fields[
                        "habilidades_curriculo_digital"
                    ].queryset = (
                        HabilidadeCurriculoDigital.objects
                        .filter(
                            etapa=serie.etapa,
                            serie__isnull=True,
                            ativa=True,
                        )
                        .order_by("ordem")
                    )

            except (
                TypeError,
                ValueError,
                SerieAno.DoesNotExist,
                Disciplina.DoesNotExist,
            ):
                pass

        # =====================================================
        # FORMULÁRIO ENVIADO
        # Recupera as disciplinas da série selecionada.
        # =====================================================

        if "serie" in self.data:
            try:
                serie_id = int(
                    self.data.get("serie")
                )

                self.fields["disciplina"].queryset = (
                    Disciplina.objects
                    .filter(
                        series__serie_id=serie_id,
                        series__ativa=True,
                    )
                    .distinct()
                    .order_by("nome")
                )

            except (TypeError, ValueError):
                pass

        # =====================================================
        # EDIÇÃO DE UM PLANEJAMENTO EXISTENTE
        # =====================================================

        elif self.instance.pk:
            self.fields["disciplina"].queryset = (
                Disciplina.objects
                .filter(
                    series__serie=self.instance.serie,
                    series__ativa=True,
                )
                .distinct()
                .order_by("nome")
            )

    def clean_ano(self):
        ano = self.cleaned_data.get("ano")
        ano_atual = timezone.localdate().year

        if ano != ano_atual:
            raise forms.ValidationError(
                f"O planejamento deve ser do ano atual ({ano_atual})."
            )

        return ano

    def clean(self):
        cleaned_data = super().clean()

        disciplina = cleaned_data.get("disciplina")

        if disciplina:
            disciplinas_recomposicao = {
                "língua portuguesa",
                "matemática",
            }

            if (
                disciplina.nome.strip().lower()
                not in disciplinas_recomposicao
            ):
                cleaned_data["habilidades_recomposicao"] = ""
                cleaned_data[
                    "caminho_metodologico_recomposicao"
                ] = ""

            serie = cleaned_data.get("serie")

            if (
                serie
                and serie.etapa.nome != "Ensino Médio"
            ):
                cleaned_data["criterios_avaliacao_em"] = (
                    CriterioAvaliacaoCurriculoDigitalEM.objects.none()
                )

        return cleaned_data