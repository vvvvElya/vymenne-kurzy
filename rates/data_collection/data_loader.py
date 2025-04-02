import pandas as pd
from django.db import connection
from rates.models import ExchangeRate, ExchangeRateNormalized, Currency
from datetime import datetime, timedelta
from rates.models import ExchangeRateNormalized

def save_exchange_rates(date, rates):
    """
    Сохраняет курсы валют, даже если данных за сегодня нет.
    """
    last_known_rates = ExchangeRate.objects.order_by('-date').first()

    # Если записи за сегодня нет, создаём её
    if not ExchangeRate.objects.filter(date=date).exists():
        ExchangeRate.objects.create(
            date=date,
            USD=rates.get('USD', last_known_rates.USD if last_known_rates else None),
            CNY=rates.get('CNY', last_known_rates.CNY if last_known_rates else None),
            HUF=rates.get('HUF', last_known_rates.HUF if last_known_rates else None),
            PLN=rates.get('PLN', last_known_rates.PLN if last_known_rates else None),
            CZK=rates.get('CZK', last_known_rates.CZK if last_known_rates else None),
            GBP=rates.get('GBP', last_known_rates.GBP if last_known_rates else None),
        )
        print(f"✅ Данные за {date} успешно сохранены.")
    else:
        print(f"🔹 Данные за {date} уже есть в базе, обновление не требуется.")

    # **Заполняем пропущенные даты**
    fill_missing_dates()


def fill_missing_dates():
    """ Проверяет и заполняет пропущенные даты в ExchangeRate """
    all_dates = pd.date_range(start="2024-01-01", end=datetime.today())
    existing_dates = set(ExchangeRate.objects.values_list('date', flat=True))

    missing_dates = [d for d in all_dates if d.date() not in existing_dates]

    if missing_dates:
        last_known_rates = ExchangeRate.objects.order_by('-date').first()
        for missing_date in missing_dates:
            ExchangeRate.objects.create(
                date=missing_date,
                USD=last_known_rates.USD,
                CNY=last_known_rates.CNY,
                HUF=last_known_rates.HUF,
                PLN=last_known_rates.PLN,
                CZK=last_known_rates.CZK,
                GBP=last_known_rates.GBP
            )


def load_exchange_rates(currency_code):
    queryset = ExchangeRateNormalized.objects.filter(currency_code=currency_code).order_by('date')
    df = pd.DataFrame.from_records(
        queryset.values('date', 'rate_value'),
        index='date'
    )
    return df


