
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
    "basics" : ["https://youtu.be/3XbPF2saKck\n", # tabs and indentation
        "https://youtu.be/BgoUPzkGlwU\n", # data types: strings
        "https://youtu.be/RrvjoSY5FnI\n", # data types: boolean
        "https://youtu.be/jagQT1BhXfw\n"], # data types: numbers
    "dicts" : ["https://youtu.be/xu6Sf1QAwLw\n"], # dictionary basics
    "files" : ["https://youtu.be/cj8-F2TazlE\n"], # basic read / write files 
    "functions" : ["https://youtu.be/Jfty6Uut_U4\n"], # function basics
    "lists" : ["https://youtu.be/adTQFdjzfts\n", # simple lists
        "https://youtu.be/pBOL7dUHMh4\n", # list searching
        "https://youtu.be/HhBEY0UFRkQ\n"], # 2d lists
    "projects" : ["https://youtu.be/6l88pu9Ba94\n", # account transactions
        "https://youtu.be/NjJJfPKExKE\n", # variable length file
        "https://youtu.be/WXW_sUridko\n", # fixed length file
        "https://youtu.be/UR7o14jgS5g\n", # atm script
        "https://youtu.be/ZpNbFrMcqM\n"], # grocery list
    "regex" : ["https://youtu.be/0gUhbDreiTs\n"] # regular expression basics
    }

    if len(cmd) > 1:
 
        topic = cmd[1]

        if topic.lower().startswith("help"):
            response = "Here is a list of valid topics:\n\n`basics`\n`dicts`\n'files'\n`functions`\n`lists`\n`projects`\n`regex`\n"
        elif topic.lower().startswith("basics"):
            response = "Everyone has to start somewhere!  Here are some videos on some of the basics:\n"
            for link in vid_dict["basics"]:
                response += link
        elif topic.lower().startswith("dicts"):
            response = "Dictionaries!  Lovely Python data type.  Here is some info:\n"
            for link in vid_dict["dicts"]:
                response += link
        elif topic.lower().startswith("files"):
            response = "File handling.  Can be a grizzly topic.  Our friend Eddie is here to help!\n"
            for link in vid_dict["files"]:
                response += link
        elif topic.lower().startswith("functions"):
            response = "Functions.  A very important topic.  This may be helpful:\n"
            for link in vid_dict["functions"]:
                response += link
        elif topic.lower().startswith("lists"):
            response = "Lists!  Awesome choice!  I think we have you covered.\n"
            for link in vid_dict["lists"]:
                response += link
        elif topic.lower().startswith("projects"):
            response = "These projects can get pretty gnarly.  Have a gander at these videos:\n"
            for link in vid_dict["projects"]:
                response += link
        elif topic.lower().startswith("regex"):
            response = "Regular expressions!  Spectacular programming topic.  Plus, you're almost done!\n"
            for link in vid_dict["regex"]:
                response += link

    return response, attachment