import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cadastros.models import (
    AreaConhecimento,
    Competencia,
    EtapaEnsino,
)


class Command(BaseCommand):
    help = "Importa competências do Ensino Médio a partir de um CSV."

    def add_arguments(self, parser):
        parser.add_argument(
            "arquivo",
            type=str,
            help="Caminho do arquivo CSV."
        )

    @transaction.atomic
    def handle(self, *args, **options):
        caminho_arquivo = options["arquivo"]

        try:
            etapa = EtapaEnsino.objects.get(
                nome="Ensino Médio"
            )
        except EtapaEnsino.DoesNotExist:
            raise CommandError(
                'A etapa "Ensino Médio" não foi encontrada.'
            )

        criadas = 0
        existentes = 0
        ignoradas = 0
        erros = 0

        ordens = {}

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

            campos_esperados = {
                "Area",
                "Competencia",
            }

            if not leitor.fieldnames:
                raise CommandError(
                    "O arquivo CSV não possui cabeçalho."
                )

            if not campos_esperados.issubset(
                set(leitor.fieldnames)
            ):
                raise CommandError(
                    'O CSV deve possuir as colunas '
                    '"Area" e "Competencia".'
                )

            for numero_linha, linha in enumerate(
                leitor,
                start=2
            ):
                nome_area = (
                    linha.get("Area") or ""
                ).strip()

                descricao = (
                    linha.get("Competencia") or ""
                ).strip()

                # Ignora linhas completamente vazias
                if not nome_area and not descricao:
                    ignoradas += 1
                    continue

                if not nome_area:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Linha {numero_linha}: "
                            "área vazia. Linha ignorada."
                        )
                    )
                    erros += 1
                    continue

                if not descricao:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Linha {numero_linha}: "
                            "competência vazia. Linha ignorada."
                        )
                    )
                    erros += 1
                    continue

                try:
                    area = AreaConhecimento.objects.get(
                        nome__iexact=nome_area
                    )
                except AreaConhecimento.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            f'área "{nome_area}" '
                            "não encontrada."
                        )
                    )
                    erros += 1
                    continue

                if area.id not in ordens:
                    maior_ordem = (
                        Competencia.objects
                        .filter(
                            etapa=etapa,
                            area_conhecimento=area
                        )
                        .order_by("-ordem")
                        .values_list("ordem", flat=True)
                        .first()
                    )

                    ordens[area.id] = maior_ordem or 0

                competencia_existente = (
                    Competencia.objects
                    .filter(
                        etapa=etapa,
                        area_conhecimento=area,
                        descricao__iexact=descricao
                    )
                    .first()
                )

                if competencia_existente:
                    existentes += 1

                    self.stdout.write(
                        self.style.WARNING(
                            f"Já existente: "
                            f"{nome_area} - "
                            f"ordem "
                            f"{competencia_existente.ordem}"
                        )
                    )
                    continue

                ordens[area.id] += 1

                Competencia.objects.create(
                    etapa=etapa,
                    disciplina=None,
                    area_conhecimento=area,
                    codigo="",
                    descricao=descricao,
                    ordem=ordens[area.id],
                    ativa=True
                )

                criadas += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Criada: {nome_area} - "
                        f"ordem {ordens[area.id]}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Importação concluída."
            )
        )
        self.stdout.write(
            f"Competências criadas: {criadas}"
        )
        self.stdout.write(
            f"Competências já existentes: {existentes}"
        )
        self.stdout.write(
            f"Linhas vazias ignoradas: {ignoradas}"
        )
        self.stdout.write(
            f"Linhas com erro: {erros}"
        )