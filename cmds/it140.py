import json

command = "it140"
public = True

data = {
    "basics": [
        ["Basics", "Everyone has to start somewhere!\n"],
        [
            ["Command line arguments: ", "https://youtu.be/oxMmUwxWAXE\n"],
            ["Tabs and Indentation: ", "https://youtu.be/3XbPF2saKck\n"],
            ["Data Types - Strings: ", "https://youtu.be/BgoUPzkGlwU\n"],
            ["String formatting: ", "https://youtu.be/W-f6lsO-HTw\n"],
            ["Data Types - Boolean: ", "https://youtu.be/RrvjoSY5FnI\n"],
            ["Data Types - Numbers: ", "https://youtu.be/jagQT1BhXfw\n"]
        ]
    ],
    "dicts": [
        ["Dictionary", "Dictionaries!  Lovely Python data type.  Here is some info:\n"],
        [
            ["Dictionary Basics: ", "https://youtu.be/xu6Sf1QAwLw\n"]
        ]
    ],
    "functions": [
        ["Functions", "Functions.  A very important topic.  This may be helpful:\n"],
        [
            ["Function Basics: ", "https://youtu.be/Jfty6Uut_U4\n"]
        ]
    ],
    "it140": [
        ["Recursion", "It looks like you've entered 'recursion.'  Excellent topic!\n"],
        [
            ["Recursion: ", "https://youtu.be/Mv9NEXX1VHc"]
        ]
    ],
    "lists": [
        ["Lists", "Lists!  Awesome choice!  I think we have you covered.\n"],
        [
            ["Simple Lists: ", "https://youtu.be/adTQFdjzfts\n"],
            ["List Searching: ", "https://youtu.be/pBOL7dUHMh4\n"],
            ["2D Lists: ", "https://youtu.be/HhBEY0UFRkQ\n"]
        ]
    ],
    "projects": [
        ["Projects", "These projects can get pretty gnarly.  Have a gander at these videos:\n"],
        [
            ["Grocery List: ", "https://youtu.be/ZpNbFrMcqMo\n"],
        ]
    ],
    "regex": [
        ["Regex", "Regular expressions!  Spectacular programming topic.  Plus, you're almost done!\n"],
        [
            ["Regular Expression Basics: ", "https://youtu.be/0gUhbDreiTs\n"]
        ]
    ]
}


def build_attachment(topic):
    links = ""
    for item in data[topic][1]:
        links += item[0] + item[1]
    title = data[topic][0][0]
    pretext = data[topic][0][1]
    attachment = json.dumps([
        {
            "pretext": pretext,
            "fields": [
                            {
                                "title": title + " Videos",
                                "value": "You may find these videos helpful:\n\n" + links,
                            }
                            ],
            "color": "#0a3370"
        }
    ])
    return attachment


def execute(command, user, bot):
    bot_id = bot.id
    response = None
    attachment = None
    cmd = command.split()

    if len(cmd) > 1:
        topic = cmd[1].lower()
        try:
            attachment = build_attachment(topic)
        except KeyError:
            response = "I'm sorry, Dave.  I'm afraid I can't do that. Try `<@{}> it140` for a list of valid topics.".format(
                bot_id)
    else:
        response = "Here is a list of valid IT-140 topics.  Proceed by entering: `<@{}> it140 topic`. \n\n".format(bot_id) \
            + "\n".join("- `{}`".format(x)
                        for x in data.keys() if x != "it140")

    return response, attachment
