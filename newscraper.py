from bs4 import BeautifulSoup
import requests

def extract_table_data(html_content):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table element
    table = soup.find('table')

    # Initialize an empty array to store table data
    data = []

    # Extract rows from the table
    rows = table.find_all('tr')

    # Loop through rows, skipping the first row (header)
    for row in rows:
        # Extract cells from the row
        cells = row.find_all('td')
        # Extract text from each cell and strip whitespace
        row_data = [cell.get_text(strip=True) for cell in cells]
        # Append row data to the main data array
        data.append(row_data)

    return data

def query_noaa_atmospheric_profile(year, month, day, hour, longitude, latitude):
    # Base URL and endpoint for the form action
    base_url = 'https://psl.noaa.gov'
    endpoint = '/cgi-bin/profile/makeplot.pl'

    # Constructing the URL with all possible parameters
    url = f'{base_url}{endpoint}?maintype=1&var=air&level=100&datatype=reanalysis&lat1={latitude}&lon1={longitude}&yr1={year}&mon1={month}&day1={day}&hr1={hour}&yr2=&mon2=&day2=&hr2=&anom=0&low=&high=&cint=&lineson=0&aspectratio=1&lat2=&lon2=&submit=Create+Plot%2FGet+Data'

    # Send a GET request to fetch the data
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract table data
        table_data = extract_table_data(response.content)
        return table_data
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None

# Example usage
year = 2020
month = 3
day = 5
hour = 0
longitude = 10.0
latitude = 10.0

table_data = query_noaa_atmospheric_profile(year, month, day, hour, longitude, latitude)
if table_data:
    print("Table Data:")
    for row in table_data:
        print(row)
else:
    print("Failed to retrieve table data.")
