import requests

# Define your User-Agent
headers = {
    'User-Agent': '(myweatherapp.com, contact@myweatherapp.com)'
}

# Example coordinates (latitude, longitude)
latitude = 38.8951  # Washington, DC
longitude = -77.0364

# Fetch the points data to get the office and gridX, gridY for the coordinates
points_url = f'https://api.weather.gov/points/{latitude},{longitude}'

# Send a request to get the points data
response = requests.get(points_url, headers=headers)
if response.status_code == 200:
    points_data = response.json()
else:
    print(f'Error fetching points data: {response.status_code}')
    points_data = {}

# Extract office and gridX, gridY from the points data
office = points_data['properties']['gridId']
gridX = points_data['properties']['gridX']
gridY = points_data['properties']['gridY']

print(f'Office: {office}, GridX: {gridX}, GridY: {gridY}')

# Construct the URL for the forecast endpoint
forecast_url = f'https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}/forecast'

# Send a request to get the forecast data
response = requests.get(forecast_url, headers=headers)
if response.status_code == 200:
    forecast_data = response.json()
else:
    print(f'Error fetching forecast data: {response.status_code}')
    forecast_data = {}

# Print the forecast data
print(forecast_data)
