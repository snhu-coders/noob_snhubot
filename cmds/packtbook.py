import json
import time
import re

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from urllib.request import urlopen
from urllib.error import HTTPError

command = 'packtbook'
public = True
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(chrome_options=options, executable_path="/usr/lib/chromium-browser/chromedriver")

def grab_element(delay, elem_function, attr, regex):
    while delay:
        if attr == "product__img":
            elem = elem_function(attr)
            text = elem.get_attribute("src")
            if regex.match(text):
                return text
            else:
                time.sleep(0.5)
                delay -= 0.5
        else:
            elem = elem_function(attr)
            text = elem.text
            if regex.match(text):
                return text
            else:
                time.sleep(0.5)
                delay -= 0.5
    # returns here only on failure
    return "Failed"

def execute(command, user):    
    response = None
    attachment = None
    mini = False
    delay = 10
    book_regex = re.compile(r"^[A-Z].*$")
    img_regex = re.compile(r"^https:\/\/.*[.]\w{3}$")
    time_regex = re.compile(r"\d{1,2}:\d{1,2}:\d{1,2}")
    time_attrs = ["hours", "minutes", "seconds"]
    url = 'https://www.packtpub.com/packt/offers/free-learning/'

    # Optional mini output
    if len(command.split()) > 1:
        arg = command.split()[1]

        if arg.lower() == "mini":
            mini = True
    
    # Simple catch all error logic
    try:
        # Set the driver to wait a little bit before assuming elements are not present, then grab the page:
        driver.implicitly_wait(delay)
        driver.get(url)

        # Get the elements
        book_string = grab_element(delay, driver.find_element_by_class_name, "product__title", book_regex)
        img_src = grab_element(delay, driver.find_element_by_class_name, "product__img", img_regex)
        time_string = grab_element(delay, driver.find_element_by_class_name, "countdown__timer", time_regex)

        # If any of those end up failing, tell the people to try again.  If not, do the attachment
        if book_string == "Failed" or img_src == "Failed" or time_string == "Failed":
            response = "This operation has failed.  Dynamic page elements are weird like that.  Try again."
        else:
            # Set the time here
            time_split = [int(x) for x in time_string.split(":")]
            times_left = []

            for t in time_split:
                ind = time_split.index(t)
                if t == 0:
                    # If there are no hours/etc, go ahead and skip it
                    pass
                elif t == 1:
                    times_left.append("{} {}".format(t, time_attrs[ind][:-1]))
                elif t > 1:
                    times_left.append("{} {}".format(t, time_attrs[ind]))
            
            if len(times_left) == 1:
                time_left_string = "{}".format(times_left[0])
            elif len(times_left) == 2:
                time_left_string = "{} and {}".format(times_left[0], times_left[1])
            elif len(times_left) == 3:
                time_left_string = "{}, {}, and {}".format(times_left[0], times_left[1], times_left[2])


            output = {"pretext":"The Packt Free Book of the Day is:",
                    "title":book_string,
                    "title_link":url,
                    "footer":"There's still {} to get this book!".format(time_left_string),
                    "color":"#ffca5b"}

            if mini:
                output['thumb_url'] = "{}".format(img_src)
            else:
                output['image_url'] = "{}".format(img_src)

            attachment = json.dumps([output])

    except HTTPError as err:
        print(err)

        response = "It appears that the free book page doesn't exist anymore.  Are they still giving away books?"
    except (TimeoutError, TimeoutException) as err:
        print(err)

        response = "Looks like the operation timed out.  Please try again later."
    except Exception as err:
        print(err)

        response = 'I have failed my human overlords!\nYou should be able to find the Packt Free Book of the day here: {}'.format(url)

    return response, attachment