from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
import os
from selenium.common import exceptions
import time
from selenium.webdriver.support import expected_conditions as EC


# removes the last occurrence of el from arr
def remove_last(arr, el):
    if type(arr) == "list":
        arr = arr.reverse()
        arr.remove(el)
        arr = arr.reverse()
    else:
        arr = arr[::-1]
        arr.replace(el, "", 1)
        arr = arr[::-1]
    return arr


#creates needed directories for given file and fixes any problems with filename
def ensure_dir(file_path):
    directory = os.path.dirname(file_path.replace("\"", "'").replace(":", "-") + "/")
    if not os.path.exists(directory):
        os.makedirs(directory)
    print(directory)
    return directory


# presses the "close tabs" button
def close_open_tabs(driver):
    driver.switch_to.default_content()
    switch_to(driver, "titles")
    driver.find_element_by_css_selector("img[title='Close all open tabs']").click()
    print("closed tabs")


# Non-recursive method to create full file tree
def make_dirs(driver, location):
    html = driver.execute_script("return document.documentElement.outerHTML;")
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("li", level="1"):
        levels = [a["name"], "", "", "", "", "", "", "", "", ""]
        for b in a.findChildren("li", level="2"):
            levels[1] = b["name"]
            extension = str()
            for level in levels:
                extension += level.replace("/", ";")
                extension += "/"
            ensure_dir(location + extension)
            for c in b.findChildren("li", level="3"):
                levels[2] = c["name"]
                extension = str()
                for level in levels:
                    extension += level.replace("/", ";")
                    extension += "/"
                ensure_dir(location + extension)
                for d in c.findChildren("li", level="4"):
                    levels[3] = d["name"]
                    extension = str()
                    for level in levels:
                        extension += level.replace("/", ";")
                        extension += "/"
                    ensure_dir(location + extension)
                    for e in d.findChildren("li", level="5"):
                        levels[4] = e["name"]
                        extension = str()
                        for level in levels:
                            extension += level.replace("/", ";")
                            extension += "/"
                        ensure_dir(location + extension)
                        for f in e.findChildren("li", level="6"):
                            levels[5] = f["name"]
                            extension = str()
                            for level in levels:
                                extension += level.replace("/", ";")
                                extension += "/"
                            ensure_dir(location + extension)
                            for g in f.findChildren("li", level="7"):
                                levels[6] = g["name"]
                                extension = str()
                                for level in levels:
                                    extension += level.replace("/", ";")
                                    extension += "/"
                                ensure_dir(location + extension)
                            levels[6] = ""
                        levels[5] = ""
                    levels[4] = ""
                levels[3] = ""
            levels[2] = ""
        levels[1] = ""


# part of make_dirs_rec()
# TODO make recursive directory tree maker work
def parse_tree(location, element, levels):
    children = element.findChildren("li")
    if len(element.findChildren("li")) == 0:
        return
    levels.append("/")
    for child in children:
        name = child["name"]
        name = name.replace('"', "'")
        levels.append(name)
        extension = str()
        for level in levels:
            extension += level.replace("/", ";")
        ensure_dir(location + extension)
        parse_tree(location, child, levels)
        levels = remove_last(levels, name)


# Adds all visible directories to file tree
# TODO make this method work
def make_dirs_rec(driver, location):
    html = driver.execute_script("return document.documentElement.outerHTML;")
    soup = BeautifulSoup(html, "html.parser")
    top_level = soup.find_all("li", type="collection", level="1")
    for item in top_level:
        levels = [item["name"]]
        parse_tree(location, item, levels)


# switches to specified frame object
def switch_to(driver, frame_id):
    iframe = driver.find_element_by_id(frame_id)
    try:
        driver.switch_to.frame(iframe)
    except exceptions.NoSuchFrameException:
        pass


# clicks on all + buttons to fully expand the search menu
# used for creating directory tree
def expand_search_menu(driver):
    clicked = list()
    num_clicked = 0
    count = 0
    while True:
        sidebar_titles = driver.find_elements_by_class_name("bulletPlus")
        print("Number of buttons left: " + str(len(sidebar_titles)))
        if len(sidebar_titles) == 0 or count == 50:
            break
        for title in sidebar_titles:
            try:
                title.click()
            except (exceptions.ElementNotInteractableException, exceptions.ElementClickInterceptedException,
                    exceptions.ElementNotVisibleException, exceptions.WebDriverException):
                break
            clicked.append(title)
            num_clicked += 1
            # print(title)
            if num_clicked % 100 == 0:
                print("Number of buttons clicked: " + str(num_clicked))


# clicks on all + buttons to fully expand the browse menu
# used for adding files to tree
# TODO Expand every li with type "collection"
def expand_browse_menu(driver):
    clicked = list()
    num_clicked = 0
    count = 0
    while True:
        sidebar_titles = driver.find_elements_by_css_selector("li[type=collection]")
        print("Number of buttons left: " + str(len(sidebar_titles)))
        if len(sidebar_titles) == 0 or count == 50:
            break
        for title in sidebar_titles:
            try:
                title.click()
            except (exceptions.ElementNotInteractableException, exceptions.ElementClickInterceptedException,
                    exceptions.ElementNotVisibleException, exceptions.WebDriverException):
                break
            clicked.append(title)
            num_clicked += 1
            if num_clicked % 100 == 0:
                print("Number of buttons clicked: " + str(num_clicked))


# clicks on a few plus buttons to partly expand menu
# useful for testing purposes
def expand_menu_test(driver):
    for x in range(0, 2):
        clicked = list()
        num_clicked = 0
        sidebar_titles = driver.find_elements_by_class_name("bulletPlus")
        print("Number of buttons left: " + str(len(sidebar_titles)))
        for title in sidebar_titles:
            try:
                title.click()
            except (exceptions.ElementNotInteractableException, exceptions.ElementClickInterceptedException,
                    exceptions.ElementNotVisibleException, exceptions.WebDriverException):
                pass
            clicked.append(title)
            num_clicked += 1
            if num_clicked % 100 == 0:
                print("Number of buttons clicked: " + str(num_clicked))
            if num_clicked >= 100:
                return


# returns expected PATH (not including repo_dir) of selenium WebElement
# make sure to pass an object with unique ID (in this case an <li>)
def get_expected_path(driver, element):
    driver.switch_to.default_content()
    switch_to(driver, "sidebar")
    element_id = element.get_attribute("id")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    soup_element = soup.find("li", id=element_id)
    path_arr = []
    for parent in soup_element.parents:
        name = None
        try:
            name = parent["name"]
            path_arr.append(name).replace("/", ";")
        except (KeyError, AttributeError):
            pass
    path_arr.reverse()
    path = ""
    for el in path_arr:
        if el is not None:
            path += el + "/"
    return path


# TODO fix repeating character occurrences
# TODO format titles better
# if there is a document in the browse panel, this method switches to the document panel and copies it
def copy_document(driver, document_number):
    print("Copying document number: " + str(document_number))
    driver.switch_to.default_content()
    WebDriverWait(driver, timeout=20).until(lambda d: d.find_element_by_id("titles"))
    switch_to(driver, "titles")
    for i in range(0, 3):
        for x in range(2, document_number + 10):
            try:
                switch_to(driver, "iFrame" + str(x))
                break
            except exceptions.NoSuchElementException:
                pass
        time.sleep(1)
    try:
        WebDriverWait(driver, timeout=20).until(lambda d: d.find_element_by_id("docFrame"))
        switch_to(driver, "docFrame")
        WebDriverWait(driver, timeout=20).until(lambda d: d.find_element_by_id("docBody"))
    except exceptions.TimeoutException:
        return None
    header = driver.find_element_by_id("header")
    body_el = driver.find_element_by_class_name("docBody")
    body = body_el.get_attribute("innerHTML")
    soup = BeautifulSoup(body, "html.parser")
    body = soup.find_all("span")
    body_arr = list()
    body_text = ""
    for item in body:
        if item.text != "":
            body_arr.append(item.text)
    for x in body_arr:
        body_text += x + " "
    for x in body_arr:
        body_text = body_text.replace(x+" "+x+" "+x+" ", "\n"+x+" ")
    return body_text


# Creates full repository
def make_repo(driver, repo_dir, overwrite=False):
    document_number = 0
    driver.switch_to.default_content()
    switch_to(driver, "sidebar")
    clicked = list()
    while True:
        count = 0
        elements = driver.find_elements_by_tag_name("li")
        if len(elements) == 0:
            break
        for li in elements:
            if li not in clicked:
                try:
                    _type = li.get_attribute("type")
                except exceptions.WebDriverException:
                    _type = None
                if _type == "collection":
                    try:
                        span = li.find_element_by_class_name("title")
                        span.click()
                        clicked.append(li)
                        time.sleep(1)
                        count += 1
                        close_open_tabs(driver)
                        driver.switch_to.default_content()
                        switch_to(driver, "sidebar")
                        break
                    except (exceptions.WebDriverException, exceptions.NoSuchElementException):
                        continue
                elif _type == "unit" or _type == "leaf":
                    extension = get_expected_path(driver, li)
                    path = repo_dir + extension + li.get_attribute("name").replace('"', "'").replace("/", ";").replace(":", "-") + ".txt"
                    print(path)
                    try:
                        span = li.find_element_by_class_name("title")
                        span.click()
                        clicked.append(li)
                        count += 1
                    except exceptions.WebDriverException:
                        continue
                    document_text = copy_document(driver, document_number)
                    document_number += 1
                    path = ensure_dir(path)
                    try:
                        with open(path + "/" + li.get_attribute("name").replace("/", ";") + ".txt", "wb") as f:
                            f.write(document_text.encode())
                    except exceptions.WebDriverException:
                        pass
                    close_open_tabs(driver)
                    driver.switch_to.default_content()
                    switch_to(driver, "sidebar")


# logs into yeshivat har etzion account on responsa.co.il
def login(driver):
    driver.switch_to.default_content()
    switch_to(driver, "titles")
    switch_to(driver, "iFrame2")
    username_input = driver.find_element_by_id("login")
    username_input.send_keys("haryeshiva")
    password_input = driver.find_element_by_id("password")
    password_input.send_keys("369har")
    login_button = driver.find_elements_by_class_name("btnMid")[1]
    login_button.click()


# method to be used if 10 people are using account
# logs in repeatedly until accepted
def get_into_account(driver):
    while True:
        login(driver)
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                            'Timed out waiting for PA creation ' +
                                            'confirmation popup to appear.')
            alert_obj = driver.switch_to.alert
            alert_obj.accept()
        except(exceptions.NoSuchFrameException, exceptions.TimeoutException):
            return
        time.sleep(2)
