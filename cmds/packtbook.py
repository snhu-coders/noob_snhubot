"""Packtbook command module

Todo:
    * Even though this has been refactored, things can still tighten up a bit.
    * Typing hints are not complete
    * Admin features at some point
    * Explore requests-html as an alternative to selenium
"""

import json
import time
import re

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from urllib.error import HTTPError
from typing import Any

command = 'packtbook'
public = True
increment = 0.5

# The following regex is designed to separate all of the words given
# for requests while accounting for phrases indicated by "phrase".

# We'll try a slightly reworked regex for a while.  Here's the old one:
# separator_regex = re.compile(r"(?<=\")[-+#.$ \w]+(?=\")|[-+#.$\w]+")

separator_regex = re.compile(r"(?<=\")(?:[-+#.$\w]+\s?)+(?=\")|[-+#.$\w]+")

try:
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=opts)
except WebDriverException as e:
    print("Error encountered while starting the ChromeDriver:\n{}".format(e))
    driver = None


def parse_arguments(command) -> (str, set):
    split_command = [x.lower() for x in separator_regex.findall(command)]

    if len(split_command) == 1:
        return "packtbook", None
    elif len(split_command) > 2 and split_command[1] in ["request", "requests"] \
            and split_command[2] in ["-a", "--add"]:
        return "request_add", {x for x in split_command[3:] if not x.startswith("-")}
    elif len(split_command) > 2 and split_command[1] in ["request", "requests"] \
            and split_command[2] in ["-d", "--delete"]:
        return "request_delete", {x for x in split_command[3:] if not x.startswith("-")}
    elif len(split_command) == 3 and split_command[1] in ["request", "requests"] \
            and split_command[2] in ["-l", "--list"]:
        return "request_list", None
    elif len(split_command) == 3 and split_command[1] in ["request", "requests"] \
            and split_command[2] in ["-c", "--clear"]:
        return "request_clear", None
    elif len(split_command) == 3 and split_command[1] in ["request", "requests"] \
            and split_command[2] == "--admin":
        return "request_admin", None
    elif len(split_command) == 3 and split_command[1] in ["request", "requests"] \
            and split_command[2] == "--dump":
        return "request_dump", None
    else:
        return "packtbook_help", None


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


def request_add(words: set, user: str, bot: Any) -> str:
    if len(words) > 0:
        # See if the words are already in the collection.  If they are, add the user to them if they aren't
        # there already.  If the words are not there, add them with an initial list of a single user.
        for word in words:
            req = bot.db_conn.find_document(
                {"word": word},
                db=bot.db_conn.CONFIG["db"],
                collection=bot.db_conn.CONFIG["collections"]["book_requests"],
            )

            if req:
                # Only add the user if they are not in there
                if user not in req["users"]:
                    # Insert the user into the word
                    req["users"].append(user)
                    # Then update the document in the db
                    bot.db_conn.update_document_by_oid(
                        req["_id"],
                        {"$set": {"users": req["users"]}},
                        db=bot.db_conn.CONFIG["db"],
                        collection=bot.db_conn.CONFIG["collections"]["book_requests"]
                    )
            else:
                bot.db_conn.insert_document(
                    {"word": word, "users": [user]},
                    db=bot.db_conn.CONFIG["db"],
                    collection=bot.db_conn.CONFIG["collections"]["book_requests"],
                )
        return "You have made a book request for: " + ", ".join(words)
    else:
        return "You didn't list any valid words to add!"


def request_delete(words: set, user: str, bot: Any) -> str:
    # For each word given, remove the user from the word's entry in the collection
    if len(words) > 0:
        req = bot.db_conn.find_documents(
            {"word": {"$in": list(words)}},
            db=bot.db_conn.CONFIG["db"],
            collection=bot.db_conn.CONFIG["collections"]["book_requests"],
        )

        for word in req:
            if user in word["users"]:
                word["users"].remove(user)

                # Then check to see if the word's list is empty.  If so, remove it from the
                # collection
                if len(word["users"]) == 0:
                    bot.db_conn.delete_document(
                        {"word": word["word"]},
                        db=bot.db_conn.CONFIG["db"],
                        collection=bot.db_conn.CONFIG["collections"]["book_requests"]
                    )
                else:
                    bot.db_conn.update_document_by_oid(
                        word["_id"],
                        {"$set": {"users": word["users"]}},
                        db=bot.db_conn.CONFIG["db"],
                        collection=bot.db_conn.CONFIG["collections"]["book_requests"]
                    )

        return "I have deleted your request(s) for: " + ", ".join(words)
    else:
        return "You didn't list any valid words to delete!"


def request_clear(user: str, bot: Any) -> str:
    req = bot.db_conn.find_documents(
        {"users": user},
        db=bot.db_conn.CONFIG["db"],
        collection=bot.db_conn.CONFIG["collections"]["book_requests"],
    )

    for word in req:
        if user in word["users"]:
            word["users"].remove(user)

            # Then check to see if the word's list is empty.  If so, remove it from the
            # collection
            if len(word["users"]) == 0:
                bot.db_conn.delete_document(
                    {"word": word["word"]},
                    db=bot.db_conn.CONFIG["db"],
                    collection=bot.db_conn.CONFIG["collections"]["book_requests"]
                )
            else:
                bot.db_conn.update_document_by_oid(
                    word["_id"],
                    {"$set": {"users": word["users"]}},
                    db=bot.db_conn.CONFIG["db"],
                    collection=bot.db_conn.CONFIG["collections"]["book_requests"]
                )

    return "All of your requests have been cleared."


def request_list(user: str, bot: Any) -> str:

    # We'll us this to store the words that the user has requested
    personal_list = []

    # Grab a list of requests that include the user
    req_list = bot.db_conn.find_documents(
        {"users": user},
        db=bot.db_conn.CONFIG["db"],
        collection=bot.db_conn.CONFIG["collections"]["book_requests"],
    )

    for word in req_list:
        if user in word["users"]:
            personal_list.append(word["word"])

    if len(personal_list) > 0:
        return "Here are your current requests: \n\n{}".format(
            "\n".join([f"`{x}`" for x in personal_list]))
    else:
        return "You haven't made any requests.  Why don't you make one already?!"


def request_admin() -> str:
    return "You have selected the admin option.  Not yet implemented"


def request_dump(bot: Any) -> str:

    req_list = bot.db_conn.find_documents(
        {},
        db=bot.db_conn.CONFIG["db"],
        collection=bot.db_conn.CONFIG["collections"]["book_requests"],
    )

    # Here we are simply iterating through the collection to build a nice
    # list to print

    return "Here are the current requests:\n\n" + \
           "\n".join([f"`{req['word']}: {', '.join(req['users'])}`" for req in req_list])


def execute(command, user, bot):
    response = None
    attachment = None

    operation, params = parse_arguments(command)

    if operation == "packtbook":
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
            error_message = grab_element(2, driver.find_element_by_css_selector, ".message.error")
            book_string = grab_element(delay, driver.find_element_by_class_name, "product__title")
            img_src = grab_element(delay, driver.find_element_by_class_name, "product__img")
            time_string = grab_element(delay, driver.find_element_by_class_name, "countdown__timer")

            # Check to see if the warning message was present
            if warning_message:
                response = warning_message
            elif error_message:
                response = "There are errors on the Packt page.  Try again after a while to see if " \
                           "they have been resolved."
            # If any of the regular elements fail, tell the people to try again.  If not, do the attachment
            elif None in [book_string, img_src, time_string]:
                response = "I couldn't grab the correct page elements.  Try again in a few minutes."
            else:
                tag_list = set()

                if bot.db_conn and "book_requests" in bot.db_conn.CONFIG["collections"]:
                    # Gather all of the requests
                    req = bot.db_conn.find_documents(
                        {},
                        db=bot.db_conn.CONFIG["db"],
                        collection=bot.db_conn.CONFIG["collections"]["book_requests"],
                    )

                    # Figure out if we have to tag anyone
                    for word in req:
                        if word["word"] in book_string.lower():
                            tag_list.update(word["users"])

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
                flavor_text = f"{', '.join([f'<@{x}>' for x in tag_list])}" if len(tag_list) > 0 else ""

                output = {
                    "pretext": f"The Packt Free Book of the Day is:",
                    "text": flavor_text,
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
    elif operation == "packtbook_help":
        response = "The correct format is the following:\n\n" \
            "*To see today's book:*\n`@NoobSNHUbot packtbook`\n" \
            "*To see your requests:*\n`@NoobSNHUbot packtbook request -l`  or:\n" \
            "`@NoobSNHUbot packtbook request --list`\n" \
            "*To add requests:*\n`@NoobSNHUbot packtbook request -a words, \"or phrases\", to, add`  or:\n" \
            "`@NoobSNHUbot packtbook request --add words, \"or phrases\", to, add`\n" \
            "*To delete requests:*\n`@NoobSNHUbot packtbook request -d words, \"or phrases\", to, delete`  or:\n" \
            "`@NoobSNHUbot packtbook request --delete words, \"or phrases\", to, delete`\n" \
            "*To clear all requests*:\n`@NoobSNHUbot packtbook request -c`  or:\n" \
            "`@NoobSNHUbot packtbook request --clear`"
    else:
        if bot.db_conn and "book_requests" in bot.db_conn.CONFIG["collections"]:
            if operation == "request_add":
                response = request_add(params, user, bot)
            elif operation == "request_delete":
                response = request_delete(params, user, bot)
            elif operation == "request_clear":
                response = request_clear(user, bot)
            elif operation == "request_list":
                response = request_list(user, bot)
            elif operation == "request_admin":
                response = request_admin()
            elif operation == "request_dump":
                response = request_dump(bot)
            else:
                response = "Sorry, I don't recognize the Packtbook option you entered. " \
                           " Were you trying to make a request?"
        else:
            response = "Request functions are currently disabled.  Contact the workspace admin for information."

    return response, attachment
