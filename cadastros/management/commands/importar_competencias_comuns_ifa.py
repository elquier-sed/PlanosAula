import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cadastros.models import CompetenciaComumItinerario


class Command(BaseCommand):
    help = "Importa Competências Comuns dos Itinerários Formativos a partir de um CSV."

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

        with arquivo:
            leitor = csv.DictReader(
                arquivo,
                delimiter=";"
            )

            if not leitor.fieldnames:
                raise CommandError(
                    "O arquivo CSV não possui cabeçalho."
                )

            if "Competencia" not in leitor.fieldnames:
                raise CommandError(
                    'O CSV deve possuir a coluna "Competencia".'
                )

            maior_ordem = (
                CompetenciaComumItinerario.objects
                .order_by("-ordem")
                .values_list("ordem", flat=True)
                .first()
            )

            proxima_ordem = maior_ordem or 0

            for numero_linha, linha in enumerate(
                leitor,
                start=2
            ):
                descricao = (
                    linha.get("Competencia") or ""
                ).strip()

                if not descricao:
                    ignoradas += 1
                    continue

                existente = (
                    CompetenciaComumItinerario.objects
                    .filter(
                        descricao__iexact=descricao
                    )
                    .first()
                )

                if existente:
                    existentes += 1

                    self.stdout.write(
                        self.style.WARNING(
                            f"Linha {numero_linha}: "
                            f"competência já existente "
                            f"(ordem {existente.ordem})."
                        )
                    )
                    continue

                proxima_ordem += 1

                CompetenciaComumItinerario.objects.create(
                    codigo="",
                    descricao=descricao,
                    ordem=proxima_ordem,
                    ativa=True
                )

                criadas += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Criada: ordem {proxima_ordem}"
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