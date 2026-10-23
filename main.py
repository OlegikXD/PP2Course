import sys
from PyQt5.QtWidgets import QApplication
from GUI import WeatherApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())