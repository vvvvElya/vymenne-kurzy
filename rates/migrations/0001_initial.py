# Generated by Django 5.1.4 on 2025-03-14 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeRateTimeSeries',
            fields=[
                ('date', models.DateField(primary_key=True, serialize=False)),
                ('usd_eur', models.DecimalField(decimal_places=6, max_digits=10)),
                ('cny_eur', models.DecimalField(decimal_places=6, max_digits=10)),
                ('huf_eur', models.DecimalField(decimal_places=6, max_digits=10)),
                ('pln_eur', models.DecimalField(decimal_places=6, max_digits=10)),
                ('czk_eur', models.DecimalField(decimal_places=6, max_digits=10)),
                ('gbp_eur', models.DecimalField(decimal_places=6, max_digits=10)),
            ],
            options={
                'db_table': 'exchange_rates_time_series',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('USD', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('CNY', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('HUF', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('PLN', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('CZK', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('GBP', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
            ],
            options={
                'db_table': 'exchange_rates',
            },
        ),
        migrations.CreateModel(
            name='Prediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('currency', models.CharField(max_length=3)),
                ('predicted_value', models.DecimalField(decimal_places=4, max_digits=10)),
                ('model_name', models.CharField(max_length=50)),
                ('confidence_interval', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'predictions',
            },
        ),
        migrations.CreateModel(
            name='ExchangeRateNormalized',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('currency', models.CharField(max_length=3)),
                ('rate_value', models.DecimalField(decimal_places=4, max_digits=10)),
            ],
            options={
                'db_table': 'exchange_rates_normalized',
                'unique_together': {('date', 'currency')},
            },
        ),
    ]
