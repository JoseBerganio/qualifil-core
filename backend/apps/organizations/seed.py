"""Idempotent initial organization seeding for QUALIFIL."""

from django.db import transaction

from .models import LGU, Barangay

DEFAULT_LGUS = (
    {
        "code": "SILAY",
        "name": "City of Silay",
        "province": "Negros Occidental",
        "region": "Region VI (Western Visayas)",
        "barangays": (
            ("SILAY-BAGTIC", "Bagtic"),
            ("SILAY-BALARING", "Balaring"),
            ("SILAY-BRGY-1", "Barangay I (Poblacion)"),
            ("SILAY-BRGY-2", "Barangay II (Poblacion)"),
            ("SILAY-BRGY-3", "Barangay III (Poblacion)"),
            ("SILAY-BRGY-4", "Barangay IV (Poblacion)"),
            ("SILAY-BRGY-5", "Barangay V (Poblacion)"),
            ("SILAY-CAPT-RAMON", "Captain Ramon"),
            ("SILAY-E-LOPEZ", "Eustaquio Lopez"),
            ("SILAY-GUIMBALAON", "Guimbala-on"),
            ("SILAY-GUINHALARAN", "Guinhalaran"),
            ("SILAY-HAWAIIAN", "Hawaiian"),
            ("SILAY-LANTAD", "Lantad"),
            ("SILAY-MAMBULAC", "Mambulac"),
            ("SILAY-PATAG", "Patag"),
            ("SILAY-RIZAL", "Rizal"),
        ),
    },
)


@transaction.atomic
def seed_default_organizations():
    """Create or update initial LGU and barangay records idempotently."""
    summary = {
        "lgus_created": 0,
        "lgus_updated": 0,
        "barangays_created": 0,
        "barangays_updated": 0,
    }

    for entry in DEFAULT_LGUS:
        lgu, created = LGU.objects.update_or_create(
            code=entry["code"],
            defaults={
                "name": entry["name"],
                "province": entry["province"],
                "region": entry["region"],
                "is_active": True,
            },
        )
        if created:
            summary["lgus_created"] += 1
        else:
            summary["lgus_updated"] += 1

        for brgy_code, brgy_name in entry["barangays"]:
            _, brgy_created = Barangay.objects.update_or_create(
                lgu=lgu,
                code=brgy_code,
                defaults={
                    "name": brgy_name,
                    "is_active": True,
                },
            )
            if brgy_created:
                summary["barangays_created"] += 1
            else:
                summary["barangays_updated"] += 1

    return summary
