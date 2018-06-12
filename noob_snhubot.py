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
            return "greet user", None, event["user"].get("id")
    
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

    print("Recieved command '{}' from user: {} on channel: {}".format(command, user, channel))

    # iterate over commands and execute
    for k, v in cmds.COMMANDS.items():        
        if command.lower().startswith(v):            
            cmd = getattr(getattr(cmds, k), 'execute')
            
            # if a channel has been defined, run normal,
            # otherwise expect channel return
            #if command.lower().startswith("greet user"):
            if channel == None or command.lower().startswith("greet user"):            
                response, channel = cmd(command, user)
            else:
                response, attachment = cmd(command, user)

    # if greet user
    #if command.lower().startswith("greet user") and channel == None:
    #    response, channel = greet_user(user)
    
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
    