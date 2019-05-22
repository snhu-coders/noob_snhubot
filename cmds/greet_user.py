
command = "greet user"
public = False

def execute(command, user, bot):
    # Get IM list
    team_info = bot.slack_client.api_call("team.info")
    channels_info = bot.slack_client.api_call("channels.list")
    channels = {} # dictionary for listing all channels in workspace
    bot_id = bot.id

    # Set the Team Name
    if team_info.get("ok"):
        team_name = team_info.get("team").get("name")
    else:
        team_name = "snhu_coders"

    # Get the channels list and prep for mention expantion
    if channels_info.get("ok"):
        for channel in channels_info.get("channels"):
            id = channel.get("id")
            name = channel.get("name")
            purpose = channel.get("purpose").get("value")

            if name == "general":
                general = id

            channels[id] = purpose # Add new dictionary item with purpose

    # Process channels dictionary for output
    channel_output = ""
    for k, v in channels.items():
        channel_output += "<#{}>: {}\n".format(k, v)

    # open the IM channel to the new user
    im_channel = bot.slack_client.api_call("im.open", user=user)

    #print("IM CHANNEL:")
    #print(im_channel)

    greeting = """
_Welcome to *{0}*, <@{1}>!_ 

We're so happy that you've joined our community! Please introduce yourself in <#{3}>, and let us know what brings you to the team! 
*{0}* is a place for people to _*learn*_, _*collaborate*_, _*network*_, and just hang out. Please be kind to each other, and _encourage_ learning!

I am <@{2}>, your friendly protocol droid. You may issue commands to me in any channel I'm present in _(even this one)_!
Use `<@{2}> help` to _*learn more about the commands*_ I respond to. For a _*detailed list of our channels*_, please issue the `<@{2}> channels` command.

*RULES TO LIVE BY:*
1. *Do not give away, nor expect, direct answers to homework assignments*. This is a learning community and cheating will not be tolerated.
2. *Do not post requests for help in multiple channels*. Find an appropriate channel for your request and be patient. Someone will be along to help you in time.
3. *Use code snippets*! See below for help posting code snippets. *Do not cut and paste code samples directly into chat*. It's impossible to read.

*More about Slack:*
_If you're new to Slack_, please check out the <https://get.slack.help/hc/en-us/articles/217626358-Tour-the-Slack-app#windows-app-1|Slack Tour>.
_A handy feature of Slack_ is the ability to <https://get.slack.help/hc/en-us/articles/204145658-Create-a-snippet|Create a Snippet>.

""".format(team_name, user, bot_id, general)

    # Return the new greeting and send private message    
    return greeting, im_channel.get("channel").get("id") if im_channel.get("ok") else (None, None)
