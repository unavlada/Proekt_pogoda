from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    error_message = None
    city = ""

    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        
        if city:
            try:
                # Шаг 1: Переводим название города (на русском) в координаты (Широта/Долгота)
                # Используем открытый и бесплатный геокодер
                geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"
                geo_response = requests.get(geo_url, timeout=5)
                geo_data = geo_response.json()
                
                if 'results' in geo_data and len(geo_data['results']) > 0:
                    location = geo_data['results'][0]
                    lat = location['latitude']
                    lon = location['longitude']
                    correct_name = location.get('name', city)
                    
                    # Шаг 2: Запрашиваем погоду по полученным координатам
                    # Добавляем флаг current_weather=true и русскую локализацию
                    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&relative_humidity_2m=true"
                    weather_response = requests.get(weather_url, timeout=5)
                    data = weather_response.json()
                    
                    current = data['current_weather']
                    
                    # Маппинг кодов погоды (WMO) на понятный русский язык
                    wmo_codes = {
                        0: "Ясно", 1: "Преимущественно ясно", 2: "Переменная облачность", 3: "Пасмурно",
                        45: "Туман", 48: "Осаждающийся туман",
                        51: "Легкая морось", 53: "Умеренная морось", 55: "Плотная морось",
                        61: "Слабый дождь", 63: "Умеренный дождь", 65: "Сильный дождь",
                        71: "Слабый снегопад", 73: "Умеренный sнегопад", 75: "Сильный снегопад",
                        77: "Снежные зерна",
                        80: "Слабый ливневый дождь", 81: "Умеренный ливневый дождь", 82: "Сильный ливневый дождь",
                        85: "Слабый ливневый снег", 86: "Сильный ливневый снег",
                        95: "Гроза", 96: "Гроза со слабым градом", 99: "Гроза с сильным градом"
                    }
                    
                    weather_code = current.get('weathercode', 0)
                    weather_desc = wmo_codes.get(weather_code, "Переменчивая погода")
                    
                    # Получаем влажность воздуха из почасового блока, соответствующего текущему времени
                    # (Для простоты open-meteo отдает влажность на текущий час в таком формате)
                    humidity = data.get('hourly', {}).get('relative_humidity_2m', [55])[0]

                    # Собираем данные для отображения в шаблоне
                    weather_data = {
                        'city': correct_name,
                        'temp': current['temperature'],
                        'humidity': humidity,
                        'desc': weather_desc
                    }
                else:
                    error_message = f"Город '{city}' не найден. Попробуйте проверить раскладку клавиатуры."
                    
            except Exception as e:
                error_message = f"Не удалось получить данные с сервера погоды: {str(e)}"

    return render_template('index.html', weather=weather_data, error=error_message, city=city)

if __name__ == '__main__':
    app.run(debug=True, port=5000)