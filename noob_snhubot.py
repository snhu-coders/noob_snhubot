import os
import time
import re
import json
import random
from slackclient import SlackClient

# create env variable with client_id in it
client_id = os.environ["SLACK_CLIENT"]

# create new Slack Client object
slack_client = SlackClient(client_id)

# noob_snhubot's user ID in Slack:
bot_id = None

# constants
RTM_READ_DELAY = 1
EXAMPLE_COMMAND = "do"
COMMANDS = [     
    "do",
    "what's my name?", 
    "what is the airspeed velocity of an unladen swallow?",
    "roll"
]
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

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
    default_response = "I don't understand. Here's a few things my human overlords have allowed me to do: \n`{}`.".format(", ".join(COMMANDS))

    # Finds and executes the given command, filling in response
    response = None
    attach = False
    attachment = None
    # This is where you start to implement more commands!
    if command.lower().startswith(COMMANDS[0]):
        response = "Sure...write some more code then I can do that!"
    if command.lower().startswith(COMMANDS[1]):        
        response = "Your name is <@{}>! Did you forget or something?".format(user)
    if command.lower().startswith(COMMANDS[2]):
        response = "https://youtu.be/y2R3FvS4xr4?t=14s"
    if command.lower().startswith(COMMANDS[3]):
        ROLL_REGEX = "^([1-9][0-9]{0,2})d([1-9][0-9]{0,2})(([+.-])(\d+))?$"
        roll = command.split()

        response = "That roll is not valid. Try `@Noob SNHUbot roll help`"   

        if len(roll) > 1:
            roll = command.split()[1]
            
            if roll.lower().startswith("help"):
                response = "Let me show you how I roll:\n`roll XdY[±Z]` rolls X number of Y-Sided dice with an optional positive or negative Z modifier.\nExamples:\n`@Noob SNHUbot roll 2d6`\n`@Noob SNHUbot roll 1d10+3`\n`@Noob SNHUbot roll 20d4-5`"
            else:
                match = re.match(ROLL_REGEX, roll)

                if match is not None:
                    rolls = []
                    num_dice = int(match.groups()[0])
                    pips = int(match.groups()[1])            

                    for x in range(num_dice):
                        rolls.append(random.randint(1, pips))

                    total = sum(rolls)
                    
                    if match.groups()[2] is not None:
                        mod = int(match.groups()[4])

                        if match.groups()[3] == "+":
                            total += mod
                        else:
                            total -= mod            
                    
                    attach = True
                    attachment = json.dumps([
                        {
                            "text":"<@{}> rolled *{}*".format(user, total),
                            "fields":[
                                {
                                    "title":"Roll",
                                    "value":"{}".format(match.group()),
                                    "short":"true"
                                },
                                {
                                    "title":"Values",
                                    "value":"{}".format(" ".join(str(roll) for roll in rolls)),
                                    "short":"true"
                                },
                                {
                                    "title":"Modifier",
                                    "value":"{}".format(match.groups()[2]),
                                    "short":"true"
                                }
                            ],
                            "color":"good"
                        }
                    ])            
    
    # Sends the response back to the channel
    if attach:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            attachments=attachment
        )
    else:
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
    