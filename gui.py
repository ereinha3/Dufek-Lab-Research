import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
import requests
from bs4 import BeautifulSoup

# Define the temporal coverage
start_date = datetime(1948, 1, 1)
end_date = datetime(2024, 7, 6)

# Function to check if a year is a leap year
def is_leap_year(year):
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False

# Function to validate the input date
def validate_date(year, month, day):
    try:
        year = int(year)
        month = int(month)
        day = int(day)
        
        # Check if month is within the valid range
        if not (1 <= month <= 12):
            return False
        
        # Check if the day is valid for the given month and year (considering leap year)
        if month in [4, 6, 9, 11]:  # Months with 30 days
            if day <= 30:
                return True
        elif month in [1, 3, 5, 7, 8, 10, 12]:  # Months with 31 days
            if day <= 31:
                return True
        elif month == 2:  # February (handling leap year)
            if is_leap_year(year):
                if day <= 29:
                    return True
            else:
                if day <= 28:
                    return True
        
        return False
    except ValueError:
        return False

# Function to retrieve table data
def retrieve_table(year, month, day, hour, latitude, longitude):
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
            table = soup.find('table')
            print(table)
            return table
        else:
            return None
    except requests.RequestException:
        return None

# Function to handle form submission
def submit_form():
    year = year_var.get()
    month = month_var.get()
    day = day_var.get()
    hour = hour_var.get()
    latitude = lat_entry.get()
    longitude = lon_entry.get()
    
    if not year or not month or not day or not hour or not latitude or not longitude:
        error_label.config(text="Please fill all the fields.")
    elif not validate_date(year, month, day):
        error_label.config(text="Invalid date. Please enter a date between Jan 1, 1948 and Jul 6, 2024.")
    elif not (int(hour) % 6 == 0):
        error_label.config(text="Invalid hour. Please enter 0, 6, 12, or 18.")
    elif not (int(latitude) > -90 and int(latitude) < 90):
        error_label.config(text="Please enter a valid latitude. (Range: -90 to 90)")
    elif not (int(longitude) > -180 and int(longitude) < 180):
        error_label.config(text="Please enter a valid longitude. (Range: -180 to 180)")
    else:
        error_label.config(text="")
        loading_label.config(text="Loading...")
        # Run data retrieval in a separate thread
        thread = threading.Thread(target=retrieve_and_display_table, args=(year, month, day, hour, latitude, longitude))
        thread.start()

# Function to retrieve and display table in GUI
def retrieve_and_display_table(year, month, day, hour, latitude, longitude):
    table = retrieve_table(year, month, day, hour, latitude, longitude)
    
    if table:
        display_table_in_gui(table)
    else:
        loading_label.config(text="")
        error_label.config(text="Error retrieving data.")

# Function to display table in GUI
def display_table_in_gui(table):
    # Clear previous table display
    if table_frame.winfo_children():
        for child in table_frame.winfo_children():
            child.destroy()
    
    # Create a new frame for the table
    table_container = ttk.Frame(table_frame)
    table_container.pack(fill="both", expand=True)
    
    # Parse table rows and columns
    rows = table.find_all('tr')
    data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [col.text.strip() for col in cols]
        data.append(cols)
    
    # Display table in GUI
    for i, row in enumerate(data):
        for j, col in enumerate(row):
            label = ttk.Label(table_container, text=col, borderwidth=1, relief="solid")
            label.grid(row=i, column=j, sticky="nsew", padx=1, pady=1)
    
    loading_label.config(text="")

# Function to update the available days in the day combobox
def update_days(*args):
    try:
        year = int(year_var.get())
        month = int(month_var.get())
        
        if year and month:
            days = [str(i) for i in range(1, 32)]
            
            if month in [4, 6, 9, 11]:  # Months with 30 days
                days = [str(i) for i in range(1, 31)]
            elif month == 2:  # February
                if is_leap_year(year):
                    days = [str(i) for i in range(1, 30)]
                else:
                    days = [str(i) for i in range(1, 29)]
            
            day_var.set('')
            day_combobox['values'] = days
    except ValueError:
        pass

# Create the main window
root = tk.Tk()
root.title("Data Input GUI")

# Create input fields
input_frame = ttk.Frame(root)

year_label = ttk.Label(input_frame, text="Year:")
year_var = tk.StringVar()
year_var.trace("w", update_days)
year_combobox = ttk.Combobox(input_frame, textvariable=year_var, values=[str(i) for i in range(1948, 2025)], state='readonly')

month_label = ttk.Label(input_frame, text="Month:")
month_var = tk.StringVar()
month_var.trace("w", update_days)
month_combobox = ttk.Combobox(input_frame, textvariable=month_var, values=[str(i) for i in range(1, 13)], state='readonly')

day_label = ttk.Label(input_frame, text="Day:")
day_var = tk.StringVar()
day_combobox = ttk.Combobox(input_frame, textvariable=day_var, state='readonly')

hour_label = ttk.Label(input_frame, text="Hour (UTC):")
hour_var = tk.StringVar()
hour_combobox = ttk.Combobox(input_frame, textvariable=hour_var, values=["0", "6", "12", "18"], state='readonly')

lat_label = ttk.Label(input_frame, text="Latitude:")
lat_entry = ttk.Entry(input_frame, width=10)

lon_label = ttk.Label(input_frame, text="Longitude:")
lon_entry = ttk.Entry(input_frame, width=10)

submit_button = ttk.Button(input_frame, text="Submit", command=submit_form)
error_label = ttk.Label(input_frame, text="", foreground="red")

# Loading label
loading_label = ttk.Label(input_frame, text="", foreground="blue")

# Table display frame
table_frame = ttk.Frame(root)
table_frame.pack(padx=10, pady=10, fill="both", expand=True)

# Arrange widgets using grid layout
input_frame.pack(padx=10, pady=10)
year_label.grid(row=0, column=0, padx=5, pady=5)
year_combobox.grid(row=0, column=1, padx=5, pady=5)

month_label.grid(row=1, column=0, padx=5, pady=5)
month_combobox.grid(row=1, column=1, padx=5, pady=5)

day_label.grid(row=2, column=0, padx=5, pady=5)
day_combobox.grid(row=2, column=1, padx=5, pady=5)

hour_label.grid(row=3, column=0, padx=5, pady=5)
hour_combobox.grid(row=3, column=1, padx=5, pady=5)

lat_label.grid(row=4, column=0, padx=5, pady=5)
lat_entry.grid(row=4, column=1, padx=5, pady=5)

lon_label.grid(row=5, column=0, padx=5, pady=5)
lon_entry.grid(row=5, column=1, padx=5, pady=5)

submit_button.grid(row=6, column=0, columnspan=2, pady=10)
error_label.grid(row=7, column=0, columnspan=2)
loading_label.grid(row=8, column=0, columnspan=2)

# Start the GUI main loop
root.mainloop()
