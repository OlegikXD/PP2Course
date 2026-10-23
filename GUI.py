from translations import TRANSLATIONS

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                             QLineEdit, QLabel, QRadioButton, QDialog, QHBoxLayout, QScrollArea)
from Weather_API import get_weather, get_5days_weather
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from template_loader import TemplateLoader

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.temperature_unit = "Celsius"
        self.theme = "light"
        self.language = "ru"

        self.template_loader = TemplateLoader()

        self.check_style_files()

        self.city_label = QLabel(self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton()
        self.get_5days_weather_button = QPushButton()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)

        self.weather_display = QLabel()
        self.weather_display.setAlignment(Qt.AlignCenter)
        self.weather_display.setWordWrap(True)
        self.weather_display.setObjectName("weather_display")
        self.weather_display.setMinimumHeight(100)
        self.scroll_layout.addWidget(self.weather_display)

        self.scroll_area.setWidget(self.scroll_content)

        self.settings_button = QPushButton()

        self.initialize_ui()
        self.update_ui_texts()

    def tr(self, key):
        return TRANSLATIONS.get(self.language, TRANSLATIONS['ru']).get(key, key)

    def check_style_files(self):
        light_exists = os.path.exists("GUI.qss")
        dark_exists = os.path.exists("DARK_GUI.qss")

        if not light_exists:
            print("⚠️ Файл GUI.qss не найден!")
        if not dark_exists:
            print("⚠️ Файл DARK_GUI.qss не найден!")

        return light_exists, dark_exists

    def initialize_ui(self):
        self.setWindowTitle(self.tr('app_title'))
        try:
            self.setWindowIcon(QIcon("APP_ICO .ico"))
        except:
            pass

        vbox = QVBoxLayout()

        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(self.get_weather_button)
        hbox_buttons.addWidget(self.get_5days_weather_button)

        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addLayout(hbox_buttons)
        vbox.addWidget(self.scroll_area)
        vbox.addWidget(self.settings_button)

        self.setLayout(vbox)

        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.get_5days_weather_button.setObjectName("get_5days_weather_button")
        self.weather_display.setObjectName("weather_display")
        self.settings_button.setObjectName("settings_button")

        self.apply_theme()

        self.get_weather_button.clicked.connect(lambda: self.get_weather_info(False))
        self.get_5days_weather_button.clicked.connect(lambda: self.get_weather_info(True))
        self.settings_button.clicked.connect(self.open_settings)

    def update_ui_texts(self):
        self.setWindowTitle(self.tr('app_title'))
        self.city_label.setText(self.tr('enter_city'))
        self.get_weather_button.setText(self.tr('get_weather'))
        self.get_5days_weather_button.setText(self.tr('get_5days_weather'))
        self.settings_button.setText(self.tr('settings'))

        current_text = self.weather_display.text()
        if current_text and "Загрузка" not in current_text:
            if hasattr(self, 'last_weather_data'):
                if isinstance(self.last_weather_data, dict):
                    if "list" in self.last_weather_data:
                        self.display_5days_weather(self.last_weather_data)
                    else:
                        self.display_weather(self.last_weather_data)

    def get_theme_colors(self):
        if self.theme == "dark":
            return {
                "bg": "#1a1a2e",
                "text": "#e8e8f0",
                "text_secondary": "#8888aa",
                "text_muted": "#666688",
                "border": "rgba(255,255,255,0.05)",
                "card_bg": "rgba(255,255,255,0.03)",
                "card_hover": "rgba(255,255,255,0.06)",
                "shadow": "0 2px 20px rgba(0,0,0,0.4)",
                "accent": "#6c63ff",
                "accent_light": "rgba(108, 99, 255, 0.15)",
                "success": "#00b894",
                "gradient": "linear-gradient(135deg, #6c63ff, #00b894)"
            }
        else:
            return {
                "bg": "white",
                "text": "#1a1a2e",
                "text_secondary": "#888888",
                "text_muted": "#aaaaaa",
                "border": "rgba(0,0,0,0.06)",
                "card_bg": "rgba(0,0,0,0.02)",
                "card_hover": "rgba(0,0,0,0.04)",
                "shadow": "0 2px 20px rgba(0,0,0,0.06)",
                "accent": "#6c63ff",
                "accent_light": "rgba(108, 99, 255, 0.1)",
                "success": "#00b894",
                "gradient": "linear-gradient(135deg, #6c63ff, #00b894)"
            }

    def apply_theme(self):
        try:
            if self.theme == "dark":
                qss_file = "DARK_GUI.qss"
            else:
                qss_file = "GUI.qss"

            if os.path.exists(qss_file):
                with open(qss_file, "r", encoding="utf-8") as file:
                    style = file.read()
                    self.setStyleSheet(style)
                    print(f"✅ Тема '{self.theme}' загружена из {qss_file}")
            else:
                print(f"⚠️ Файл {qss_file} не найден, используются стандартные стили")
                self.setStyleSheet(self.get_fallback_styles())

        except Exception as e:
            print(f"❌ Ошибка загрузки стилей: {e}")
            self.setStyleSheet(self.get_fallback_styles())

        if hasattr(self, 'last_weather_data'):
            current_text = self.weather_display.text()
            if current_text and "Загрузка" not in current_text:
                if isinstance(self.last_weather_data, dict):
                    if "list" in self.last_weather_data:
                        self.display_5days_weather(self.last_weather_data)
                    else:
                        self.display_weather(self.last_weather_data)

    def get_fallback_styles(self):
        if self.theme == "dark":
            return """
                QWidget {
                    background-color: #0f0f1a;
                    color: #e8e8f0;
                }
                QLabel#city_label {
                    font-size: 22px;
                    font-weight: 600;
                    color: #e8e8f0;
                }
                QLineEdit#city_input {
                    font-size: 18px;
                    background: #1a1a2e;
                    color: #e8e8f0;
                    border: 2px solid #2a2a40;
                    border-radius: 12px;
                    padding: 12px 20px;
                }
                QPushButton#get_weather_button {
                    font-size: 16px;
                    font-weight: 600;
                    color: white;
                    background: #6c63ff;
                    border: none;
                    border-radius: 12px;
                    padding: 14px 20px;
                }
                QPushButton#get_weather_button:hover {
                    background: #7c73ff;
                }
                QPushButton#get_5days_weather_button {
                    font-size: 16px;
                    font-weight: 600;
                    color: white;
                    background: #00b894;
                    border: none;
                    border-radius: 12px;
                    padding: 14px 20px;
                }
                QPushButton#get_5days_weather_button:hover {
                    background: #00c9a0;
                }
                QLabel#weather_display {
                    background: #1a1a2e;
                    border-radius: 16px;
                    padding: 25px;
                    margin: 10px;
                    color: #e8e8f0;
                }
                QPushButton#settings_button {
                    font-size: 15px;
                    font-weight: 500;
                    background: #1a1a2e;
                    color: #e8e8f0;
                    border: 2px solid #2a2a40;
                    border-radius: 12px;
                    padding: 12px 20px;
                }
                QPushButton#settings_button:hover {
                    background: #22223a;
                    border-color: #7c73ff;
                    color: #7c73ff;
                }
            """
        else:
            return """
                QWidget {
                    background-color: #f0f2f5;
                    color: #1a1a2e;
                }
                QLabel#city_label {
                    font-size: 22px;
                    font-weight: 600;
                    color: #1a1a2e;
                }
                QLineEdit#city_input {
                    font-size: 18px;
                    background: white;
                    color: #1a1a2e;
                    border: 2px solid #e0e0e0;
                    border-radius: 12px;
                    padding: 12px 20px;
                }
                QPushButton#get_weather_button {
                    font-size: 16px;
                    font-weight: 600;
                    color: white;
                    background: #6c63ff;
                    border: none;
                    border-radius: 12px;
                    padding: 14px 20px;
                }
                QPushButton#get_weather_button:hover {
                    background: #7c73ff;
                }
                QPushButton#get_5days_weather_button {
                    font-size: 16px;
                    font-weight: 600;
                    color: white;
                    background: #00b894;
                    border: none;
                    border-radius: 12px;
                    padding: 14px 20px;
                }
                QPushButton#get_5days_weather_button:hover {
                    background: #00c9a0;
                }
                QLabel#weather_display {
                    background: white;
                    border-radius: 16px;
                    padding: 25px;
                    margin: 10px;
                    color: #1a1a2e;
                }
                QPushButton#settings_button {
                    font-size: 15px;
                    font-weight: 500;
                    background: white;
                    color: #1a1a2e;
                    border: 2px solid #e0e0e0;
                    border-radius: 12px;
                    padding: 12px 20px;
                }
                QPushButton#settings_button:hover {
                    background: #f8f9fa;
                    border-color: #6c63ff;
                    color: #6c63ff;
                }
            """

    def get_weather_info(self, is_5days):
        city = self.city_input.text().strip()
        if not city:
            self.display_error(self.tr('enter_city_error'))
            return

        self.weather_display.setStyleSheet("font-size: 45px;")
        self.weather_display.setText(self.tr('loading'))

        if is_5days:
            get_5days_weather(self, city)
        else:
            get_weather(self, city)

    def display_weather(self, data):
        try:
            colors = self.get_theme_colors()
            self.last_weather_data = data

            main_data = data.get("main", {})
            temperature_k = main_data.get("temp", 0)
            feels_like_k = main_data.get("feels_like", 0)
            humidity = main_data.get("humidity", 0)
            pressure = main_data.get("pressure", 0)

            wind_data = data.get("wind", {})
            wind_speed = wind_data.get("speed", 0)

            weather_list = data.get("weather", [])
            weather_data = weather_list[0] if weather_list else {}
            weather_id = weather_data.get("id", 800)
            weather_description = weather_data.get("description", self.tr('unknown'))

            if self.temperature_unit == "По Фаренгейту":
                temperature = temperature_k * 9 / 5 + 32
                feels_like = feels_like_k * 9 / 5 + 32
                unit = self.tr('fahrenheit_unit')
            else:
                temperature = temperature_k
                feels_like = feels_like_k
                unit = self.tr('celsius_unit')

            emoji = self.get_weather_emoji(weather_id)

            html = self.template_loader.render(
                "weather.html",
                text_color=colors['text'],
                text_secondary=colors['text_secondary'],
                accent_light=colors['accent_light'],
                card_bg=colors['card_bg'],
                border_color=colors['border'],
                emoji=emoji,
                temperature=f"{temperature:.0f}",
                feels_like=f"{feels_like:.0f}",
                unit=unit,
                feels_like_text=self.tr('feels_like'),
                description=weather_description.capitalize(),
                humidity_label=self.tr('humidity'),
                pressure_label=self.tr('pressure'),
                wind_label=self.tr('wind'),
                humidity=humidity,
                pressure=pressure,
                pressure_unit=self.tr('hpa'),
                wind_speed=f"{wind_speed:.1f}",
                wind_unit=self.tr('mps')
            )

            self.weather_display.setStyleSheet(f"""
                QLabel {{
                    background: {colors['bg']};
                    color: {colors['text']};
                    border-radius: 16px;
                    padding: 20px;
                    margin: 10px;
                    border: 1px solid {colors['border']};
                    box-shadow: {colors['shadow']};
                }}
            """)
            self.weather_display.setText(html)
            self.scroll_area.verticalScrollBar().setValue(0)

        except Exception as e:
            self.display_error(f"{self.tr('display_error')} {e}")
            print(f"Детали ошибки: {e}")

    def display_5days_weather(self, data):
        try:
            colors = self.get_theme_colors()
            self.last_weather_data = data

            forecasts = data.get("list", [])

            if not forecasts:
                self.display_error(self.tr('no_forecast_data'))
                return

            daily_forecasts = []
            seen_dates = set()

            for forecast in forecasts:
                date = forecast.get("dt_txt", "").split()[0]
                if date not in seen_dates and len(daily_forecasts) < 5:
                    seen_dates.add(date)
                    daily_forecasts.append(forecast)

            from datetime import datetime

            forecast_cards = ""
            for forecast in daily_forecasts:
                try:
                    date = forecast.get("dt_txt", "").split()[0]

                    main_data = forecast.get("main", {})
                    temp = main_data.get("temp", 0)
                    feels_like = main_data.get("feels_like", 0)
                    humidity = main_data.get("humidity", 0)

                    weather_list = forecast.get("weather", [])
                    weather_data = weather_list[0] if weather_list else {}
                    description = weather_data.get("description", self.tr('unknown'))
                    weather_id = weather_data.get("id", 800)

                    if self.temperature_unit == "По Фаренгейту":
                        temp = temp * 9 / 5 + 32
                        feels_like = feels_like * 9 / 5 + 32
                        unit = self.tr('fahrenheit_unit')
                    else:
                        unit = self.tr('celsius_unit')

                    emoji = self.get_weather_emoji(weather_id)
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    date_formatted = date_obj.strftime("%d.%m")
                    day_name = date_obj.strftime("%a")

                    days_short = self.tr('days_short')
                    day_name_ru = days_short.get(day_name, day_name)

                    if weather_id == 800:
                        border_color = "#ffd700"
                    elif 801 <= weather_id <= 804:
                        border_color = "#a0a0a0"
                    elif 500 <= weather_id <= 531:
                        border_color = "#0064ff"
                    elif 600 <= weather_id <= 622:
                        border_color = "#c8c8ff"
                    else:
                        border_color = colors['accent']

                    card_html = self.template_loader.render(
                        "forecast_card.html",
                        card_bg=colors['card_bg'],
                        border_color=border_color,
                        shadow=colors['shadow'],
                        text_color=colors['text'],
                        text_secondary=colors['text_secondary'],
                        day_name=day_name_ru,
                        date=date_formatted,
                        emoji=emoji,
                        temp=f"{temp:.0f}",
                        feels_like=f"{feels_like:.0f}",
                        unit=unit,
                        feels_like_text=self.tr('feels_like_short'),
                        humidity=humidity,
                        description=description.capitalize()
                    )
                    forecast_cards += card_html

                except Exception as e:
                    print(f"Ошибка обработки прогноза: {e}")
                    continue

            html = self.template_loader.render(
                "forecast_5days.html",
                text_color=colors['text'],
                gradient=colors['gradient'],
                forecast_title=self.tr('forecast_5days'),
                forecast_cards=forecast_cards
            )

            self.weather_display.setStyleSheet(f"""
                QLabel {{
                    background: {colors['bg']};
                    color: {colors['text']};
                    border-radius: 16px;
                    padding: 20px;
                    margin: 10px;
                    border: 1px solid {colors['border']};
                    box-shadow: {colors['shadow']};
                }}
            """)
            self.weather_display.setText(html)
            self.scroll_area.verticalScrollBar().setValue(0)

        except Exception as e:
            self.display_error(f"{self.tr('forecast_error')} {e}")
            print(f"Детали ошибки: {e}")

    def display_error(self, error_message):
        try:
            colors = self.get_theme_colors()
        except:
            colors = {
                "bg": "white",
                "text": "#1a1a2e",
                "text_secondary": "#888888"
            }

        html = self.template_loader.render(
            "error.html",
            text_color=colors['text'],
            text_secondary=colors['text_secondary'],
            error_title=self.tr('error_title'),
            error_message=error_message
        )

        self.weather_display.setStyleSheet(f"""
            QLabel {{
                background: {colors['bg']};
                color: {colors['text']};
                border-radius: 16px;
                padding: 20px;
                margin: 10px;
                border: 2px solid rgba(255, 107, 107, 0.2);
                box-shadow: 0 2px 20px rgba(255, 107, 107, 0.1);
            }}
        """)
        self.weather_display.setText(html)
        self.scroll_area.verticalScrollBar().setValue(0)

    def open_settings(self):
        dialog = SettingsDialog(self, self.temperature_unit, self.theme, self.language)
        if dialog.exec_() == QDialog.Accepted:
            new_unit = dialog.get_temperature_unit()
            new_theme = dialog.get_theme()
            new_language = dialog.get_language()

            if new_unit != self.temperature_unit:
                self.temperature_unit = new_unit

            if new_theme != self.theme:
                self.theme = new_theme
                self.apply_theme()

            if new_language != self.language:
                self.language = new_language
                self.update_ui_texts()

            city = self.city_input.text().strip()
            if city:
                print(f"🔄 Обновление погоды на языке: {self.language}")
                self.weather_display.setStyleSheet("font-size: 45px;")
                self.weather_display.setText(self.tr('loading'))
                get_weather(self, city)

    @staticmethod
    def get_weather_emoji(weather_id):
        if 200 <= weather_id <= 232:
            return "⛈️"
        elif 300 <= weather_id <= 321:
            return "🌦️"
        elif 500 <= weather_id <= 531:
            return "🌧️"
        elif 600 <= weather_id <= 622:
            return "🌨️"
        elif 701 <= weather_id <= 741:
            return "🌫️"
        elif weather_id == 762:
            return "🌋"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 781:
            return "🌪️"
        elif weather_id == 800:
            return "☀️"
        elif 801 <= weather_id <= 804:
            return "☁️"
        else:
            return ""


class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_unit="Celsius", current_theme="light", current_language="ru"):
        super().__init__(parent)
        self.parent = parent
        self.current_unit = current_unit
        self.current_theme = current_theme
        self.current_language = current_language

        self.setWindowTitle(self.tr('settings_title'))
        try:
            self.setWindowIcon(QIcon("settings.ico"))
        except:
            pass

        self.resize(350, 550)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.setup_layout()
        self.set_initial_values()

    def tr(self, key):
        if self.parent:
            return self.parent.tr(key)
        return TRANSLATIONS.get('ru', {}).get(key, key)

    def create_widgets(self):
        self.instructions = QLabel(self.tr('temperature_unit'), self)
        self.celsius_radio = QRadioButton(self.tr('celsius'))
        self.fahrenheit_radio = QRadioButton(self.tr('fahrenheit'))

        self.theme_label = QLabel(self.tr('theme'), self)
        self.light_theme_radio = QRadioButton(self.tr('light_theme'))
        self.dark_theme_radio = QRadioButton(self.tr('dark_theme'))

        self.language_label = QLabel(self.tr('language'), self)
        self.russian_radio = QRadioButton(self.tr('russian'))
        self.english_radio = QRadioButton(self.tr('english'))

        self.ok_button = QPushButton(self.tr('ok'))
        self.ok_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton(self.tr('cancel'))
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.clicked.connect(self.reject)

    def setup_layout(self):
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignTop)
        vbox.setSpacing(10)

        vbox.addWidget(self.instructions)
        vbox.addWidget(self.celsius_radio)
        vbox.addWidget(self.fahrenheit_radio)

        vbox.addSpacing(20)

        vbox.addWidget(self.theme_label)
        vbox.addWidget(self.light_theme_radio)
        vbox.addWidget(self.dark_theme_radio)

        vbox.addSpacing(20)

        vbox.addWidget(self.language_label)
        vbox.addWidget(self.russian_radio)
        vbox.addWidget(self.english_radio)

        vbox.addSpacing(20)

        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(self.ok_button)
        hbox_buttons.addWidget(self.cancel_button)
        vbox.addLayout(hbox_buttons)

        self.setLayout(vbox)

    def set_initial_values(self):
        if self.current_unit == "По Фаренгейту":
            self.fahrenheit_radio.setChecked(True)
        else:
            self.celsius_radio.setChecked(True)

        if self.current_theme == "dark":
            self.dark_theme_radio.setChecked(True)
        else:
            self.light_theme_radio.setChecked(True)

        if self.current_language == "en":
            self.english_radio.setChecked(True)
        else:
            self.russian_radio.setChecked(True)


    def get_temperature_unit(self):
        if self.celsius_radio.isChecked():
            return "По Цельсию"
        else:
            return "По Фаренгейту"

    def get_theme(self):
        if self.dark_theme_radio.isChecked():
            return "dark"
        else:
            return "light"

    def get_language(self):
        if self.english_radio.isChecked():
            return "en"
        else:
            return "ru"