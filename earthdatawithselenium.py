from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to click the button using Selenium WebDriver
def clickAddCoordinate(username, password):
    # Set up Selenium WebDriver
    driver = webdriver.Chrome()  # You can use other browsers like Firefox, Edge, etc.
    driver.get('https://earthexplorer.usgs.gov/')

    # Log in if not already logged in
    if 'earthexplorer.usgs.gov' not in driver.current_url:
        login_url = 'https://ers.cr.usgs.gov/login/'
        driver.get(login_url)
        driver.find_element_by_id('username').send_keys(username)
        driver.find_element_by_id('password').send_keys(password)
        driver.find_element_by_id('loginButton').click()

        # Wait for login to complete
        WebDriverWait(driver, 10).until(EC.url_contains('earthexplorer.usgs.gov'))

    # Now on EarthExplorer page, find and click the Add Coordinate button
    try:
        add_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'coordEntryAdd'))
        )
        add_button.click()
        print("Clicked Add Coordinate button successfully.")
    except Exception as e:
        print(f"Failed to click Add Coordinate button: {e}")

    # Close the browser session
    driver.quit()

# Example usage
username = 'your_username'
password = 'your_password'
clickAddCoordinate(username, password)
