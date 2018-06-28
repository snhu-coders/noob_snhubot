
command = "channels"

def execute(command, user):
    # import on execution
    from noob_snhubot import slack_client
    
    # Get IM list
    channels_info = slack_client.api_call("channels.list")
    channels = {} # dictionary for listing all channels in workspace
    
    # Get the channels list and prep for mention expantion
    if channels_info.get("ok"):
        for channel in channels_info.get("channels"):
            id = channel.get("id")
            purpose = channel.get("purpose").get("value")

            channels[id] = purpose # Add new dictionary item with purpose

    # Process channels dictionary for output
    channel_output = ""
    for k, v in channels.items():
        channel_output += "<#{}>: {}\n".format(k, v)

    attachment = None
    response = """
_*Here's a detailed list of our channels for your convenience.*_
Click on the links to view the channels and start chatting!
{}
""".format(channel_output)

    return response, attachment