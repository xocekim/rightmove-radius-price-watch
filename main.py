import re
import sqlite3
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
)

# setup db
con = sqlite3.connect("rightmove.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

# setup selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1200")
# options.binary_location = """C:\Program Files\Google\Chrome Beta\Application\chrome.exe"""
driver = webdriver.Chrome(options=options)
# driver.set_window_position(-1000, 0)
driver.maximize_window()
driver.implicitly_wait(5)

# get root page
driver.get("https://www.rightmove.co.uk/property-for-sale.html")

# test for cookie banner
try:
    driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
except NoSuchElementException:
    pass

# set location and click search
driver.find_element(By.CSS_SELECTOR, "input#ta_searchInput").send_keys("Lytham")
driver.find_element(By.CSS_SELECTOR, "button.dsrm_button").click()

# set filters
driver.find_element(By.CSS_SELECTOR, '#radius option[value="1.0"]').click()

# set min/max price
driver.find_element(By.CSS_SELECTOR, 'select[name="minPrice"] option[value="175000"]').click()
driver.find_element(By.CSS_SELECTOR, 'select[name="maxPrice"] option[value="270000"]').click()

# include under offer and sold
driver.find_element(By.CSS_SELECTOR, 'label[for="includeSSTC"]').click()
driver.find_element(By.ID, "propertySearchCriteria").submit()

# sort by lowest price
try:
    driver.find_element(By.CSS_SELECTOR, 'select[id="sortType"] option[value="1"]').click()
except ElementNotInteractableException:
    pass

# iterate through pages
while True:
    # wait for results to load
    time.sleep(1)
    try:
        results = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div#l-searchResults > div > div.l-searchResult"))
        )
        last_page = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "button.pagination-direction--next"))
        )
    except TimeoutException:
        break

    # iterate through results
    for _ in results:
        p = {}
        prop_price_a = _.find_element(By.CSS_SELECTOR, "a.propertyCard-salePrice")
        p["price"] = re.search(r"([\d,]+)", prop_price_a.text)
        p["price"] = int(p["price"].group(1).replace(",", "")) if p["price"] else -1
        p["id"] = int(re.search(r"properties\/(\d+)", prop_price_a.get_attribute("href")).group(1))
        p["address"] = _.find_element(By.CSS_SELECTOR, "address").text
        p["type"] = _.find_element(By.CSS_SELECTOR, "div.property-information > span.text").text
        prop_agent = _.find_elements(By.CSS_SELECTOR, "div.propertyCard-branchLogo > a")
        p["agent"] = prop_agent[0].get_attribute("title") if prop_agent else "Private"
        # insert new property
        cur.execute(
            "INSERT INTO property (id, price, address, type, agent, last_seen) "
            "VALUES (:id, :price, :address, :type, :agent, CURRENT_TIMESTAMP) "
            "ON CONFLICT (id) DO UPDATE SET price=:price, address=:address, type=:type, "
            "agent=:agent, last_seen=CURRENT_TIMESTAMP",
            p,
        )

    # commit changes
    con.commit()

    # break if no more pages
    if last_page.get_attribute("disabled"):
        break
    last_page.click()


driver.quit()
