import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cadastros.models import Referencia


class Command(BaseCommand):
    help = "Importa referências a partir de um CSV."

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

            if "Referencia" not in leitor.fieldnames:
                raise CommandError(
                    'O CSV deve possuir a coluna "Referencia".'
                )

            maior_ordem = (
                Referencia.objects
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
                    linha.get("Referencia") or ""
                ).strip()

                if not descricao:
                    ignoradas += 1
                    continue

                existente = (
                    Referencia.objects
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
                            "referência já existente "
                            f"(ordem {existente.ordem})."
                        )
                    )
                    continue

                proxima_ordem += 1

                Referencia.objects.create(
                    descricao=descricao,
                    ordem=proxima_ordem,
                    ativa=True
                )

                criadas += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Criada: ordem {proxima_ordem} - "
                        f"{descricao[:80]}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS("Importação concluída.")
        )
        self.stdout.write(
            f"Referências criadas: {criadas}"
        )
        self.stdout.write(
            f"Referências já existentes: {existentes}"
        )
        self.stdout.write(
            f"Linhas vazias ignoradas: {ignoradas}"
        )