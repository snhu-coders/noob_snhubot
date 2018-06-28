
command = "greet user"

def execute(command, user):
    # import on execution
    from noob_snhubot import slack_client
    
    # Get IM list
    team_info = slack_client.api_call("team.info")
    channels_info = slack_client.api_call("channels.list")
    channels = {} # dictionary for listing all channels in workspace
    bot_id = slack_client.api_call("auth.test")["user_id"]

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
    im_channel = slack_client.api_call("im.open", user=user)

    print("IM CHANNEL:")
    print(im_channel)

    greeting = """
_Welcome to *{0}*, <@{1}>!_ 
We're so happy that you've joined our community! Please introduce yourself in <#{3}>, and let us know what brings you to the team! 
*{0}* is a place for people to _*learn*_, _*collaborate*_, _*network*_, and just hang out. Please be kind to each other, and encourage learning! Don't give away, nor expect, direct answers to homework assignments.

I am <@{2}>, your friendly protocol droid. Feel free to learn more about me by saying `<@{2}> help` in any channel I'm active in.

_If you're new to Slack_, please check out the <https://get.slack.help/hc/en-us/articles/217626358-Tour-the-Slack-app#windows-app-1|Slack Tour>.
_A handy feature of Slack_ is the ability to <https://get.slack.help/hc/en-us/articles/204145658-Create-a-snippet|Create a Snippet>.

_*Here's a detailed list of our channels for your convenience.*_ You've been automatically joined to some of these.
Click on the links to view the channels and start chatting!
{4}
""".format(team_name, user, bot_id, general, channel_output)

    # Return the new greeting and send private message    
    return greeting, im_channel.get("channel").get("id") if im_channel.get("ok") else (None, None)
