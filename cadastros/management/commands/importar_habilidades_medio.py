import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cadastros.models import (
    AreaConhecimento,
    Competencia,
    EtapaEnsino,
    Habilidade,
    SerieAno,
)


class Command(BaseCommand):
    help = "Importa habilidades do Ensino Médio a partir de um CSV."

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
                nome__iexact="Ensino Médio"
            )
        except EtapaEnsino.DoesNotExist:
            raise CommandError(
                'A etapa "Ensino Médio" não foi encontrada.'
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

        # Controla a ordem das habilidades dentro de cada competência.
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
                "Area",
                "Competencia",
                "SerieOrigem",
                "Codigo",
                "Habilidade",
            }

            if not campos_esperados.issubset(
                set(leitor.fieldnames)
            ):
                raise CommandError(
                    "O CSV deve possuir as colunas: "
                    "Area, Competencia, SerieOrigem, "
                    "Codigo e Habilidade."
                )

            for numero_linha, linha in enumerate(
                leitor,
                start=2
            ):
                nome_area = (
                    linha.get("Area") or ""
                ).strip()

                numero_competencia = (
                    linha.get("Competencia") or ""
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

                # Linha completamente vazia
                if not any([
                    nome_area,
                    numero_competencia,
                    nome_serie,
                    codigo,
                    descricao,
                ]):
                    ignoradas += 1
                    continue

                # Campos obrigatórios
                if not nome_area:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            "Área não informada."
                        )
                    )
                    erros += 1
                    continue

                if not numero_competencia:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            "Competência não informada."
                        )
                    )
                    erros += 1
                    continue

                if not descricao:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            "Habilidade não informada."
                        )
                    )
                    erros += 1
                    continue

                # Competência deve ser um número de ordem.
                try:
                    ordem_competencia = int(
                        numero_competencia
                    )
                except ValueError:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            f'Competência "{numero_competencia}" '
                            "não é um número válido."
                        )
                    )
                    erros += 1
                    continue

                # Localiza a área.
                try:
                    area = AreaConhecimento.objects.get(
                        nome__iexact=nome_area
                    )
                except AreaConhecimento.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            f'área "{nome_area}" não encontrada.'
                        )
                    )
                    erros += 1
                    continue
                except AreaConhecimento.MultipleObjectsReturned:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            f'existe mais de uma área "{nome_area}".'
                        )
                    )
                    erros += 1
                    continue

                # Localiza a competência pela combinação:
                # Ensino Médio + Área + Ordem.
                try:
                    competencia = Competencia.objects.get(
                        etapa=etapa,
                        area_conhecimento=area,
                        ordem=ordem_competencia,
                    )
                except Competencia.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            f"competência {ordem_competencia} "
                            f'da área "{nome_area}" '
                            "não encontrada."
                        )
                    )
                    erros += 1
                    continue
                except Competencia.MultipleObjectsReturned:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Linha {numero_linha}: "
                            f"há mais de uma competência com "
                            f"ordem {ordem_competencia} "
                            f'na área "{nome_area}".'
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
                                f'série "{nome_serie}" '
                                "não encontrada no Ensino Médio."
                            )
                        )
                        erros += 1
                        continue
                    except SerieAno.MultipleObjectsReturned:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Linha {numero_linha}: "
                                f'existe mais de uma série '
                                f'"{nome_serie}" no Ensino Médio.'
                            )
                        )
                        erros += 1
                        continue

                # Evita duplicidade.
                # Se houver código, ele é nossa principal referência.
                if codigo:
                    existente = Habilidade.objects.filter(
                        etapa_origem=etapa,
                        competencia=competencia,
                        codigo__iexact=codigo,
                    ).first()
                else:
                    existente = Habilidade.objects.filter(
                        etapa_origem=etapa,
                        competencia=competencia,
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

                # Descobre a próxima ordem dentro da competência.
                if competencia.id not in ordens:
                    maior_ordem = (
                        Habilidade.objects
                        .filter(
                            etapa_origem=etapa,
                            competencia=competencia
                        )
                        .order_by("-ordem")
                        .values_list("ordem", flat=True)
                        .first()
                    )

                    ordens[competencia.id] = maior_ordem or 0

                ordens[competencia.id] += 1

                Habilidade.objects.create(
                    disciplina=None,
                    competencia=competencia,
                    etapa_origem=etapa,
                    serie_origem=serie_origem,
                    codigo=codigo,
                    descricao=descricao,
                    ordem=ordens[competencia.id],
                    ativa=True,
                )

                criadas += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Linha {numero_linha}: criada - "
                        f"{nome_area} / "
                        f"Competência {ordem_competencia} / "
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