"""Pytest configuration file."""

import pytest
from django.core.management import call_command


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Configure the test database."""
    with django_db_blocker.unblock():
        # Load any initial data your tests need
        try:
            call_command("migrate", "--noinput")
        except Exception as e:
            pytest.fail(f"Failed to apply migrations: {e}")


@pytest.fixture
def time_slots(db):
    """Create test time slots with overlapping ranges."""
    from django.utils import timezone
    from psycopg2.extras import DateTimeTZRange

    from example_project.example.models import TimeSlot

    now = timezone.now()

    # Create three time slots with overlapping ranges
    slot1 = TimeSlot.objects.create(
        name="Morning", time_range=DateTimeTZRange(now.replace(hour=8, minute=0), now.replace(hour=12, minute=0))
    )

    slot2 = TimeSlot.objects.create(
        name="Mid-day", time_range=DateTimeTZRange(now.replace(hour=11, minute=0), now.replace(hour=15, minute=0))
    )

    slot3 = TimeSlot.objects.create(
        name="Afternoon", time_range=DateTimeTZRange(now.replace(hour=14, minute=0), now.replace(hour=18, minute=0))
    )

    return [slot1, slot2, slot3]
