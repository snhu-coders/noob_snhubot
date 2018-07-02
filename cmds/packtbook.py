import datetime
import json
import time

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from urllib.request import urlopen

command = 'packtbook'
public = True

def execute(command, user):    
    response = None
    attachment = None
    mini = False
    url = 'https://www.packtpub.com/packt/offers/free-learning/'

    # Optional mini output
    if len(command.split()) > 1:
        arg = command.split()[1]

        if arg.lower() == "mini":
            mini = True
    
    # Simple catch all error logic
    try:
        soup = BeautifulSoup(urlopen(url), 'html.parser')

        # Grab the book title
        book_box = soup.find('div', attrs={'class':'dotd-title'})
        book_title = book_box.text.strip()

        # Grab the book image
        book_img = soup.find('img', attrs={'class':'bookimage'})
        book_img_src = book_img['src'].strip().replace(' ', '%20')
        # format book image
        if book_img_src.lower().startswith("//"):
            book_img_src = "https" + book_img_src
        elif not book_img_src.lower().startswith("https://"):
            book_img_src = "https://" + book_img_src

        # Grab the timestamps
        book_expires = soup.find('span', attrs={'class':'packt-js-countdown'})
        expires_time = datetime.datetime.fromtimestamp(int(book_expires['data-countdown-to']))
        cur_time = datetime.datetime.fromtimestamp(int(time.time()))        
        
        # Figure out time output (handles plurals)
        attrs = ['hours', 'minutes', 'seconds']
        human_readable = lambda delta: ['{} {}'.format(
            getattr(delta, attr),
            getattr(delta, attr) > 1 and attr or attr[:-1])
            for attr in attrs if getattr(delta, attr)]
        
        time_diff = relativedelta(expires_time, cur_time)
        times = human_readable(time_diff)

        time_string = "{}, {}, and {}".format(*times)

        output = {"pretext":"The Packt Free Book of the Day is:",
                "title":book_title,
                "title_link":url,
                "footer":"There's still {} to get this book!".format(time_string),                
                "color":"#ffca5b"}
        
        if mini:
            output['thumb_url'] = "{}".format(book_img_src)
        else:
            output['image_url'] = "{}".format(book_img_src)

        attachment = json.dumps([output])

    except:
        # TODO: For some reason this link won't unfurl in Slack
        response = 'I have failed my human overlords!\nYou should be able to find the Packt Free Book of the day here: {}'.format(url)

    return response, attachment