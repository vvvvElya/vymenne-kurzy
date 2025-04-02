import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exchange_rates.settings")
import django
django.setup()

from rates.data_collection.data_loader import load_exchange_rates
from rates.models import ExchangeRateNormalized

def get_model_dir():
    return os.path.join(django.conf.settings.BASE_DIR, 'rates', 'forecasting', 'trained_models')

def prepare_data(df, look_back=30):
    if len(df) < look_back:
        raise ValueError("Недостаточно данных для подготовки выборки.")

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df[['rate_value']])
    X, y = [], []
    for i in range(look_back, len(scaled_data)):
        X.append(scaled_data[i - look_back:i, 0])
        y.append(scaled_data[i, 0])

    return np.array(X), np.array(y), scaler

def save_scaler(scaler, currency):
    scaler_path = os.path.join(get_model_dir(), f'scaler_{currency}.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)

def load_scaler(currency):
    scaler_path = os.path.join(get_model_dir(), f'scaler_{currency}.pkl')
    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Скейлер не найден для {currency} по пути {scaler_path}")
    with open(scaler_path, 'rb') as f:
        return pickle.load(f)

def train_lstm(currency_code, look_back=30):
    df = load_exchange_rates(currency_code)
    if df.empty:
        raise ValueError(f"Нет данных для валюты {currency_code}.")

    df = df.sort_values(by="date")
    X, y, scaler = prepare_data(df, look_back)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
        LSTM(50),
        Dense(25, activation='relu'),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X, y, epochs=50, batch_size=16, verbose=1)

    model_dir = get_model_dir()
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, f'lstm_{currency_code}.h5')
    model.save(model_path)
    save_scaler(scaler, currency_code)
    print(f"Модель и скейлер успешно сохранены для {currency_code}.")

    return model, scaler

def predict_future(currency, days, model_name="lstm", look_back=30):
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    from tensorflow.keras.layers import LSTM, Dense
    historical_data = ExchangeRateNormalized.objects.filter(
        currency__currency_code=currency
    ).order_by('date')
    df = pd.DataFrame(list(historical_data.values()))
    if df.empty:
        raise ValueError("Нет данных для предсказания.")

    df = df.sort_values(by="date")
    df["rate_value"] = df["rate_value"].astype(float)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")

    values = df["rate_value"].values.reshape(-1, 1)
    scaler = load_scaler(currency)
    scaled_data = scaler.transform(values)

    # Создание окон
    X, y = [], []
    for i in range(look_back, len(scaled_data)):
        X.append(scaled_data[i - look_back:i, 0])
        y.append(scaled_data[i, 0])
    X = np.array(X)
    y = np.array(y)

    # Разделение train/test
    train_size = int(len(X) * 0.8)
    X_train, y_train = X[:train_size], y[:train_size]
    X_test, y_test = X[train_size:], y[train_size:]

    # Ресейп
    X_train = X_train.reshape((-1, look_back, 1))
    X_test = X_test.reshape((-1, look_back, 1))

    model_path = os.path.join(get_model_dir(), f'lstm_{currency}.h5')
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Модель не найдена по пути {model_path}")
    model = load_model(model_path)

    # Предсказание на тестовой выборке
    y_pred_scaled = model.predict(X_test, verbose=0).flatten()
    y_pred = scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
    y_true = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()

    # Даты для тестового прогноза
    test_start = df.index[look_back + train_size]
    test_dates = df.index[look_back + train_size : look_back + train_size + len(y_test)]

    # Метрики
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    # Прогноз на будущее
    last_window = scaled_data[-look_back:].reshape(1, look_back, 1)
    future_preds_scaled = []
    for _ in range(days):
        pred_scaled = model.predict(last_window, verbose=0)[0, 0]
        future_preds_scaled.append(pred_scaled)
        last_window = np.append(last_window[:, 1:, :], [[[pred_scaled]]], axis=1)

    future_preds = scaler.inverse_transform(np.array(future_preds_scaled).reshape(-1, 1)).flatten()
    last_date = df.index[-1]
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days)

    forecast_df = pd.DataFrame({
        "date": future_dates,
        "forecast": future_preds
    }).set_index("date")

    return {
        "test_result": {
            "dates": test_dates.strftime("%Y-%m-%d").tolist(),
            "y_pred": y_pred.tolist(),
            "y_true": y_true.tolist(),
            "metrics": {
                "MSE": round(mse, 4),
                "RMSE": round(rmse, 4),
                "MAE": round(mae, 4),
                "R2": round(r2, 4),
            }
        },
        "future": forecast_df["forecast"]
    }
