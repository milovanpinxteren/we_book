# custom_tags.py

from django import template

register = template.Library()

@register.filter(name="table_reservations")
def table_reservations(tables, date, reservations):
    booked_tables = []
    for table in tables:
        if any(reservation.reservation_date == date and reservation.table.table_nr == table for reservation in reservations):
            booked_tables.append(table)
    return booked_tables
