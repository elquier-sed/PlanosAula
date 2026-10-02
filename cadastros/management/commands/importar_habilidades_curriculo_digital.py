import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cadastros.models import (
    EtapaEnsino,
    SerieAno,
    HabilidadeCurriculoDigital,
)


class Command(BaseCommand):
    help = (
        "Importa habilidades do Currículo Digital "
        "do Ensino Fundamental e Ensino Médio."
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

        criadas = 0
        existentes = 0
        ignoradas = 0
        erros = 0

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

        # Guarda a última ordem utilizada por etapa/série.
        ordens = {}

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
                "Etapa",
                "Serie",
                "Codigo",
                "Habilidade",
            }

            if not campos_esperados.issubset(
                set(leitor.fieldnames)
            ):
                raise CommandError(
                    "O CSV deve possuir as colunas: "
                    "Etapa, Serie, Codigo e Habilidade."
                )

            for numero_linha, linha in enumerate(
                leitor,
                start=2
            ):
                nome_etapa = (
                    linha.get("Etapa") or ""
                ).strip()

                nome_serie = (
                    linha.get("Serie") or ""
                ).strip()

                codigo = (
                    linha.get("Codigo") or ""
                ).strip()

                descricao = (
                    linha.get("Habilidade") or ""
                ).strip()

                # Linha completamente vazia.
                if not any([
                    nome_etapa,
                    nome_serie,
                    codigo,
                    descricao,
                ]):
                    ignoradas += 1
                    continue

                # Etapa é obrigatória.
                if not nome_etapa:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            "etapa não informada."
                        )
                    )
                    erros += 1
                    continue

                # Código é obrigatório.
                if not codigo:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            "código não informado."
                        )
                    )
                    erros += 1
                    continue

                # Habilidade é obrigatória.
                if not descricao:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            "habilidade não informada."
                        )
                    )
                    erros += 1
                    continue

                # Localiza a etapa.
                try:
                    etapa = EtapaEnsino.objects.get(
                        nome__iexact=nome_etapa
                    )
                except EtapaEnsino.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            f'etapa "{nome_etapa}" não encontrada.'
                        )
                    )
                    erros += 1
                    continue
                except EtapaEnsino.MultipleObjectsReturned:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            f'existe mais de uma etapa "{nome_etapa}".'
                        )
                    )
                    erros += 1
                    continue

                # Série é opcional.
                # No EF deverá estar preenchida.
                # No EM ficará vazia.
                serie = None

                if nome_serie:
                    try:
                        serie = SerieAno.objects.get(
                            etapa=etapa,
                            nome__iexact=nome_serie
                        )
                    except SerieAno.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Linha {numero_linha}: "
                                f'série "{nome_serie}" não encontrada '
                                f'na etapa "{nome_etapa}".'
                            )
                        )
                        erros += 1
                        continue
                    except SerieAno.MultipleObjectsReturned:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Linha {numero_linha}: "
                                f'existe mais de uma série '
                                f'"{nome_serie}" na etapa '
                                f'"{nome_etapa}".'
                            )
                        )
                        erros += 1
                        continue

                # Verifica duplicidade pelo código dentro da etapa.
                existente = (
                    HabilidadeCurriculoDigital.objects
                    .filter(
                        etapa=etapa,
                        codigo__iexact=codigo
                    )
                    .first()
                )

                if existente:
                    existentes += 1

                    self.stdout.write(
                        self.style.WARNING(
                            f"Linha {numero_linha}: "
                            f'habilidade "{codigo}" já existente.'
                        )
                    )
                    continue

                # A ordenação é independente para cada
                # combinação etapa/série.
                chave_ordem = (
                    etapa.id,
                    serie.id if serie else None,
                )

                if chave_ordem not in ordens:
                    maior_ordem = (
                        HabilidadeCurriculoDigital.objects
                        .filter(
                            etapa=etapa,
                            serie=serie
                        )
                        .order_by("-ordem")
                        .values_list(
                            "ordem",
                            flat=True
                        )
                        .first()
                    )

                    ordens[chave_ordem] = maior_ordem or 0

                ordens[chave_ordem] += 1

                HabilidadeCurriculoDigital.objects.create(
                    etapa=etapa,
                    serie=serie,
                    codigo=codigo,
                    descricao=descricao,
                    ordem=ordens[chave_ordem],
                    ativa=True,
                )

                criadas += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Linha {numero_linha}: criada - "
                        f"{nome_etapa} / "
                        f"{nome_serie or 'todas as séries'} / "
                        f"{codigo}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS("Importação concluída.")
        )
        self.stdout.write(
            f"Habilidades criadas: {criadas}"
        )
        self.stdout.write(
            f"Habilidades já existentes: {existentes}"
        )
        self.stdout.write(
            f"Linhas vazias ignoradas: {ignoradas}"
        )
        self.stdout.write(
            f"Linhas com erro: {erros}"
        )