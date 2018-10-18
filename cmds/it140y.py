import json
import yaml

command = "it140y"
public = True

def execute(command, user):
    from noob_snhubot import slack_client

    with open("it140.yml", "r") as file:
        data = yaml.load(file)

    bot_id = slack_client.api_call("auth.test")["user_id"]
    response = None
    attachment = None
    cmd = command.split()

    def build_attachment(topic):
        links = ""
        for item in data["it140"]["topics"][topic]["videos"]:
            links += item["title"] + item["link"]
        title = data["it140"]["topics"][topic]["title"]
        pretext = data["it140"]["topics"][topic]["message"]
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