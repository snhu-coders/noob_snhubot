from .MongoConn import MongoConn

"""
File containing helper functions for the request functionality of the packtbook command
"""


def insert_request_word(word: str, first_user: str, conn: MongoConn):
    """
    Inserts a new word into the collection of requests

    :param word: word to insert into collection
    :type word: str
    :param first_user: first user to add to the request
    :type first_user: str
    :param conn: specific mongo connection to access
    :type conn: MongoConn
    :return: None
    :rtype: None
    """

    # Insert the word into the collection
    conn.collection_log_remove_find(
        {"word": word, "users": [first_user]},
        conn.CONFIG["db"],
        conn.CONFIG["collections"]["book_requests"],
        conn.insert_document
    )


def remove_request_word(word: str, conn: MongoConn):
    """
    Removes the given word from the collection of requests

    :param word: word to remove from collection
    :type word: str
    :param conn: specific mongo connection to access
    :type conn: MongoConn
    :return: None
    :rtype: None
    """

    # Remove the word's document from the collection
    conn.collection_log_remove_find(
        {"word": word},
        conn.CONFIG["db"],
        conn.CONFIG["collections"]["book_requests"],
        conn.delete_document
    )


def insert_user_into_request(request: dict, insert_user: str, conn: MongoConn):
    """
    Inserts a new user into an already existing request word

    :param request: current request of word
    :type request: dict
    :param insert_user: user to enter into the request
    :type insert_user: str
    :param conn: specific mongo connection to access
    :type conn: MongoConn
    :return: None
    :rtype: None
    """

    # Insert the user into the word
    request["users"].append(insert_user)
    # Then update the document in the db
    conn.collection_update(
        request["_id"],
        {"$set": {"users": request["users"]}},
        conn.CONFIG["db"],
        conn.CONFIG["collections"]["book_requests"],
        conn.update_document_by_oid
    )


def remove_user_from_words(requests: list, remove_user: str, conn: MongoConn):
    """
    Removes the user from a single word in the collection of requests.  Also
    calls remove_request_word if the user was the sole user in the request.

    :param requests: collection of requests from which to remove the user
    :type requests: dict
    :param remove_user: user to be removed from the request words
    :type remove_user: str
    :param conn: specific mongo connection to access
    :type conn: MongoConn
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
            remove_request_word(req["word"], conn)
        else:
            conn.collection_update(
                req["_id"],
                {"$set": {"users": req["users"]}},
                conn.CONFIG["db"],
                conn.CONFIG["collections"]["book_requests"],
                conn.update_document_by_oid
            )
