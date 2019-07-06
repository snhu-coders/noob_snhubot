command = "channels"
public = True


def execute(command, user, bot):
    # Get IM list
    channels_info = bot.slack_client.api_call("channels.list")
    channels = {} # dictionary for listing all channels in workspace

    # Get the channels list and prep for mention expansion
    if channels_info.get("ok"):
        for channel in channels_info.get("channels"):
            id = channel.get("id")
            purpose = channel.get("purpose").get("value")

            channels[id] = purpose # Add new dictionary item with purpose

    attachment = None
    
    channel_output = ""
    for k, v in channels.items():
        channel_output += "<#{}>: {}\n".format(k, v.encode('ascii', errors="replace").decode())
        
    response = """
_*Here's a detailed list of our channels for your convenience.*_
Click on the links to view the channels and start chatting!
{}
""".format(channel_output)

    return response, attachment
