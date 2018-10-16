import json

command = "it140"
public = True

def execute(command, user):
    from noob_snhubot import bot_id

    attachment = None

    vid_dict = {
        "basics" : [
            ["Tabs and Indentation: ", "https://youtu.be/3XbPF2saKck\n"],
            ["Data Types: Strings: ", "https://youtu.be/BgoUPzkGlwU\n"], 
            ["Data Types: Boolean: ", "https://youtu.be/RrvjoSY5FnI\n"], 
            ["Data Types: Numbers: ", "https://youtu.be/jagQT1BhXfw\n"]
        ], 
        "dicts" : [
            ["Dictionary Basics: ", "https://youtu.be/xu6Sf1QAwLw\n"]
        ], 
        "files" : [
            ["Basic Read/Write Files: ", "https://youtu.be/cj8-F2TazlE\n"]
        ], 
        "functions" : [
            ["Function Basics: ", "https://youtu.be/Jfty6Uut_U4\n"]
        ],
        "lists" : [
            ["Simple Lists: ", "https://youtu.be/adTQFdjzfts\n"], 
            ["List Searching: ", "https://youtu.be/pBOL7dUHMh4\n"], 
            ["2D Lists: ", "https://youtu.be/HhBEY0UFRkQ\n"]
        ],
        "it140" : [
            ["Recursion: ", "https://youtu.be/Mv9NEXX1VHc"]
        ],
        "projects" : [
            ["Grocery List: ", "https://youtu.be/ZpNbFrMcqM\n"],
            ["ATM Script: ", "https://youtu.be/UR7o14jgS5g\n"], 
            ["Fixed Length File: ", "https://youtu.be/WXW_sUridko\n"], 
            ["Variable Length File: ", "https://youtu.be/NjJJfPKExKE\n"], 
            ["Account Transactions: ", "https://youtu.be/6l88pu9Ba94\n"]
        ], 
        "regex" : [
            ["Regular Expression Basics: ", "https://youtu.be/0gUhbDreiTs\n"]
        ] 
    }
    
    def give_help():
        response = "Here is a list of valid IT-140 topics:\n\n`basics`\n`dicts`\n`files`\n`functions`\n`lists`\n`projects`\n`regex`\n"
        return response, None
    
    def give_basics():
        links = ""
        for item in vid_dict["basics"]:
            links += item[0] + item[1]
        attachment = json.dumps([
                        {
                            "pretext" : "Everyone has to start somewhere!\n",
                            "fields": [
                                {
                                    "title" : "Basics Videos",
                                    "value" : "You may find these videos helpful:\n\n" + links,
                                }
                            ],
                            "color":"good"
                        }
                    ])
        return None, attachment
    
    def give_dicts():
        links = ""
        for item in vid_dict["dicts"]:
            links += item[0] + item[1]
        attachment = json.dumps([
                {
                    "pretext" : "Dictionaries!  Lovely Python data type.  Here is some info:\n",
                    "fields": [
                        {
                            "title" : "Dictionary Videos",
                            "value" : "You may find these videos helpful:\n\n" + links,
                        }
                    ],
                    "color":"good"
                }
            ])
        return None, attachment

    def give_files():
        links = ""
        for item in vid_dict["files"]:
            links += item[0] + item[1]
        attachment = json.dumps([
                {
                    "pretext" : "File handling.  Can be a grizzly topic.  Our friend Eddie is here to help!\n",
                    "fields": [
                        {
                            "title" : "Files Videos",
                            "value" : "You may find these videos helpful:\n\n" + links,
                        }
                    ],
                    "color":"good"
                }
            ])
        return None, attachment
    
    def give_functions():
        links = ""
        for item in vid_dict["functions"]:
            links += item[0] + item[1]
        attachment = json.dumps([
                {
                    "pretext" : "Functions.  A very important topic.  This may be helpful:\n",
                    "fields": [
                        {
                            "title" : "Function Videos",
                            "value" : "You may find these videos helpful:\n\n" + links,
                        }
                    ],
                    "color":"good"
                }
            ])
        return None, attachment
    
    def give_lists():
        links = ""
        for item in vid_dict["lists"]:
            links += item[0] + item[1]
        attachment = json.dumps([
                {
                    "pretext" : "Lists!  Awesome choice!  I think we have you covered.\n",
                    "fields": [
                        {
                            "title" : "List Videos",
                            "value" : "You may find these videos helpful:\n\n" + links,
                        }
                    ],
                    "color":"good"
                }
            ])
        return None, attachment
    
    def give_it140():
        links = ""
        for item in vid_dict["it140"]:
            links += item[0] + item[1]
        attachment = json.dumps([
                {
                    "pretext" : "It looks like you entered 'recursion.'  Excellent topic!\n",
                    "fields": [
                        {
                            "title" : "Recursion Videos",
                            "value" : "You may find these videos helpful:\n\n" + links,
                        }
                    ],
                    "color":"good"
                }
            ])
        return None, attachment
    
    def give_projects():
        links = ""
        for item in vid_dict["projects"]:
            links += item[0] + item[1]
        attachment = json.dumps([
                {
                    "pretext" : "These projects can get pretty gnarly.  Have a gander at these videos:\n",
                    "fields": [
                        {
                            "title" : "Project Videos",
                            "value" : "You may find these videos helpful:\n\n" + links,
                        }
                    ],
                    "color":"good"
                }
            ])
        return None, attachment

    def give_regex():
        links = ""
        for item in vid_dict["regex"]:
            links += item[0] + item[1]
        attachment = json.dumps([
                {
                    "pretext" : "Regular expressions!  Spectacular programming topic.  Plus, you're almost done!\n",
                    "fields": [
                        {
                            "title" : "Regex Videos",
                            "value" : "You may find these videos helpful:\n\n" + links,
                        }
                    ],
                    "color":"good"
                }
            ])
        return None, attachment

    give_options = {
    "help" : give_help,
    "basics" : give_basics,
    "dicts" : give_dicts,
    "files" : give_files,
    "functions" : give_functions,
    "lists" : give_lists,
    "it140" : give_it140,
    "projects" : give_projects,
    "regex" : give_regex
    }

    cmd = command.split()

    if len(cmd) > 1:
        topic = cmd[1]
        try:
            response, attachment = give_options[topic]()
        except KeyError:
            response = "I'm sorry, Dave.  I'm afraid I can't do that. Try `<@{}> it140 help` for a list of topics.".format(bot_id)
    else:
        response = "Looks like you may have forgotten the topic.  You can get a list from `<@{}> it140 help`.".format(bot_id)
            
    return response, attachment