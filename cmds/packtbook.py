import json
import time
import re

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from urllib.error import HTTPError
from noob_snhubot import DB_CONFIG

command = 'packtbook'
public = True
do_requests = False
symbol_regex = re.compile(r"^[\W]+")
opts = Options()
opts.add_argument("--headless")
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(chrome_options=opts)
increment = 0.5

# Check to see if we're using a Mongo configuration.  If so,
# set the db and collection.  If not, disable the requests
# functionality
if DB_CONFIG:
    if "book_requests" in DB_CONFIG["collections"]:
        # Grab the main mongo connection
        from BotHelper import MongoConnection

        mongo = MongoConnection(
            db=DB_CONFIG['db'],
            collection=DB_CONFIG['collections']['book_requests'],
            hostname=DB_CONFIG['hostname'],
            port=DB_CONFIG['port']
        )

        # Enable requests if Mongo connects
        if mongo.connected:
            do_requests = True


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


def insert_request_word(word: str, first_user: str):
    """
    Inserts a new word into the collection of requests

    :param word: word to insert into collection
    :type word: str
    :param first_user: first user to add to the request
    :type first_user: str
    :return: None
    :rtype: None
    """

    # Insert the word into the collection
    mongo.insert_document({"word": word, "users": [first_user]})


def remove_request_word(word: str):
    """
    Removes the given word from the collection of requests

    :param word: word to remove from collection
    :type word: str
    :return: None
    :rtype: None
    """

    # Remove the word's document from the collection
    mongo.delete_document({"word": word})


def insert_user_into_request(request: dict, insert_user: str):
    """
    Inserts a new user into an already existing request word

    :param request: current request of word
    :type request: dict
    :param insert_user: user to enter into the request
    :type insert_user: str
    :return: None
    :rtype: None
    """

    # Insert the user into the word
    request["users"].append(insert_user)
    # Then update the document in the db
    mongo.update_document_by_oid(request["_id"], {"$set": {"users": request["users"]}})


def remove_user_from_words(requests: list, remove_user: str):
    """
    Removes the user from a single word in the collection of requests.  Also
    calls remove_request_word if the user was the sole user in the request.

    :param requests: collection of requests from which to remove the user
    :type requests: dict
    :param remove_user: user to be removed from the request words
    :type remove_user: str
    :return: None
    :rtype: None
    """

    # Process each of the words given
    for req in requests:
        # Remove the user's association with the request word
        req["users"].remove(remove_user)

        # Then check to see if the word's list is empty.  If so, remove it from the
        # collection
        if len(req["users"]) == 0:
            remove_request_word(req["word"])
        else:
            mongo.update_document_by_oid(req["_id"], {"$set": {"users": req["users"]}})


def split_text(text: str):
    """
    Slightly more elaborate split function that automatically converts
    the text to lowercase and accounts for random spaces

    :param text: text to split
    :type text: str
    :return: list of split words
    :rtype: list
    """

    # First, remove punctuation
    sub_text = re.sub("[:,]", "", text)
    # Then set everything to lowercase
    sub_text = sub_text.lower()
    # Split text, avoiding blanks
    split_list = [x.strip() for x in sub_text.split(" ") if x != ""]
    # Return the completed list
    return split_list


def execute(command, user):
    response = None
    attachment = None
    delay = 10
    time_attrs = ["hours", "minutes", "seconds"]
    url = 'https://www.packtpub.com/packt/offers/free-learning/'

    # Split the given command here and set it all to lowercase
    split_command = split_text(command)

    # Check to see if the user is trying a request.  If so, insert them
    # into the collection.  If not, proceed as normal
    if len(split_command) > 1 and split_command[1] == "request":
        # If requests are enabled, then do the work.  If not, tell the user that requests are disabled.
        if do_requests:
            if len(split_command) > 2:
                # Check to see if the word after "request" starts with a symbol.  If the argument
                # is something we recognize, then do the appropriate thing.  If not, tell the user
                # to run the main command for options
                if symbol_regex.match(split_command[2]):
                    if split_command[2] in ["-d", "--delete"]:
                        # Gather the words, making sure there are no blanks
                        words = [x for x in split_command[3:] if not symbol_regex.match(x)]

                        # For each word given, remove the user from the word's entry in the collection
                        if len(words) > 0:
                            remove_from_words = []
                            req = mongo.find_documents({"word": {"$in": words}})

                            for word in req:
                                if user in word["users"]:
                                    remove_from_words.append(word)

                            remove_user_from_words(remove_from_words, user)

                            if len(words) > 0:
                                response = "I have deleted your request(s) for: " + ", ".join(words)
                            else:
                                response = "I did not delete anything.  Did you have symbols in the word(s)?"
                        else:
                            # If the words list is empty, then the user didn't provide any words
                            response = "The correct format for deleting requests is the following:\n\n" \
                                "`@NoobSNHUbot packtbook request -d words, to, delete, here`  or:\n" \
                                "`@NoobSNHUbot packtbook request --delete words, to, delete, here`"
                    elif split_command[2] in ["-c", "--clear"]:
                        req = mongo.find_documents({"users": user})

                        remove_user_from_words(req, user)
                        response = "All of your requests have been cleared."
                    elif split_command[2] == "--justforfun":
                        request_list = mongo.find_documents({})

                        # Here we are simply iterating through the collection to build a nice
                        # list to print

                        response = "Here are the current requests:\n\n" + \
                                   "\n".join([f"`{req['word']}: {', '.join(req['users'])}`" for req in request_list])
                    elif split_command[2] == "--admin":
                        response = "You have selected the admin option.  Not yet implemented."
                    else:
                        response = "Unknown symbol or argument detected.  Were you trying to delete or clear " \
                            "requests?  Run `@NoobSNHUbot packtbook request` for a list of options."
                else:
                    # Gather the words, making sure there are no blanks
                    words = [x for x in split_command[2:] if not symbol_regex.match(x)]

                    # See if the words are already in the collection.  If they are, add the user to them if they aren't
                    # there already.  If the words are not there, add them with an initial list of a single user.
                    for word in words:
                        req = mongo.find_document({"word": word})

                        if req:
                            # Only add the user if they are not in there
                            if user not in req["users"]:
                                insert_user_into_request(req, user)
                        else:
                            insert_request_word(word, user)

                    response = "You have made a book request for: " + ", ".join(words)
            else:
                response = "The correct format is the following:\n\n" \
                    "*To add:*\n`@NoobSNHUbot packtbook request words, to, add, here`\n" \
                    "*To delete:*\n`@NoobSNHUbot packtbook request -d words, to, delete, here`  or:\n" \
                    "`@NoobSNHUbot packtbook request --delete words, to, delete, here`\n" \
                    "*To clear all*:\n`@NoobSNHUbot packtbook request -c`  or:\n" \
                    "`@NoobSNHUbot packtbook request --clear`"

        else:
            response = "Requests are currently disabled.  Contact your workspace admin for information."
    else:
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
                # Split the title so we can check words
                title_split = split_text(book_string)
                # We'll use this list to tag users later
                tag_list = set()
                # Find the right documents
                req = mongo.find_documents({"word": {"$in": title_split}})

                # Figure out if we have to tag anyone
                for word in req:
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

                output = {
                    "pretext": f"The Packt Free Book of the Day is:",
                    "text": f"Come and get it!\n{', '.join([f'<@{x}>' for x in tag_list])}",
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
