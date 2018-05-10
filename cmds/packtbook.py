import re
import json
from urllib.request import urlopen
from bs4 import BeautifulSoup

command = 'packtbook'

def execute(command, user):
    response = None
    attachment = None
    
    url = 'https://www.packtpub.com/packt/offers/free-learning/' 
    soup = BeautifulSoup(urlopen(url), 'html.parser')
    
    book_box = soup.find('div', attrs={'class':'dotd-title'})
    book_title = book_box.text.strip()

    book_img = soup.find('img', attrs={'class':'bookimage'})
    book_img_src = book_img['src'].strip().replace(' ', '%20')

    attachment = json.dumps([
        {
            "title":"Packt Free Book of the Day!",
            "title_link":url,
			"text":book_title,
			"image_url":"https:{}".format(book_img_src),
            "color":"#ffca5b"
        }])


    #print(book_title)
    #print(book_img_src)
    #print(attachment)
    return response, attachment
