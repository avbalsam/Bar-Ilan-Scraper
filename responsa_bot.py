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


# creates needed directories for given file and fixes any problems with filename
def ensure_dir(file_path):
    directory = os.path.dirname(file_path.replace("\"", "'").replace(":", "-") + "/")
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


# presses the "close tabs" button
def close_open_tabs(driver):
    driver.switch_to.default_content()
    switch_to(driver, "titles")
    driver.find_element_by_css_selector("img[title='Close all open tabs']").click()
    print("closed tabs")


# switches to specified frame object
def switch_to(driver, frame_id):
    iframe = driver.find_element_by_id(frame_id)
    try:
        driver.switch_to.frame(iframe)
    except exceptions.NoSuchFrameException:
        pass


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
    WebDriverWait(driver, timeout=10).until(lambda d: d.find_element_by_id("titles"))
    switch_to(driver, "titles")
    try:
        print("25%")
        WebDriverWait(driver, timeout=10).until(lambda d: d.find_element_by_id("iFrame" + str(document_number + 3)))
        switch_to(driver, "iFrame" + str(document_number + 3))
        WebDriverWait(driver, timeout=10).until(lambda d: d.find_element_by_id("docFrame"))
        switch_to(driver, "docFrame")
        print("50%")
        WebDriverWait(driver, timeout=10).until(lambda d: d.find_element_by_id("docBody"))
    except exceptions.TimeoutException:
        return None
    print("60%")
    time.sleep(.2)
    # header = driver.find_element_by_id("header")
    body_el = driver.find_element_by_class_name("docBody")
    body = body_el.get_attribute("innerHTML")
    soup = BeautifulSoup(body, "html.parser")
    body = soup.find_all("span")
    body_arr = list()
    body_text = ""
    print("75%")
    for item in body:
        if item.text != "":
            body_arr.append(item.text)
    print("85%")
    for x in body_arr:
        body_text += x + " "
    print("90%")
    for x in body_arr:
        body_text = body_text.replace(x+" "+x+" "+x+" ", x+" ")
    print("100%")
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
                    name = li.get_attribute("name").replace('"', "'").replace("/", ";").replace(":", "-")
                except exceptions.WebDriverException:
                    _type = None

                # if the item is a directory, click on it
                if _type == "collection":
                    try:
                        span = li.find_element_by_class_name("title")
                        span.click()
                        clicked.append(li)
                        time.sleep(.2)
                        count += 1
                        close_open_tabs(driver)
                        driver.switch_to.default_content()
                        switch_to(driver, "sidebar")
                        break
                    except (exceptions.WebDriverException, exceptions.NoSuchElementException):
                        continue
                # if the item is a file, click on it and copy it to repository
                elif _type == "unit" or _type == "leaf":
                    extension = get_expected_path(driver, li)
                    path = repo_dir + extension
                    # print(path)
                    try:
                        span = li.find_element_by_class_name("title")
                        span.click()
                        clicked.append(li)
                        count += 1
                    except exceptions.WebDriverException:
                        continue
                    errs = 0
                    document_text = None
                    copy = True

                    # logs in if login button exists
                    login_buttons = driver.find_elements_by_class_name("btnMid")
                    if "Login" in [x.text for x in login_buttons]:
                        login(driver)

                    # tries a maximum of ten times to copy document, otherwise changes copy flag
                    while document_text is None:
                        errs += 1
                        if errs == 3:
                            get_into_account(driver, document_number)
                        document_text = copy_document(driver, document_number)
                    document_number += 1

                    # if copy flag has not been changed, writes document_text to correct file
                    if not copy:
                        continue
                    path = ensure_dir(path)
                    filename = path + "/" + name + ".txt"
                    print(filename)
                    with open(filename, "wb") as f:
                        f.write(document_text.encode())
                    close_open_tabs(driver)
                    driver.switch_to.default_content()
                    switch_to(driver, "sidebar")


# logs into yeshivat har etzion account on responsa.co.il
def login(driver, document_number):
    driver.switch_to.default_content()
    switch_to(driver, "titles")
    try:
        switch_to(driver, "iFrame" + str(document_number + 3))
    except (exceptions.NoSuchElementException, exceptions.NoSuchFrameException):
        return -1
    username_input = driver.find_element_by_id("login")
    username_input.send_keys("haryeshiva")
    password_input = driver.find_element_by_id("password")
    password_input.send_keys("369har")
    login_button = driver.find_elements_by_class_name("btnMid")[1]
    login_button.click()


# method to be used if 10 people are using account
# logs in repeatedly until accepted
def get_into_account(driver, document_number):
    while True:
        if login(driver, document_number) == -1:
            return -1
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                            'Timed out waiting for PA creation ' +
                                            'confirmation popup to appear.')
            alert_obj = driver.switch_to.alert
            alert_obj.accept()
        except(exceptions.NoSuchFrameException, exceptions.TimeoutException):
            return
        time.sleep(2)
