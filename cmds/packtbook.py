import json
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from urllib.error import HTTPError

command = 'packtbook'
public = True
opts = Options()
opts.add_argument("--headless")
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=opts)
increment = 0.5


def grab_element(delay, elem_function, attr):
    while delay:
        try:
            if attr == "product__img":
                elem = elem_function(attr)
                text = elem.get_attribute("src")
                if len(text) > 0:
                    return text
            else:
                elem = elem_function(attr)
                text = elem.text
                if len(text) > 0:
                    return text
        except NoSuchElementException:
            # returns here only on failure
            return None

        time.sleep(increment)
        delay -= increment


def execute(command, user, bot):
    response = None
    attachment = None
    delay = 10
    time_attrs = ["hours", "minutes", "seconds"]
    url = 'https://www.packtpub.com/packt/offers/free-learning/'

    # Simple catch all error logic
    try:
        # Set the driver to wait a little bit before assuming elements are not present, then grab the page:
        driver.implicitly_wait(delay)
        driver.get(url)

        # Get the elements
        warning_message = grab_element(2, driver.find_element_by_css_selector, ".message.warning")
        book_string = grab_element(delay, driver.find_element_by_class_name, "product__title")
        img_src = grab_element(delay, driver.find_element_by_class_name, "product__img")
        time_string = grab_element(delay, driver.find_element_by_class_name, "countdown__timer")

        # Check to see if the warning message was present
        if warning_message:
            response = warning_message
        # If any of the regular elements fail, tell the people to try again.  If not, do the attachment
        elif None in [book_string, img_src, time_string]:
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

            time_format = "{}"

            if len(times_left) == 2:
                time_format = "{} and {}"
            elif len(times_left) == 3:
                time_format = "{}, {}, and {}"

            time_left_string = time_format.format(*times_left)

            output = {
                "pretext": "The Packt Free Book of the Day is:",
                "title": book_string,
                "title_link": url,
                "footer": "There's still {} to get this book!".format(time_left_string),
                "color": "#ffca5b",
                "image_url": "{}".format(img_src)
            }

            attachment = json.dumps([output])

    except HTTPError as err:
        print(err)

        response = "It appears that the free book page doesn't exist anymore.  Are they still giving away books?"
    except (TimeoutError, TimeoutException) as err:
        print(err)

        response = "Looks like the operation timed out.  Please try again later."
    except Exception as err:
        print(err)

        response = 'I have failed my human overlords!\nYou should be able to find the Packt Free' \
                   ' Book of the day here: {}'.format(url)

    return response, attachment
