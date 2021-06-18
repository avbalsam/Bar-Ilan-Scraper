from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
import responsa_bot


driver = webdriver.Chrome()
repo_dir = "/Users/avbal/Desktop/Coding/Selenium Scripts/Bar_Ilan_1/"


# driver.set_window_size(2048, 768)

# Navigate to url
driver.get("http://www.responsa.co.il")

# click on search button
search = driver.find_element_by_link_text("Browse")
search.click()

# wait until sidebar iframe exists
WebDriverWait(driver, timeout=6).until(lambda d: d.find_element_by_id("sidebar"))

# Switch to sidebar panel
responsa_bot.switch_to(driver, "sidebar")

# wait until expand buttons exist
WebDriverWait(driver, timeout=20).until(lambda d: d.find_elements_by_class_name("bulletPlus"))

#responsa_bot.expand_search_menu(driver)

#responsa_bot.make_dirs(driver, repo_dir)

#input("Press enter when ready...")

#responsa_bot.login(driver)

'''with open("C:/Users/avbal/Desktop/Coding/Selenium Scripts/test.txt", "wb") as f:
    f.write(responsa_bot.copy_document(driver).encode())'''

#responsa_bot.make_files(driver, repo_dir)

# driver.quit()

"""element_id = input("Enter ID of element to find: ")
el = driver.find_element_by_id(element_id)
responsa_bot.ensure_dir(repo_dir + responsa_bot.get_expected_path(driver, el))"""

input("Get login ready...")
responsa_bot.login(driver)
input("Close everything...")

responsa_bot.make_repo(driver, repo_dir)

"""input("Navigate to login page from tree... ")
responsa_bot.get_into_account(driver)
responsa_bot.close_open_tabs(driver)
responsa_bot.make_repo(driver, repo_dir)"""
