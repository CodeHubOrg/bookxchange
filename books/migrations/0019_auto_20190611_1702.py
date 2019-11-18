# Generated by Django 2.2 on 2019-06-11 16:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0018_auto_20190611_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='year_published',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(2019)]),
        ),
    ]