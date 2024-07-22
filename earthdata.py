from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

logging.basicConfig(level=logging.INFO)  # Set logging level to INFO

def decimal_to_dms(deg):
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return d, m, sd

# Function to click the button using Selenium WebDriver
def clickAddCoordinate(username, password, latitude, longitude):
    lat_deg, lat_min, lat_sec = decimal_to_dms(latitude)
    lon_deg, lon_min, lon_sec = decimal_to_dms(longitude)

    # Set up Selenium WebDriver
    driver = webdriver.Chrome()  # You can use other browsers like Firefox, Edge, etc.
    try:
        driver.get('https://ers.cr.usgs.gov/login/')
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        username_field.send_keys(username)
        
        password_field = driver.find_element_by_name('password')
        password_field.send_keys(password)
        
        # Click the login button
        login_button = driver.find_element_by_id('loginButton')
        login_button.click()

        driver.get('https://earthexplorer.usgs.gov/')
        WebDriverWait(driver, 10).until(EC.url_contains('earthexplorer.usgs.gov'))

        # Now on EarthExplorer page, find and click the Add Coordinate button
        add_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'coordEntryAdd'))
        )
        add_button.click()
        logging.info("Clicked Add Coordinate button successfully.")

        # Wait for the dialog to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-labelledby='ui-id-7']"))
        )

        # Fill out latitude fields
        driver.find_element_by_id('degreesLat').send_keys(str(lat_deg))
        driver.find_element_by_id('minutesLat').send_keys(str(lat_min))
        driver.find_element_by_id('secondsLat').send_keys(f"{lat_sec:.6f}")
        driver.find_element_by_class_name('directionLat').send_keys('N' if latitude >= 0 else 'S')

        # Fill out longitude fields
        driver.find_element_by_id('degreesLng').send_keys(str(lon_deg))
        driver.find_element_by_id('minutesLng').send_keys(str(lon_min))
        driver.find_element_by_id('secondsLng').send_keys(f"{lon_sec:.6f}")
        driver.find_element_by_class_name('directionLng').send_keys('E' if longitude >= 0 else 'W')

        # Click the Add button in the dialog
        add_button_dialog = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@class='ui-button ui-corner-all ui-widget' and text()='Add']"))
        )
        add_button_dialog.click()
        logging.info("Clicked 'Add' button in the dialog.")

        # Select the dataset checkbox
        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'coll_5e83a3ee1af480c5'))
        )
        checkbox.click()
        logging.info("Selected dataset checkbox.")

        # Click the Results button
        results_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input.button.tabButton.unselectable[data-tab='4']"))
        )
        results_button.click()
        logging.info("Clicked 'Results' button.")

        # Wait for the Download button to appear and click it
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='download']"))
        )
        download_button.click()
        logging.info("Clicked 'Download Options' button.")

    except Exception as e:
        logging.error(f"Failed: {e}")

    finally:
        # Close the browser session
        time.sleep(5)  # Wait a few seconds before closing (optional)
        driver.quit()
        logging.info("Browser session closed.")

# Example usage
username = 'ereinha3'
password = 'Allhart0857!'
latitude = 42.5  # Example decimal latitude
longitude = -100.75  # Example decimal longitude

clickAddCoordinate(username, password, latitude, longitude)
