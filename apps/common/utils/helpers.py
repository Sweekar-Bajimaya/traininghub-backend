import datetime
import os
import uuid
from functools import reduce

from django.utils import timezone


def get_today():
    return timezone.now().astimezone().date()


def get_uuid_filename(filename):
    """
    rename the file name to uuid4 and return the
    path
    """
    ext = filename.split(".")[-1]
    return "{}.{}".format(uuid.uuid4().hex, ext)


def get_upload_path(instance, filename):
    return os.path.join(
        f"uploads/{instance.__class__.__name__.lower()}", get_uuid_filename(filename)
    )


def combine_date_parts(year: int = 0, month: int = 0, day: int = 1):
    """
    Combines date parts and returns date
    :param year: Year int
    :param month: Month int
    :param day: Day int (defaults to 1)
    :return: datetime.date instance if valid and None if invalid
    """
    date_kwargs = {"day": day}

    if year:
        date_kwargs["year"] = year
    if month:
        date_kwargs["month"] = month

    try:
        return datetime.date(**date_kwargs)
    except (OverflowError, ValueError, TypeError):
        return None


def update_instance(instance: object, validated_data: dict, save: bool = True):
    """
    Sets attributes to given instance
    :param instance: Instance to update
    :param validated_data: Dictionary containing fields as keys and update
        as values
    :param save: If true, calls save() method of instance
    :return: updated instance
    """
    for attr, value in validated_data.items():
        setattr(instance, attr, value)

    if save and hasattr(instance, "save"):
        instance.save()
    return instance


def set_instance_fields(
    instance: object,
    validated_data: dict,
    save: bool = True,
    fields=(),
    pop_items: bool = False,
):
    """
    Sets attributes to given instance
    :param instance: Instance to update
    :param validated_data: Dictionary containing fields as keys and update as values
    :param save: If true, calls save() method of instance
    :param fields: name of fields that will be updated
    :param pop_items: pop items in fields from validated_data
    :return: updated instance
    """
    if fields:
        if pop_items:
            validated_data = {
                field_name: validated_data.pop(field_name)
                for field_name in fields
                if field_name in validated_data.keys()
            }
        else:
            validated_data = {
                key: value for key, value in validated_data.items() if key in fields
            }
    return update_instance(instance, validated_data, save)


def nested_getattr(
    instance: object, attributes: str, separator=".", default=None, call=True
):
    """
    Returns nested getattr and returns default if not found
    :param instance: object to get nested attributes from
    :param attributes: separator separated attributes
    :param separator: separator between nested attributes.
    :param default: default value to return if attribute was not found
    :param call: flag that determines whether to call or not if callable
    :return:
    """
    nested_attrs = attributes.split(separator)
    nested_attrs.insert(0, instance)
    try:
        attr = reduce(
            lambda instance_, attribute_: getattr(instance_, attribute_), nested_attrs
        )
        if call and callable(attr):
            return attr()
        return attr
    except AttributeError:
        return default


def _duration(months):
    """{"value", "unit", "text"} for whole months: under a year in months, otherwise whole years."""
    if months < 12:
        value, unit = max(months, 1), "MONTHS"
    else:
        value, unit = months // 12, "YEARS"
    word = unit.lower()
    return {
        "value": value,
        "unit": unit,
        "text": f"{value} {word[:-1] if value == 1 else word}",  # "1 year" / "6 years"
    }


def institute_experience(established_year):
    """Experience since `established_year`, counted from 1 January of that year (only the year is
    stored, so this is approximate). None when the year is unknown or in the future."""
    if not established_year:
        return None
    today = timezone.localdate()
    months = (today.year - established_year) * 12 + today.month - 1
    return None if months < 0 else _duration(months)


def membership_duration(joined_at):
    """How long since `joined_at` (an aware datetime, e.g. `Institute.created_at`), same shape as
    `institute_experience`. The exact date is known, so a month only counts once its day is reached."""
    if not joined_at:
        return None
    joined = timezone.localtime(joined_at).date()  # the Kathmandu day, not the UTC one
    today = timezone.localdate()
    months = (today.year - joined.year) * 12 + today.month - joined.month
    if today.day < joined.day:
        months -= 1
    return None if months < 0 else _duration(months)

