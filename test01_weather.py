import requests

# url = 'api.openweathermap.org/data/2.5/forecast/daily?lat=23.1167&lon=113.25&cnt=10&appid=32ef9e7529d18b0e020660d069fa0bcb'
# url = 'http://api.openweathermap.org/data/2.5/forecast/daily?q=London&cnt=3&appid=32ef9e7529d18b0e020660d069fa0bcb'
# url = 'https://api.openweathermap.org/data/3.0/onecall?lat=23.116&lon=113.25&exclude=current&appid=32ef9e7529d18b0e020660d069fa0bcb'
url = 'https://api.openweathermap.org/data/2.5/weather?lat=23.116&lon=113.25&units=metric&lang=zh_cn&appid=32ef9e7529d18b0e020660d069fa0bcb'
r = requests.get(url).json()
Guangzhou_weather = {}

if r['cod'] == 200:
    Guangzhou_weather = {
        'city': 'Guangzhou',
        'temperature': float("{0:.2f}".format(r['main']['temp'])),
        'description': r['weather'][0]['description'],
        'icon': r['weather'][0]['icon'],
        'country': "China"
        }
print(Guangzhou_weather)
print(r)
print(r['weather'][0]['icon'])
print(float("{0:.2f}".format(r['main']['temp'])))