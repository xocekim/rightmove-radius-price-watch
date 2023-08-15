import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

options = webdriver.ChromeOptions()
options.add_argument("--disable-extensions")
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
    "AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/115.0.5790.170 Safari/537.36")
driver = webdriver.Chrome(options=options)
driver.set_window_position(-1000, 0)
driver.maximize_window()
driver.implicitly_wait(2)
driver.get("https://www.rightmove.co.uk/property-for-sale.html")

# test for cookie banner
try:
    driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
except NoSuchElementException:
    pass

# set location
driver.find_element(By.ID, "searchLocation").send_keys("Lytham")
driver.find_element(By.CSS_SELECTOR, 'ul#typeAheadResult > li').click()
driver.find_element(By.ID, 'initialSearch').submit()

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
page = 1
while page < 2:
    # wait for results to load
    try:
        results = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, 'div#l-searchResults > div > div.l-searchResult')))
    except TimeoutException:
        break

    # iterate through results
    for _ in results:
        prop_price_a = _.find_element(By.CSS_SELECTOR, 'a.propertyCard-salePrice')
        prop_price = int(re.search(r'([\d,]+)', prop_price_a.text).group(1).replace(',', ''))
        prop_id = int(re.search(r'properties\/(\d+)', prop_price_a.get_attribute('href')).group(1))
        prop_address = _.find_element(By.CSS_SELECTOR, 'address').text
        prop_type = _.find_element(By.CSS_SELECTOR, 'div.property-information > span.text').text
        prop_agent = _.find_elements(By.CSS_SELECTOR, 'div.propertyCard-branchLogo > a')
        prop_agent = prop_agent[0].get_attribute('title') if prop_agent else 'Private'
        print(prop_id, prop_price, prop_address, prop_type, prop_agent)

    # break if no more pages
    next_page = driver.find_elements(By.CSS_SELECTOR, 'button.pagination-direction--next:not(disabled)')
    if next_page:
        page += 1
        driver.find_element(By.CSS_SELECTOR, 'button.pagination-direction--next').click()
        continue


driver.quit()
