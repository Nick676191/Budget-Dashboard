# # testing that the selenium google driver works
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from dotenv import load_dotenv
# import os

# load_dotenv()

# username = os.getenv("USERNAME")
# password = os.getenv("PASSWORD")

# driver = webdriver.Chrome()

# driver.get("https://www.americanexpress.com/en-us/account/login")

# # logging into the form, making sure to wait until everything loads before proceeding
# WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='eliloUserID']"))).send_keys(username)
# # find password input box and put it in
# driver.find_element(By.XPATH, "//input[@name='eliloPassword']").send_keys(password)
# # click the log in button
# driver.find_element(By.ID, "loginSubmit").submit()

# # code to keep the page open until I close it
# input("Press ENTER to exit\\n")
# driver.quit()

""""Everything above is done in selenium, does not allow me to log into the website. So I will need something a little more lightweight. Let's try playwright"""
import requests
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
import os
from pprint import pprint
from playwright.sync_api import sync_playwright

# getting the username and password for the account
load_dotenv()

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

def main():
    # loading up the page using the URL for the page
    login_url = "https://www.americanexpress.com/en-us/account/login"

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", 
                                    headless=False,
                                    args=["--disable-blink-features=AutomationControlled"])
        # page = browser.new_page()
        context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        page.goto(login_url)

        # login to account
        page.wait_for_selector("#eliloUserID", timeout=10000)
        page.type("#eliloUserID", username, delay=125)
        page.type("#eliloPassword", password, delay=150)
        page.click("#loginSubmit")

        page.wait_for_selector("#hamburgerMenuOpener", timeout=15000)

        input("Press ENTER to quit\\n")
        page.close()

if __name__ == "__main__":
    main()