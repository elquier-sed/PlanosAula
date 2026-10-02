import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cadastros.models import Competencia, Disciplina, EtapaEnsino


class Command(BaseCommand):
    help = "Importa competências do Ensino Fundamental a partir de um arquivo CSV."

    def add_arguments(self, parser):
        parser.add_argument(
            "arquivo",
            type=str,
            help="Caminho do arquivo CSV a ser importado."
        )

    @transaction.atomic
    def handle(self, *args, **options):
        caminho_arquivo = options["arquivo"]

        try:
            etapa = EtapaEnsino.objects.get(
                nome="Ensino Fundamental - Anos Finais"
            )
        except EtapaEnsino.DoesNotExist:
            raise CommandError(
                'A etapa "Ensino Fundamental - Anos Finais" '
                "não foi encontrada no banco de dados."
            )

        criadas = 0
        existentes = 0
        ignoradas = 0
        erros = 0

        # Mantém uma contagem separada para cada disciplina
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

            campos_esperados = {"Disciplina", "Competencia"}

            if not leitor.fieldnames:
                raise CommandError(
                    "O arquivo CSV não possui cabeçalho."
                )

            if not campos_esperados.issubset(set(leitor.fieldnames)):
                raise CommandError(
                    "O CSV deve possuir as colunas "
                    '"Disciplina" e "Competencia".'
                )

            for numero_linha, linha in enumerate(leitor, start=2):

                nome_disciplina = (
                    linha.get("Disciplina") or ""
                ).strip()

                descricao = (
                    linha.get("Competencia") or ""
                ).strip()

                # Ignora linhas completamente vazias
                if not nome_disciplina and not descricao:
                    ignoradas += 1
                    continue

                if not nome_disciplina:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Linha {numero_linha}: "
                            "disciplina vazia. Linha ignorada."
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

                # Descobre a próxima ordem para a disciplina
                if disciplina.id not in ordens:
                    maior_ordem = (
                        Competencia.objects
                        .filter(
                            etapa=etapa,
                            disciplina=disciplina
                        )
                        .order_by("-ordem")
                        .values_list("ordem", flat=True)
                        .first()
                    )

                    ordens[disciplina.id] = maior_ordem or 0

                # Verifica se essa competência já existe
                competencia_existente = Competencia.objects.filter(
                    etapa=etapa,
                    disciplina=disciplina,
                    descricao__iexact=descricao
                ).first()

                if competencia_existente:
                    existentes += 1

                    self.stdout.write(
                        self.style.WARNING(
                            f"Já existente: "
                            f"{nome_disciplina} - "
                            f"ordem {competencia_existente.ordem}"
                        )
                    )

                    continue

                ordens[disciplina.id] += 1

                Competencia.objects.create(
                    etapa=etapa,
                    disciplina=disciplina,
                    area_conhecimento=None,
                    codigo="",
                    descricao=descricao,
                    ordem=ordens[disciplina.id],
                    ativa=True
                )

                criadas += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Criada: {nome_disciplina} - "
                        f"ordem {ordens[disciplina.id]}"
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