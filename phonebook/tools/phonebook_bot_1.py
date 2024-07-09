import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
from dotenv import load_dotenv

load_dotenv()
# อ่านค่าตัวแปรจาก .env
user_name = os.getenv('USER_NAME')
password = os.getenv('EMAIL_PASS')

def read_html_table_by_id(driver, table_id):
    # Get the outer HTML of the table by its ID
    table_html = driver.find_element(By.ID, table_id).get_attribute("outerHTML")
    
    # Use BeautifulSoup to parse the HTML content of the table
    soup = BeautifulSoup(table_html, "html.parser")
    table_data = []

    # Extracting headers
    headers = [header.text for header in soup.find_all('th')]
    table_data.append(headers)
    
    # Extracting rows
    for row in soup.find_all('tr')[1:]:  # Skip the header row
        cols = row.find_all('td')
        row_data = [col.text.strip() for col in cols]
        table_data.append(row_data)
    
    return table_data

# Setup the WebDriver (make sure to adjust the path to your WebDriver)
service = Service('/opt/homebrew/bin/chromedriver')  # Adjust the path to your WebDriver
driver = webdriver.Chrome(service=service)

# Define the URL of the page
url = os.getenv('URL_PHONEBOOK')  # Replace with the actual URL

# Load the page
driver.get(url)
time.sleep(2)
user_box = driver.find_element(By.ID, 'p_lt_ctl02_LogonForm_Login1_UserName')
user_box.send_keys(user_name)
pass_box = driver.find_element(By.ID, 'p_lt_ctl02_LogonForm_Login1_Password')
pass_box.send_keys(password)
submit_button = driver.find_element(By.ID, 'btntest2')
submit_button.click()

# Input the search parameter and submit the form
search_param = '%'  # Replace with the desired search parameter
search_box = driver.find_element(By.ID, 'text_parameter')
search_box.send_keys(search_param)
submit_button = driver.find_element(By.ID, 'settxtParam')
submit_button.click()

# Wait for the results to load
time.sleep(15)  # Wait for at least 15 seconds to ensure the results have loaded

# Select value = 100 from the <select> element
select_element = Select(driver.find_element(By.NAME, 'TableQuerySTAFF_length'))
select_element.select_by_value('100')

# Wait for the table to reload after changing the number of entries displayed
time.sleep(5)

# Initialize a list to store the table data
all_table_data = []
headers = []

# Loop through all pages
while True:
    # Extract table data from the current page
    table_data = read_html_table_by_id(driver, 'TableQuerySTAFF')  # Adjust the table ID as necessary

    if not headers:
        headers = table_data[0]
    all_table_data.extend(table_data[1:])

    # Check for the "Next" button and navigate to the next page
    try:
        next_button = driver.find_element(By.CLASS_NAME, 'next')  # Adjust the selector for the "Next" button
        # Check if the "Next" button is disabled
        if "disabled" in next_button.get_attribute("class"):
            break
        next_button.click()
        time.sleep(0.1)  # Wait for the next page to load
    except:
        break  # No more pages

# Close the WebDriver
driver.quit()

# Create a DataFrame from the collected table data
df = pd.DataFrame(all_table_data, columns=headers)

# Display the DataFrame
print(df)
df.to_excel("./bot/phonebook_nt_20240619.xlsx", index=False)
