from django import template
from calendar import monthcalendar
from datetime import date

register = template.Library()

@register.simple_tag
def get_calendar():
    today = date.today()
    cal = monthcalendar(today.year, today.month)
    return {
        'calendar': cal,
        'today': today.day,
        'month_name': today.strftime('%B %Y'),
        'weekdays': ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    }