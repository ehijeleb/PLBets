from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
import time
import re

# Set up Selenium WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# URL of the page
url = 'https://www.whoscored.com/Regions/252/Tournaments/2/Seasons/9618/Stages/22076/RefereeStatistics/England-Premier-League-2023-2024'

# Load the page
driver.get(url)

# Wait for the table to load
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.ID, "referee-tournaments-table-body")))

# Open CSV file to write the scraped data
with open('scraped_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Write headers
    writer.writerow(['referee', 'fouls_pg', 'fouls/tackles', 'pen_pg', 'yel_pg', 'yel', 'red_pg', 'red'])

    page_count = 1  # Start the counter for pages

    while page_count <= 2:  # Since there are only 2 pages
        # Get the page source and pass it to BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find the table body by ID
        table_body = soup.find('tbody', id='referee-tournaments-table-body')
        table_rows = table_body.find_all('tr') if table_body else []

        # Loop through each row and extract data
        for row in table_rows:
            columns = row.find_all('td')
            if columns:
                # Extract the first column (which contains both rank and referee name) and remove the numeric rank
                raw_referee_name = columns[0].text.strip()
                referee_name = re.sub(r'^\d+\.\s*', '', raw_referee_name)  # Remove numbers and dots (e.g., "1. ")

                # Extract the rest of the data
                data = [referee_name] + [col.text.strip() for col in columns[1:]]  # Extract remaining columns
                writer.writerow(data)

        # After scraping the first page, go to the second page if the page count is 1
        if page_count == 1:
            try:
                next_button = driver.find_element(By.ID, 'next')
                
                if next_button and next_button.text.strip().lower() == 'next':
                    print("Next button found:", next_button.text)
                    driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Scroll to the button

                    # Wait for the "Next" button to be clickable
                    wait.until(EC.element_to_be_clickable((By.ID, 'next')))

                    # Use JavaScript to click the button instead of next_button.click()
                    driver.execute_script("arguments[0].click();", next_button)
                    print("Next button clicked!")

                    # Add a fixed delay to allow the page to load
                    time.sleep(3)  # Increase if needed

                    # Increment the page count to stop after the second page
                    page_count += 1
                else:
                    print("Next button not found or disabled. Exiting.")
                    break

            except Exception as e:
                print(f"Error navigating to next page: {e}")
                break  # Stop if the next button is not found or there's an issue
        else:
            # If we've already navigated to the second page, exit the loop
            print("All pages scraped successfully.")
            break

# Close the Selenium WebDriver
driver.quit()

print('Data scraping completed successfully!')
