import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cadastros.models import (
    ObjetivoAprendizagemIFAGeral,
    ObjetivoAprendizagemIFAEspecifico,
)


class Command(BaseCommand):
    help = (
        "Importa objetivos gerais e específicos de aprendizagem "
        "dos Itinerários Formativos a partir de um CSV."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "arquivo",
            type=str,
            help="Caminho do arquivo CSV."
        )

    @transaction.atomic
    def handle(self, *args, **options):
        caminho_arquivo = options["arquivo"]

        gerais_criados = 0
        gerais_existentes = 0
        especificos_criados = 0
        especificos_existentes = 0
        linhas_ignoradas = 0

        try:
            arquivo = open(
                caminho_arquivo,
                mode="r",
                encoding="utf-8-sig",
                newline=""
            )
        except FileNotFoundError:
            raise CommandError(
                f'Arquivo não encontrado: "{caminho_arquivo}"'
            )

        with arquivo:
            leitor = csv.DictReader(
                arquivo,
                delimiter=";"
            )

            if not leitor.fieldnames:
                raise CommandError(
                    "O arquivo CSV não possui cabeçalho."
                )

            campos_esperados = {
                "ObjetivoGeral",
                "ObjetivoEspecifico",
            }

            if not campos_esperados.issubset(
                set(leitor.fieldnames)
            ):
                raise CommandError(
                    'O CSV deve possuir as colunas '
                    '"ObjetivoGeral" e "ObjetivoEspecifico".'
                )

            maior_ordem_geral = (
                ObjetivoAprendizagemIFAGeral.objects
                .order_by("-ordem")
                .values_list("ordem", flat=True)
                .first()
            )

            proxima_ordem_geral = maior_ordem_geral or 0

            ordens_especificas = {}

            objetivos_gerais_processados = set()

            for numero_linha, linha in enumerate(
                leitor,
                start=2
            ):
                descricao_geral = (
                    linha.get("ObjetivoGeral") or ""
                ).strip()

                descricao_especifica = (
                    linha.get("ObjetivoEspecifico") or ""
                ).strip()

                if not descricao_geral and not descricao_especifica:
                    linhas_ignoradas += 1
                    continue

                if not descricao_geral:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Linha {numero_linha}: "
                            "ObjetivoGeral vazio. Linha ignorada."
                        )
                    )
                    linhas_ignoradas += 1
                    continue

                objetivo_geral = (
                    ObjetivoAprendizagemIFAGeral.objects
                    .filter(
                        descricao__iexact=descricao_geral
                    )
                    .first()
                )

                if objetivo_geral is None:
                    proxima_ordem_geral += 1

                    objetivo_geral = (
                        ObjetivoAprendizagemIFAGeral.objects.create(
                            descricao=descricao_geral,
                            ordem=proxima_ordem_geral,
                            ativo=True
                        )
                    )

                    gerais_criados += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Objetivo geral criado: "
                            f"ordem {objetivo_geral.ordem} - "
                            f"{descricao_geral[:80]}"
                        )
                    )

                elif objetivo_geral.id not in objetivos_gerais_processados:
                    gerais_existentes += 1

                objetivos_gerais_processados.add(
                    objetivo_geral.id
                )

                if not descricao_especifica:
                    continue

                if objetivo_geral.id not in ordens_especificas:
                    maior_ordem_especifica = (
                        ObjetivoAprendizagemIFAEspecifico.objects
                        .filter(
                            objetivo_geral=objetivo_geral
                        )
                        .order_by("-ordem")
                        .values_list("ordem", flat=True)
                        .first()
                    )

                    ordens_especificas[
                        objetivo_geral.id
                    ] = maior_ordem_especifica or 0

                existente = (
                    ObjetivoAprendizagemIFAEspecifico.objects
                    .filter(
                        objetivo_geral=objetivo_geral,
                        descricao__iexact=descricao_especifica
                    )
                    .first()
                )

                if existente:
                    especificos_existentes += 1

                    self.stdout.write(
                        self.style.WARNING(
                            f"Linha {numero_linha}: "
                            "objetivo específico já existente "
                            f"em '{descricao_geral[:50]}'."
                        )
                    )
                    continue

                ordens_especificas[
                    objetivo_geral.id
                ] += 1

                ordem_especifica = (
                    ordens_especificas[
                        objetivo_geral.id
                    ]
                )

                ObjetivoAprendizagemIFAEspecifico.objects.create(
                    objetivo_geral=objetivo_geral,
                    descricao=descricao_especifica,
                    ordem=ordem_especifica,
                    ativo=True
                )

                especificos_criados += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  Específico criado: "
                        f"ordem {ordem_especifica} - "
                        f"{descricao_especifica[:80]}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Importação concluída."
            )
        )
        self.stdout.write(
            f"Objetivos gerais criados: {gerais_criados}"
        )
        self.stdout.write(
            f"Objetivos gerais já existentes: "
            f"{gerais_existentes}"
        )
        self.stdout.write(
            f"Objetivos específicos criados: "
            f"{especificos_criados}"
        )
        self.stdout.write(
            f"Objetivos específicos já existentes: "
            f"{especificos_existentes}"
        )
        self.stdout.write(
            f"Linhas ignoradas: {linhas_ignoradas}"
        )