# set geolocation in chrome with python

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Specify the path to chromedriver
chrome_driver_path = '/opt/homebrew/bin/chromedriver'
'''
หากคุณไม่พบ ChromeDriver คุณอาจจะต้องดาวน์โหลดและติดตั้งมันก่อน
คุณสามารถดาวน์โหลดได้จากเว็บไซต์อย่างเป็นทางการของ ChromeDriver: https://sites.google.com/a/chromium.org/chromedriver/downloads
'''

# Set up Chrome options
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.geolocation": 1  # 1:allow, 2:block
})

# Initialize the Chrome driver
driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)

# Define the geolocation parameters
#  Berlin, Germany
latitude = 52.520007
longitude = 13.404954
accuracy = 100

# Function to set geolocation using Chrome DevTools Protocol
def set_geolocation(driver, latitude, longitude, accuracy):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "accuracy": accuracy
    }
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)

# Set the geolocation
set_geolocation(driver, latitude, longitude, accuracy)

# Open web
driver.get('https://browserleaks.com/geo')

# Wait for the page to load
time.sleep(15)


# Close the browser
driver.quit()
