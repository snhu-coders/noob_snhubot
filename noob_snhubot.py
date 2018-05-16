import os
import time
import re
import json
from slackclient import SlackClient

# Import bot cmds
import cmds

# create env variable with client_id in it
client_id = os.environ["SLACK_CLIENT"]

# create new Slack Client object
slack_client = SlackClient(client_id)

# noob_snhubot's user ID in Slack:
bot_id = None

# constants
RTM_READ_DELAY = 1
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

commands = list(cmds.COMMANDS.values())
commands.sort()

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If it's not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == bot_id:
                return message, event["channel"], event["user"]
        elif event["type"] == "team_join":
            return "greet user test", None, event["user"].get("id")
    
    return None, None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention in message text and returns the user ID which 
        was mentioned. If there is no direct mentions, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second groups contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel, user):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user    
    default_response = "I don't understand. Here's a few things my human overlords have allowed me to do: \n`{}`.".format(", ".join(commands))

    # Finds and executes the given command, filling in response
    response = None    
    attachment = None

    print("Recieved command '{}' from user: {}".format(command, user))

    # iterate over commands and execute
    for k, v in cmds.COMMANDS.items():        
        if command.lower().startswith(v):            
            cmd = getattr(getattr(cmds, k), 'execute')
            response, attachment = cmd(command, user)

    # if send msg
    if command.lower().startswith("greet user test"): #and channel == None:
        response, channel = greet_user(user)
    
    # Sends the response back to the channel
    if attachment:
        print("Sending attachment: {}".format(attachment))
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            attachments=attachment
        )
    else:
        print("Sending response: {}".format(response or default_response))
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response or default_response
        )

def greet_user(user):
    # Get IM list
    team_info = slack_client.api_call("team.info")
    channels_info = slack_client.api_call("channels.list")
    channels = {} # dictionary for listing all channels in workspace

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
Welcome to {0}, <@{1}>! I am <@{2}>, your friendly protocol droid. Feel free to learn more about me by saying `<@{2}> help` in any channel I'm active in.

We're so happy that you've joined us. Please introduce yourself in <#{3}>, and let us know what brings you to the team!

If you're new to Slack, please check out the <https://get.slack.help/hc/en-us/articles/217626358-Tour-the-Slack-app#windows-app-1|Slack Tour>.
A handy feature of Slack is the ability to <https://get.slack.help/hc/en-us/articles/204145658-Create-a-snippet|Create a Snippet>.

Here's a detailed list of our channels for your convenience. You've been automatically joined to some of these.
Click on the links to view the channels and start chatting!
{4}
""".format(team_name, user, bot_id, general, channel_output)

    # Return the new greeting and send private message    
    return greeting, im_channel.get("channel").get("id") if im_channel.get("ok") else (None, None)


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Noob SNHUbot connected and running!")
        # Read bot's user id by calling Web API method 'auth.test'
        bot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel, user = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel, user)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
    