# Generated by Django 3.1.4 on 2021-01-07 06:21

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('width', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('height', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('win_threshold', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('colors', models.JSONField()),
                ('order', models.JSONField(blank=True, default=list)),
                ('history', models.JSONField(blank=True, default=list)),
                ('field', models.JSONField(blank=True, default=None, null=True)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('started', models.BooleanField(default=False)),
                ('win_line_start_i', models.IntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('win_line_start_j', models.IntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('win_line_direction_i', models.IntegerField(blank=True, default=None, null=True)),
                ('win_line_direction_j', models.IntegerField(blank=True, default=None, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('players', models.ManyToManyField(related_name='tic_tac_toe_games', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
