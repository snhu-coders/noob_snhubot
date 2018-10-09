
command = "it140"
public = True

def execute(command, user):
    from noob_snhubot import bot_id

    cmd = command.split()
    response = "I'm sorry, Dave.  I'm afraid I can't do that. Try `<@{}> it140 help` for a list of topics.".format(bot_id)

    """
    Maybe this one?  Design options.
    response = "I'm sorry, {}.  I'm afraid I can't do that.  Try `<@{}> it140 help` for a list of topics.".format(user, bot_id)
    """

    attachment = None

    vid_dict = {
    "basics1" : "https://youtu.be/3XbPF2saKck\n", # tabs and indentation
    "basics2" : "https://youtu.be/BgoUPzkGlwU\n", # data types: strings
    "basics3" : "https://youtu.be/RrvjoSY5FnI\n", # data types: boolean
    "basics4" : "https://youtu.be/jagQT1BhXfw\n", # data types: numbers
    "dicts1" : "https://youtu.be/xu6Sf1QAwLw\n", # dictionary basics
    "files1" : "https://youtu.be/cj8-F2TazlE\n", # basic read / write files 
    "functions1" : "https://youtu.be/Jfty6Uut_U4\n", # function basics
    "lists1" : "https://youtu.be/adTQFdjzfts\n", # simple lists
    "lists2" : "https://youtu.be/pBOL7dUHMh4\n", # list searching
    "lists3" : "https://youtu.be/HhBEY0UFRkQ\n", # 2d lists
    "projects1" : "https://youtu.be/6l88pu9Ba94\n", # account transactions
    "projects2" : "https://youtu.be/NjJJfPKExKE\n", # variable length file
    "projects3" : "https://youtu.be/WXW_sUridko\n", # fixed length file
    "projects4" : "https://youtu.be/UR7o14jgS5g\n", # atm script
    "projects5" : "https://youtu.be/ZpNbFrMcqM\n", # grocery list
    "regex1" : "https://youtu.be/0gUhbDreiTs\n" # regular expression basics
    }

    if len(cmd) > 1:
 
        topic = cmd[1]

        if topic.lower().startswith("help"):
            response = "Here is a list of valid topics:\n\n`basics`\n`dicts`\n'files'\n`functions`\n`lists`\n`projects`\n`regex`\n"
        elif topic.lower().startswith("basics"):
            response = "Everyone has to start somewhere!  Here are some videos on some of the basics:\n"
            for key, value in vid_dict:
                if key.startswith("basics"):
                    response += value
        elif topic.lower().startswith("dicts"):
            response = "Dictionaries!  Lovely Python data type.  Here is some info:\n"
            for key, value in vid_dict:
                if key.startswith("dicts"):
                    response += value
        elif topic.lower().startswith("files"):
            response = "File handling.  Can be a grizzly topic.  Our friend Eddie is here to help!\n"
            for key, value in vid_dict:
                if key.startswith("files"):
                    response += value
        elif topic.lower().startswith("functions"):
            response = "Functions.  A very important topic.  This may be helpful:\n"
            for key, value in vid_dict:
                if key.startswith("functions"):
                    response += value
        elif topic.lower().startswith("lists"):
            response = "Lists!  Awesome choice!  I think we have you covered.\n"
            for key, value in vid_dict:
                if key.startswith("lists"):
                    response += value
        elif topic.lower().startswith("projects"):
            response = "These projects can get pretty gnarly.  Have a gander at these videos:\n"
            for key, value in vid_dict:
                if key.startswith("projects"):
                    response += value
        elif topic.lower().startswith("regex"):
            response = "Regular expressions!  Spectacular programming topic.  Plus, you're almost done!\n"
            for key, value in vid_dict:
                if key.startswith("regex"):
                    response += value

    return response, attachment