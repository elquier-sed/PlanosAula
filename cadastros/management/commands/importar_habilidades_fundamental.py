import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cadastros.models import (
    Disciplina,
    EtapaEnsino,
    Habilidade,
    SerieAno,
)


class Command(BaseCommand):
    help = (
        "Importa habilidades do Ensino Fundamental - "
        "Anos Finais a partir de um CSV."
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
            etapa = EtapaEnsino.objects.get(
                nome__iexact="Ensino Fundamental - Anos Finais"
            )
        except EtapaEnsino.DoesNotExist:
            raise CommandError(
                'A etapa "Ensino Fundamental - Anos Finais" '
                "não foi encontrada."
            )

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

        # Guarda a última ordem utilizada em cada disciplina.
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
                "Disciplina",
                "SerieOrigem",
                "Codigo",
                "Habilidade",
            }

            if not campos_esperados.issubset(
                set(leitor.fieldnames)
            ):
                raise CommandError(
                    "O CSV deve possuir as colunas: "
                    "Disciplina, SerieOrigem, Codigo e Habilidade."
                )

            for numero_linha, linha in enumerate(
                leitor,
                start=2
            ):
                nome_disciplina = (
                    linha.get("Disciplina") or ""
                ).strip()

                nome_serie = (
                    linha.get("SerieOrigem") or ""
                ).strip()

                codigo = (
                    linha.get("Codigo") or ""
                ).strip()

                descricao = (
                    linha.get("Habilidade") or ""
                ).strip()

                # Ignora linha completamente vazia.
                if not any([
                    nome_disciplina,
                    nome_serie,
                    codigo,
                    descricao,
                ]):
                    ignoradas += 1
                    continue

                # Disciplina é obrigatória.
                if not nome_disciplina:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            "disciplina não informada."
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

                # Localiza a disciplina.
                try:
                    disciplina = Disciplina.objects.get(
                        nome__iexact=nome_disciplina
                    )
                except Disciplina.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            f'disciplina "{nome_disciplina}" '
                            "não encontrada."
                        )
                    )
                    erros += 1
                    continue
                except Disciplina.MultipleObjectsReturned:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            f'existe mais de uma disciplina chamada '
                            f'"{nome_disciplina}".'
                        )
                    )
                    erros += 1
                    continue

                # Série de origem é opcional.
                serie_origem = None

                if nome_serie:
                    try:
                        serie_origem = SerieAno.objects.get(
                            etapa=etapa,
                            nome__iexact=nome_serie
                        )
                    except SerieAno.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Linha {numero_linha}: "
                                f'série "{nome_serie}" não encontrada '
                                "no Ensino Fundamental - Anos Finais."
                            )
                        )
                        erros += 1
                        continue
                    except SerieAno.MultipleObjectsReturned:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Linha {numero_linha}: "
                                f'existe mais de uma série '
                                f'"{nome_serie}" nesta etapa.'
                            )
                        )
                        erros += 1
                        continue

                # Verifica duplicidade.
                # Se houver código, usamos código + disciplina.
                if codigo:
                    existente = Habilidade.objects.filter(
                        etapa_origem=etapa,
                        disciplina=disciplina,
                        codigo__iexact=codigo,
                    ).first()

                # Se não houver código, usamos o texto da habilidade.
                else:
                    existente = Habilidade.objects.filter(
                        etapa_origem=etapa,
                        disciplina=disciplina,
                        descricao__iexact=descricao,
                    ).first()

                if existente:
                    existentes += 1

                    self.stdout.write(
                        self.style.WARNING(
                            f"Linha {numero_linha}: "
                            f'habilidade "{codigo or descricao[:40]}" '
                            "já existente."
                        )
                    )
                    continue

                # Descobre a próxima ordem da disciplina.
                if disciplina.id not in ordens:
                    maior_ordem = (
                        Habilidade.objects
                        .filter(
                            etapa_origem=etapa,
                            disciplina=disciplina
                        )
                        .order_by("-ordem")
                        .values_list("ordem", flat=True)
                        .first()
                    )

                    ordens[disciplina.id] = maior_ordem or 0

                ordens[disciplina.id] += 1

                Habilidade.objects.create(
                    disciplina=disciplina,
                    competencia=None,
                    etapa_origem=etapa,
                    serie_origem=serie_origem,
                    codigo=codigo,
                    descricao=descricao,
                    ordem=ordens[disciplina.id],
                    ativa=True,
                )

                criadas += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Linha {numero_linha}: criada - "
                        f"{nome_disciplina} / "
                        f"{nome_serie or 'sem série específica'} / "
                        f"{codigo or 'sem código'}"
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