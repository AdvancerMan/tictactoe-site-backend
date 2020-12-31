# Generated by Django 3.1.4 on 2020-12-31 11:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticTacToe', '0002_auto_20201231_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='height',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AlterField(
            model_name='game',
            name='history',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='game',
            name='width',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AlterField(
            model_name='game',
            name='winThreshold',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(1000)]),
        ),
    ]
