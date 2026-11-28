"""Management command to seed initial LGU and barangay records."""

from django.core.management.base import BaseCommand

from apps.organizations.seed import seed_default_organizations


class Command(BaseCommand):
    help = "Seed initial LGU and barangay records (idempotent)."

    def handle(self, *args, **options):
        summary = seed_default_organizations()
        self.stdout.write(
            self.style.SUCCESS(
                "Seeded organizations: "
                f"lgus(created={summary['lgus_created']}, updated={summary['lgus_updated']}), "
                f"barangays(created={summary['barangays_created']}, updated={summary['barangays_updated']})."
            )
        )
