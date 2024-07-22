import requests
from bs4 import BeautifulSoup

def query_noaa_atmospheric_profile(year, month, day, hour, longitude, latitude):
    # Initial URL to get the form
    url = 'https://psl.noaa.gov/data/atmoswrit/profile/'

    # Send a GET request to fetch the form page
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the form (assuming there's only one form on the page)
    form = soup.find('form')

    # Check if the form exists
    if form is None:
        print("Form not found on the page.")
        return

    # Create a dictionary to store form data
    form_data = {}

    # Populate form data with the input fields, modifying the year and month input fields
    for input_tag in form.find_all('input'):
        name = input_tag.get('name')
        if name:
            if name == 'yr1':
                form_data[name] = year
            elif name == 'lon1':
                form_data[name] = longitude
            elif name == 'lat1':
                form_data[name] = latitude
            else:
                form_data[name] = input_tag.get('value', '')

    # Handle the month, day, and hour selectors
    for select_tag in form.find_all('select'):
        name = select_tag.get('name')
        if name:
            if name == 'mon1':
                form_data[name] = month
            elif name == 'day1':
                form_data[name] = day
            elif name == 'hr1':
                form_data[name] = hour
            else:
                selected_option = select_tag.find('option', selected=True)
                if selected_option:
                    form_data[name] = selected_option.get('value')
                else:
                    form_data[name] = select_tag.find('option').get('value')

    # Handle other form elements (e.g., textarea) if necessary
    for textarea_tag in form.find_all('textarea'):
        name = textarea_tag.get('name')
        if name:
            form_data[name] = textarea_tag.text

    # Get the form action (URL to which the form will be submitted)
    action = form.get('action')
    if not action.startswith('http'):
        action = url + action

    # Send a POST request to submit the form with the modified data
    response = requests.post(action, data=form_data)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response to extract the desired data
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract relevant data (adjust based on the actual HTML structure)
        # This is an example and may need adjustments based on the specific page structure
        profile_data = soup.find('div', {'id': 'profile_data'})
        
        if profile_data:
            print(profile_data.text.strip())
        else:
            print("Profile data not found.")
    else:
        print(f"Failed to submit the form. Status code: {response.status_code}")

# Example usage
year = 2020
month = 7
day = 15
hour = 12
longitude = -105.0
latitude = 40.0

query_noaa_atmospheric_profile(year, month, day, hour, longitude, latitude)
