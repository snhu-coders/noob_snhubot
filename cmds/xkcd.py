import json
import requests

command = "xkcd"
public = True

"""	
month	"10"
num	2217
link	""
year	"2019"
news	""
safe_title	"53 Cards"
transcript	""
alt	"Well, there's one right here at the bottom, where it says \"53.\""
img	"https://imgs.xkcd.com/comics/53_cards.png"
title	"53 Cards"
day	"18"
"""

def execute(command, user, bot):
    attachment = None
    response = None

    r = requests.get('https://xkcd.com/info.0.json')

    if r.status_code == 200:
        data = json.loads(r.text)

        attachment = json.dumps([{
            "title": "{}".format(data["title"]),
            "title_link": "https://xkcd.com/{}".format(data["num"]),
            "image_url": "{}".format(data["img"]),
            "footer": "{}".format(data["alt"])
        }])

    return response, attachment
