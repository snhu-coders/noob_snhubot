import json

command = "it140"
public = True

def execute(command, user):
    from noob_snhubot import slack_client

    bot_id = slack_client.api_call("auth.test")["user_id"]
    response = None
    attachment = None
    cmd = command.split()

    data = {
        "basics" : [
            ["Basics", "Everyone has to start somewhere!\n"],
            [
                ["Tabs and Indentation: ", "https://youtu.be/3XbPF2saKck\n"],
                ["Data Types - Strings: ", "https://youtu.be/BgoUPzkGlwU\n"], 
                ["Data Types - Boolean: ", "https://youtu.be/RrvjoSY5FnI\n"], 
                ["Data Types - Numbers: ", "https://youtu.be/jagQT1BhXfw\n"]
            ]
        ], 
        "dicts" : [
            ["Dictionary", "Dictionaries!  Lovely Python data type.  Here is some info:\n"],
            [
                ["Dictionary Basics: ", "https://youtu.be/xu6Sf1QAwLw\n"]
            ]
        ], 
        "files" : [
            ["Files", "File handling.  Can be a grizzly topic.  Our friend Eddie is here to help!\n"],
            [
                ["Basic Read/Write Files: ", "https://youtu.be/cj8-F2TazlE\n"]
            ]
        ], 
        "functions" : [
            ["Functions", "Functions.  A very important topic.  This may be helpful:\n"],
            [
                ["Function Basics: ", "https://youtu.be/Jfty6Uut_U4\n"]
            ]
        ],
        "it140" : [
            ["Recursion", "It looks like you've entered 'recursion.'  Excellent topic!\n"],
            [
                ["Recursion: ", "https://youtu.be/Mv9NEXX1VHc"]
            ]
        ],
        "lists" : [
            ["Lists", "Lists!  Awesome choice!  I think we have you covered.\n"],
            [
                ["Simple Lists: ", "https://youtu.be/adTQFdjzfts\n"], 
                ["List Searching: ", "https://youtu.be/pBOL7dUHMh4\n"], 
                ["2D Lists: ", "https://youtu.be/HhBEY0UFRkQ\n"]
            ]
        ],
        "projects" : [
            ["Projects", "These projects can get pretty gnarly.  Have a gander at these videos:\n"],
            [
                ["Grocery List: ", "https://youtu.be/ZpNbFrMcqMo\n"],
                ["ATM Script: ", "https://youtu.be/UR7o14jgS5g\n"], 
                ["Fixed Length File: ", "https://youtu.be/WXW_sUridko\n"], 
                ["Variable Length File: ", "https://youtu.be/NjJJfPKExKE\n"], 
                ["Account Transactions: ", "https://youtu.be/6l88pu9Ba94\n"]
            ]
        ], 
        "regex" : [
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
                            "pretext" : pretext,
                            "fields": [
                                {
                                    "title" : title + " Videos",
                                    "value" : "You may find these videos helpful:\n\n" + links,
                                }
                            ],
                            "color":"#0a3370"
                        }
                    ])
        return attachment

    if len(cmd) > 1:
        topic = cmd[1].lower()
        try:
            if topic == "help":
                response = "Here is a list of valid IT-140 topics:\n\n`basics`\n`dicts`\n`files`\n`functions`\n`lists`\n`projects`\n`regex`\n"
            else:
                attachment = build_attachment(topic)
        except KeyError:
            response = "I'm sorry, Dave.  I'm afraid I can't do that. Try `<@{}> it140 help` for a list of topics.".format(bot_id)
    else:
        response = "Looks like you may have forgotten the topic.  You can get a list from `<@{}> it140 help`.".format(bot_id)
             
    return response, attachment