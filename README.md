# django-range-merge

Enables the `range_merge` Aggregate for Django on Postgres. `range_merge` "Computes the smallest range that includes ... the given ranges".

![Visualization of what range_merge does, returning smallest range that includes input ranges in the QuerySet](https://raw.githubusercontent.com/jacklinke/django-range-merge/main/media/range_merge.png)

This package should only be used with Django projects using the Postgres database. See [Postgres docs on Range Functions](https://www.postgresql.org/docs/14/functions-range.html#RANGE-FUNCTIONS-TABLE).

Note: This app is still a work-in-progress, but currently works. Tests have not yet been implemented.


## Installing

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "django_range_merge",
    ...
]
```

Migrate to apply the aggregation to your database:

```bash
> python manage.py migrate
````

## Getting Started

Here is a quick example. We have an `Event` model with two different range fields: `period`, which contains the datetime range period during which the Event occurs; and `potential_visitors`, which is an approximation of the minimum and maximum number of people attending the Event.

We want two different views to help Event organizers understand some aggregate details about Events.

- **range_of_visitors_this_month**: Show the overall lowest and greatest number of people we expect for all events this month
- **overall_dates_of_funded_events**: Shows the overall range of dates for Events which are funded (the `is_funded` BooleanField is set to True)

models.py

```python
class Event(models.Model):
    name = models.CharField(max_length=30)
    period = models.DateTimeRangeField(help_text="The period of time this event covers")
    potential_visitors = models.IntegerRangeField(help_text="The range of visitors expected at this event")
    is_funded = BooleanField(default=False)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        return self.name

```

date_utils.py

```python
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from psycopg2.extras import DateTimeRange

def get_month_range():
    today = timezone.now().date()
    if today.day > 25:
        today += timezone.timedelta(7)
    this_month_start = today.replace(day=1)
    next_month_start = this_month_start + relativedelta(months=1)
    return DateTimeRange(this_month_start, next_month_start)
```

views.py

```python
from django.template.response import TemplateResponse

from .date_utils import get_month_range

def range_of_visitors_this_month(request):
    """
    e.g., given the following instance: 
        {"id" : 1, "name" : "Birthday",     "potential_visitors" : "[2, 3)", ...}
        {"id" : 2, "name" : "Bake Sale",    "potential_visitors" : "[30, 50)", ...}
        {"id" : 3, "name" : "Band Camp",    "potential_visitors" : "[22, 28)", ...}
        {"id" : 4, "name" : "Cooking Show", "potential_visitors" : "[7, 20)", ...}
        {"id" : 5, "name" : "Pajama Day",   "potential_visitors" : "[15, 30)", ...}
    
    The result would be:
        {'output': NumericRange(2, 50, '[)')}
    """
    template = "base.html"
    
    context = Event.objects.filter(period__overlaps=get_month_range()).aggregate(
        output=Aggregate(F("potential_visitors"), function="range_merge")
    )

    return TemplateResponse(request, template, context)

def overall_dates_of_funded_events(request):
    template = "base.html"
    
    context = Event.objects.filter(is_funded=True).aggregate(
        output=Aggregate(F("period"), function="range_merge")
    )
    # Example result: {'output': DateTimeRange("2022-10-01", "2022-12-07", '[)')}

    return TemplateResponse(request, template, context)

```

base.html

```html
<html>
    <head></head>
    <body>
        {{ output }}
    </body>
</html>
```

## License

The code in this repository is licensed under The MIT License. See LICENSE.md in the repository for more details.


## Contributing

Contributions are very welcome.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to have a discussion about your new feature idea with the maintainers prior to
beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.
