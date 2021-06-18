from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
import responsa_bot

driver = webdriver.Chrome()
repo_dir = "/Users/Avi/Desktop/Bar_Ilan/"

# Navigate to url
driver.get("http://www.responsa.co.il")

# click on browse button
driver.find_element_by_link_text("Browse").click()

# wait until sidebar iframe exists
WebDriverWait(driver, timeout=6).until(lambda d: d.find_element_by_id("sidebar"))

# Switch to sidebar panel
responsa_bot.switch_to(driver, "sidebar")

# wait until file tree is navigable
WebDriverWait(driver, timeout=20).until(lambda d: d.find_elements_by_class_name("bulletPlus"))

input("Navigate to login page from tree... ")
responsa_bot.get_into_account(driver)
responsa_bot.close_open_tabs(driver)
responsa_bot.make_repo(driver, repo_dir)
