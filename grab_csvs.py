# testing that the selenium google driver works
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

load_dotenv()

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

driver = webdriver.Chrome()

driver.get("https://global.americanexpress.com/overview")

# logging into the form, making sure to wait until everything loads before proceeding
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='eliloUserID']"))).send_keys(username)
# find password input box and put it in
driver.find_element(By.XPATH, "//input[@name='eliloPassword']").send_keys(password)
# click the log in button
driver.find_element(By.ID, "loginSubmit").click()

# code to keep the page open until I close it
input("Press ENTER to exit\\n")
driver.quit()