"""Test cases for the django-range-merge package."""

import pytest
from django.conf import settings
from django.db.models import F
from django.db.utils import DataError
from django.utils import timezone
from psycopg2.errors import DataException
from psycopg2.extras import DateTimeTZRange

from example_project.example.models import TimeSlot


def test_succeeds() -> None:
    """Test that the test suite runs."""
    assert 0 == 0


def test_settings() -> None:
    """Test that the settings are configured correctly."""
    assert settings.USE_TZ is True
    assert "django_range_merge" in settings.INSTALLED_APPS
    assert "example_project.example" in settings.INSTALLED_APPS


@pytest.mark.django_db
class TestTimeSlotModel:
    """Test cases for the TimeSlot model."""

    def test_create_timeslot(self):
        """Test creation of a TimeSlot instance."""
        now = timezone.now()
        time_slot = TimeSlot.objects.create(
            name="Test Slot", time_range=DateTimeTZRange(now.replace(hour=8, minute=0), now.replace(hour=12, minute=0))
        )
        assert time_slot.name == "Test Slot"
        assert time_slot.time_range.lower == now.replace(hour=8, minute=0)
        assert time_slot.time_range.upper == now.replace(hour=12, minute=0)

    def test_invalid_range(self):
        """Test that invalid time ranges raise ValidationError."""
        now = timezone.now()
        with pytest.raises(DataError):
            TimeSlot.objects.create(
                name="Invalid Slot",
                time_range=DateTimeTZRange(
                    now.replace(hour=12, minute=0), now.replace(hour=8, minute=0)  # End time  # Start time
                ),
            )

    def test_str_representation(self):
        """Test the string representation of TimeSlot."""
        now = timezone.now()
        time_slot = TimeSlot.objects.create(
            name="Test Slot", time_range=DateTimeTZRange(now.replace(hour=8, minute=0), now.replace(hour=12, minute=0))
        )
        assert str(time_slot) == f"Test Slot: {time_slot.time_range}"


@pytest.mark.django_db
class TestRangeMerge:
    """Test cases for the range_merge aggregate function."""

    def test_range_merge_basic(self, time_slots):
        """Test that range_merge correctly merges overlapping time ranges."""
        from django.db.models import Aggregate

        class RangeMerge(Aggregate):
            function = "range_merge"
            name = "range_merge"

        merged_range = TimeSlot.objects.aggregate(merged=RangeMerge(F("time_range")))["merged"]

        earliest_start = min(slot.time_range.lower for slot in time_slots)
        latest_end = max(slot.time_range.upper for slot in time_slots)

        assert merged_range.lower == earliest_start
        assert merged_range.upper == latest_end

    def test_range_merge_empty(self):
        """Test that range_merge returns None for empty querysets."""
        from django.db.models import Aggregate

        class RangeMerge(Aggregate):
            function = "range_merge"
            name = "range_merge"

        merged_range = TimeSlot.objects.none().aggregate(merged=RangeMerge(F("time_range")))["merged"]

        assert merged_range is None

    def test_range_merge_single(self):
        """Test that range_merge works correctly with a single range."""
        from django.db.models import Aggregate

        class RangeMerge(Aggregate):
            function = "range_merge"
            name = "range_merge"

        now = timezone.now()
        slot = TimeSlot.objects.create(
            name="Single", time_range=DateTimeTZRange(now.replace(hour=8, minute=0), now.replace(hour=12, minute=0))
        )

        merged_range = TimeSlot.objects.filter(pk=slot.pk).aggregate(merged=RangeMerge(F("time_range")))["merged"]

        assert merged_range.lower == slot.time_range.lower
        assert merged_range.upper == slot.time_range.upper

    def test_range_merge_non_overlapping(self):
        """Test that range_merge correctly handles non-overlapping ranges."""
        from django.db.models import Aggregate

        class RangeMerge(Aggregate):
            function = "range_merge"
            name = "range_merge"

        now = timezone.now()

        slot1 = TimeSlot.objects.create(
            name="Morning", time_range=DateTimeTZRange(now.replace(hour=8, minute=0), now.replace(hour=10, minute=0))
        )

        slot2 = TimeSlot.objects.create(
            name="Afternoon", time_range=DateTimeTZRange(now.replace(hour=14, minute=0), now.replace(hour=16, minute=0))
        )

        merged_range = TimeSlot.objects.filter(pk__in=[slot1.pk, slot2.pk]).aggregate(
            merged=RangeMerge(F("time_range"))
        )["merged"]

        assert merged_range.lower == slot1.time_range.lower
        assert merged_range.upper == slot2.time_range.upper

    def test_range_merge_adjacent(self):
        """Test that range_merge correctly handles adjacent ranges."""
        from django.db.models import Aggregate

        class RangeMerge(Aggregate):
            function = "range_merge"
            name = "range_merge"

        now = timezone.now()

        slot1 = TimeSlot.objects.create(
            name="Morning", time_range=DateTimeTZRange(now.replace(hour=8, minute=0), now.replace(hour=12, minute=0))
        )

        slot2 = TimeSlot.objects.create(
            name="Afternoon", time_range=DateTimeTZRange(now.replace(hour=12, minute=0), now.replace(hour=16, minute=0))
        )

        merged_range = TimeSlot.objects.filter(pk__in=[slot1.pk, slot2.pk]).aggregate(
            merged=RangeMerge(F("time_range"))
        )["merged"]

        assert merged_range.lower == slot1.time_range.lower
        assert merged_range.upper == slot2.time_range.upper
