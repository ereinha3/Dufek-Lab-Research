import requests
from bs4 import BeautifulSoup
import re
def retrieve_table(year = 2024, month = 7, day = 16, hour = 6, latitude = 45, longitude = -125):
    url = "https://psl.noaa.gov/cgi-bin/profile/makeplot.pl"
    params = {
        "maintype": 1,
        "var": "air",
        "level": 100,
        "datatype": "reanalysis",
        "lat1": latitude,
        "lon1": longitude,
        "yr1": year,
        "mon1": month,
        "day1": day,
        "hr1": hour,
        "yr2": "",
        "mon2": 1,
        "day2": 1,
        "hr2": 0,
        "anom": 0,
        "low": "",
        "high": "",
        "cint": "",
        "lineson": 0,
        "aspectratio": 1,
        "lat2": "",
        "lon2": "",
        "submit": "Create+Plot%2FGet+Data"
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = str(soup.find('table'))
            # print(table)
            # Remove HTML tags and extract the data
            rows = re.findall(r'<tr>(.*?)</tr>', table)
            header = re.findall(r'<td>(.*?)</td>', rows[0])
            data = []

            for row in rows[1:]:
                cols = re.findall(r'<td align="right">(.*?)</td>', row)
                data.append([float(col.strip()) for col in cols])

            # Print the header and data array
            print(f"Scraped Data at ({latitude}, {longitude}) on {month}/{day}/{year} at {hour} UTC")
            print("Header:", header)
            print("Data array:")
            for row in data:
                print(row)
            return data
        else:
            return None
    except requests.RequestException:
        print("Error: Unable to retrieve data from the NOAA website.")
        return None
