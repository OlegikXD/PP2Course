import requests
import os
from dotenv import load_dotenv

load_dotenv("API_KEY.env")


def get_weather(app, city):
    api_key = os.getenv("API_KEY")
    if not api_key:
        app.display_error("API ключ не настроен")
        return

    lang = app.language if hasattr(app, 'language') else "ru"

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": lang
    }

    try:
        response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("cod") == 200 and "main" in data:
            app.display_weather(data)
        else:
            app.display_error("Не удалось получить данные о погоде")

    except requests.exceptions.HTTPError as e:
        handle_http_error(app, e, response, city)
    except requests.exceptions.ConnectionError:
        app.display_error("Ошибка соединения. Проверьте интернет")
    except requests.exceptions.Timeout:
        app.display_error("Превышено время ожидания ответа")
    except requests.exceptions.TooManyRedirects:
        app.display_error("Слишком много перенаправлений")
    except requests.exceptions.RequestException as e:
        app.display_error(f"Ошибка запроса: {e}")
    except ValueError as e:
        app.display_error(f"Ошибка обработки данных: {e}")


def get_5days_weather(app, city):
    api_key = os.getenv("API_KEY")
    if not api_key:
        app.display_error("API ключ не настроен")
        return

    lang = app.language if hasattr(app, 'language') else "ru"

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": lang,
        "cnt": 40
    }

    try:
        response = requests.get("https://api.openweathermap.org/data/2.5/forecast", params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("cod") == "200":
            app.display_5days_weather(data)
        else:
            app.display_error("Не удалось получить данные о погоде")

    except requests.exceptions.HTTPError as e:
        handle_http_error(app, e, response, city)
    except requests.exceptions.ConnectionError:
        app.display_error("Ошибка соединения. Проверьте интернет")
    except requests.exceptions.Timeout:
        app.display_error("Превышено время ожидания ответа")
    except requests.exceptions.TooManyRedirects:
        app.display_error("Слишком много перенаправлений")
    except requests.exceptions.RequestException as e:
        app.display_error(f"Ошибка запроса: {e}")
    except ValueError as e:
        app.display_error(f"Ошибка обработки данных: {e}")


def handle_http_error(app, error, response, city):
    status_code = response.status_code
    errors = {
        400: "Неверный запрос. Проверьте название города",
        401: "Неверный API ключ. Проверьте файл .env",
        403: "Доступ запрещен",
        404: f"Город '{city}' не найден",
        429: "Слишком много запросов. Подождите немного",
        500: "Ошибка на сервере. Попробуйте позже",
        502: "Ошибка шлюза",
        503: "Сервис недоступен",
        504: "Таймаут шлюза"
    }
    app.display_error(errors.get(status_code, f"HTTP ошибка: {error}"))