import secrets

import apps.common.validators
from django.db import migrations, models


def fill_random_pan_vat(apps, schema_editor):
    """Institutes registered before this column existed get a random, unique nine-digit number
    so the unique index can be built. It is not their real PAN/VAT: replace it with the real one."""
    Institute = apps.get_model("institutes", "Institute")
    used = set()
    for pk in Institute.objects.filter(pan_vat_number__isnull=True).values_list("pk", flat=True):
        number = f"{secrets.randbelow(10**9):09d}"
        while number in used:
            number = f"{secrets.randbelow(10**9):09d}"
        used.add(number)
        Institute.objects.filter(pk=pk).update(pan_vat_number=number)


class Migration(migrations.Migration):

    dependencies = [
        ('institutes', '0002_institute_profile_split'),
    ]

    operations = [
        migrations.AddField(
            model_name='institute',
            name='pan_vat_number',
            field=models.CharField(max_length=9, null=True),
        ),
        migrations.RunPython(fill_random_pan_vat, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='institute',
            name='pan_vat_number',
            field=models.CharField(max_length=9, unique=True),
        ),
        migrations.AddField(
            model_name='institutecontact',
            name='telephone_number',
            field=models.CharField(blank=True, max_length=25, validators=[apps.common.validators.validate_phone_number]),
        ),
    ]
