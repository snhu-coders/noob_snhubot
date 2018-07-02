import os
import sys
import time
import re
import json
import websocket._exceptions as ws_exceptions
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
                return message, event["channel"], event["user"], event["type"]
        elif event["type"] == "team_join":
            return "greet user", None, event["user"].get("id"), event["type"]
    
    return None, None, None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention in message text and returns the user ID which 
        was mentioned. If there is no direct mentions, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second groups contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def execute_command(command, commands, user):
    response1 = None
    response2 = None
    
    for k, v in commands:     
        if command.lower().startswith(v):
            cmd = getattr(getattr(cmds, k), 'execute')
            
            response1, response2 = cmd(command, user)

    return response1, response2

def handle_command(command, channel, user, msg_type):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user    
    default_response = "Does not compute. Try `<@{}> help` for command information.".format(bot_id)

    response = None
    attachment = None

    print("Recieved command '{}' from user: {} on channel: {}".format(command, user, channel))

    if msg_type == "message":
        response, attachment = execute_command(command, cmds.COMMANDS.items(), user)
    else:
        response, channel = execute_command(command, cmds.COMMANDS_HIDDEN.items(), user)
    
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
    # main loop to reconnect bot if necessary
    while True:
        #if slack_client.rtm_connect(with_team_state=False):
        if slack_client.rtm_connect(with_team_state=False):
            print("Noob SNHUbot connected and running!")
            
            # Read bot's user id by calling Web API method 'auth.test'
            bot_id = slack_client.api_call("auth.test")["user_id"]        

            print("Bot ID: " + bot_id)
            
            while True:
                # Exceptions: TimeoutError, ConnectionResetError, WebSocketConnectionClosedException
                try:
                    command, channel, user, msg_type = parse_bot_commands(slack_client.rtm_read())

                    if command:
                        handle_command(command, channel, user, msg_type)
                    time.sleep(RTM_READ_DELAY)                
                except TimeoutError as err:
                    print("Timeout Error occurred.\n{}".format(err))
                except ws_exceptions.WebSocketConnectionClosedException as err:
                    print("Connection is closed.\n{}\n{}".format(err, *sys.exc_info()[0:]))                    
                    break
                except ConnectionResetError as err:
                    print("Connection has been reset.\n{}\n{}".format(err, *sys.exc_info()[0:]))
                    break
                except:
                    print("Something awful happened!\n{}\n{}".format(*sys.exc_info()[0:]))
                    sys.exit()
        else:
            print("Connection failed. Exception traceback printed above.")
            break

        print("Reconnecting...")
    