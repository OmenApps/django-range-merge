"""Models for the example app."""

from django.contrib.postgres.fields import DateTimeRangeField
from django.db import models


class TimeSlot(models.Model):
    """Model to test range merging with DateTimeRangeField."""

    name = models.CharField(max_length=100)
    time_range = DateTimeRangeField()

    def __str__(self):
        return f"{self.name}: {self.time_range}"
