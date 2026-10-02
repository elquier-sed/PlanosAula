import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cadastros.models import RecursoPedagogico


class Command(BaseCommand):
    help = "Importa recursos pedagógicos a partir de um CSV."

    def add_arguments(self, parser):
        parser.add_argument(
            "arquivo",
            type=str,
            help="Caminho do arquivo CSV."
        )

    @transaction.atomic
    def handle(self, *args, **options):
        caminho_arquivo = options["arquivo"]

        criados = 0
        existentes = 0
        ignorados = 0

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

            if "Recurso" not in leitor.fieldnames:
                raise CommandError(
                    'O CSV deve possuir a coluna "Recurso".'
                )

            maior_ordem = (
                RecursoPedagogico.objects
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
                    linha.get("Recurso") or ""
                ).strip()

                if not descricao:
                    ignorados += 1
                    continue

                existente = (
                    RecursoPedagogico.objects
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
                            "recurso já existente "
                            f"(ordem {existente.ordem})."
                        )
                    )
                    continue

                proxima_ordem += 1

                RecursoPedagogico.objects.create(
                    descricao=descricao,
                    ordem=proxima_ordem,
                    ativo=True
                )

                criados += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Criado: ordem {proxima_ordem} - "
                        f"{descricao[:80]}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS("Importação concluída.")
        )
        self.stdout.write(
            f"Recursos criados: {criados}"
        )
        self.stdout.write(
            f"Recursos já existentes: {existentes}"
        )
        self.stdout.write(
            f"Linhas vazias ignoradas: {ignorados}"
        )