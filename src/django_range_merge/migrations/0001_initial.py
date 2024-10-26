"""This migration creates the range_merge aggregate function."""

from django.db import migrations


class Migration(migrations.Migration):
    """Migration to create the range_merge aggregate function."""

    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(
            sql=[("CREATE OR REPLACE AGGREGATE range_merge(anyrange)(sfunc=range_merge, stype=anyrange);")],
            reverse_sql=[("DROP AGGREGATE IF EXISTS range_merge(anyrange);")],
        )
    ]
