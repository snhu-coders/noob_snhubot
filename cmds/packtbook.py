import datetime
import json
import time

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from urllib.request import urlopen

command = 'packtbook'

def execute(command, user):
    response = None
    attachment = None
    mini = False

    # Optional mini output
    if len(command.split()) > 1:
        arg = command.split()[1]

        if arg.lower() == "mini":
            mini = True
    
    url = 'https://www.packtpub.com/packt/offers/free-learning/' 
    soup = BeautifulSoup(urlopen(url), 'html.parser')
    
    # Grab the book title
    book_box = soup.find('div', attrs={'class':'dotd-title'})
    book_title = book_box.text.strip()

    # Grab the book image
    book_img = soup.find('img', attrs={'class':'bookimage'})
    book_img_src = book_img['src'].strip().replace(' ', '%20')

    # Grab the timestamp
    book_expires = soup.find('span', attrs={'class':'packt-js-countdown'})
    expires_time = datetime.datetime.fromtimestamp(int(book_expires['data-countdown-to']))
    cur_time = datetime.datetime.fromtimestamp(int(time.time()))
    time_diff = expires_time - cur_time

    time_string = "time"
    
    # Figure the time out
    if str(time_diff).count(":") == 2:
        h, m, s = str(time_diff).split(":")

        time_string = "{} hours, {} minutes, and {} seconds".format(h, m, s)

    if mini:
        attachment = json.dumps([
        {
            "pretext":"The Packt Free Book of the Day is:",
            "title":book_title,
            "title_link":url,
			"footer":"There's still {} to get this book!".format(time_string),
			"thumb_url":"https:{}".format(book_img_src),
            "color":"#ffca5b"
        }])
    else:
        attachment = json.dumps([
            {
                "pretext":"The Packt Free Book of the Day is:",
                "title":book_title,
                "title_link":url,
                "footer":"There's still {} to get this book!".format(time_string),
                "image_url":"https:{}".format(book_img_src),
                "color":"#ffca5b"
            }])

    return response, attachment