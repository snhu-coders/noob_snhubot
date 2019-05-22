import datetime
import re
import sys
import time
import websocket._exceptions as ws_exceptions
import yaml
import os

from slackclient import SlackClient
from BotHelper import Scheduler
from BotHelper import MongoConnection

# Import bot cmds
import cmds

# load configuration from file if it exists
try:
    with open("config\config.yml", 'r') as f:
        print(f"UTC: {datetime.datetime.utcnow().timestamp()} - Reading configuration in config.yml")
        CONFIG = yaml.load(f.read())
        BOT_CONFIG = CONFIG['slackbot'] if 'slackbot' in CONFIG.keys() else None
        DB_CONFIG = CONFIG['mongo'] if 'mongo' in CONFIG.keys() else None
except FileNotFoundError as err:
    print(f"UTC: {datetime.datetime.utcnow().timestamp()} - No configuration file detected")
    BOT_CONFIG = None
    DB_CONFIG = None

# constants
RTM_READ_DELAY = 1
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

# global variables
bot_id = None # bot's user ID in Slack (updated on connection)
client_id = BOT_CONFIG['token'] if BOT_CONFIG else os.environ['SLACK_CLIENT'] # load client token from config

slack_client = SlackClient(client_id) # create new Slack Client object
scheduler = Scheduler() # Scheduled events

if DB_CONFIG:
    mongo = MongoConnection(
        db = DB_CONFIG['db'], 
        collection = DB_CONFIG['collections']['conn'], 
        hostname = DB_CONFIG['hostname'], 
        port = DB_CONFIG['port']    
    )

    # Exit if not connected to database
    if not mongo.connected:
        sys.exit('No database connection available.')

commands = list(cmds.COMMANDS.values()) # list of available commands
commands.sort()

def output(message):
    """
    Print message with UTC timestamp
    """
    print(f"UTC: {datetime.datetime.utcnow().timestamp()} - {message}")

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

def execute_command(command, commands, user, log_id=None):
    """
    Executes the command and returns responses received from command output.

    Respones can be response, attachment, or channels, depending on command executed
    """
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

    output(f"Command: '{command}' - User: {user} - Channel: {channel}")    
    
    if DB_CONFIG:
        doc = {'date': datetime.datetime.utcnow(), 
            'command': command, 
            'user': user, 
            'channel': channel
        }

        mongo.use_db(DB_CONFIG['db'])
        mongo.use_collection(DB_CONFIG['collections']['cmds'])
        result = mongo.insert_document(doc)
        output(f"[{mongo.db}: {mongo.collection}] - Inserted: {result.inserted_id}")        

    if msg_type == "message":
        response, attachment = execute_command(command, cmds.COMMANDS.items(), user)
    else:
        response, channel = execute_command(command, cmds.COMMANDS_HIDDEN.items(), user)
    
    # Log response
    if DB_CONFIG:
        response_type = "attachment" if attachment else "response"
        update = {'$set': {
            'response': {
                'date': datetime.datetime.now(),
                'type': response_type,
                'message': attachment or response or default_response, 
                'channel': channel
            }
        }}
        result = mongo.update_document_by_oid(result.inserted_id, update)
        output(f"[{mongo.db}: {mongo.collection}] - Updated: {result.raw_result}")
    
    # Sends the response back to the channel
    if attachment:
        output(f"Sending attachment: {attachment}")        
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            attachments=attachment
        )
    else:
        output(f"Sending response: {response or default_response}")
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response or default_response
        )

def main():
    """
    Primary logic loop.
    """
    # main loop to reconnect bot if necessary
    while True:
        #if slack_client.rtm_connect(with_team_state=False):
        if slack_client.rtm_connect(with_team_state=False, auto_reconnect=True):            
            output("Noob SNHUbot connected and running!")
            
            # pull global bot_id into scope
            global bot_id
            
            # Read bot's user id by calling Web API method 'auth.test'            
            bot_id = slack_client.api_call("auth.test")["user_id"]
            output(f"Bot ID: {bot_id}")            
            
            if DB_CONFIG:
                mongo.use_db(DB_CONFIG['db'])
                mongo.use_collection(DB_CONFIG['collections']['conn'])
                doc = {'date': datetime.datetime.utcnow(),
                    'type': 'connection',
                    'token': client_id,
                    'bot_id': bot_id
                }
                
                result = mongo.insert_document(doc)         
                output(f"[{mongo.db}: {mongo.collection}] - Inserted: {result.inserted_id}")
            
            while slack_client.server.connected:
                # Exceptions: TimeoutError, ConnectionResetError, WebSocketConnectionClosedException
                try:
                    command, channel, user, msg_type = parse_bot_commands(slack_client.rtm_read())

                    if command:
                        handle_command(command, channel, user, msg_type)
                    time.sleep(RTM_READ_DELAY)                
                except TimeoutError as err:                    
                    output("Timeout Error occurred.\n{}".format(err))
                except ws_exceptions.WebSocketConnectionClosedException as err:
                    output("Connection is closed.\n{}\n{}".format(err, *sys.exc_info()[0:]))
                    break
                except ConnectionResetError as err:
                    output("Connection has been reset.\n{}\n{}".format(err, *sys.exc_info()[0:]))
                    break
                except:
                    output("Something awful happened!\n{}\n{}".format(*sys.exc_info()[0:]))
                    sys.exit()

                # Keep scheduling the task                
                if not scheduler.has_task('packtbook', datetime.time(20, 30)):
                    scheduler.schedule_cmd('packtbook', 'CB8B913T2', datetime.time(20, 30), handle_command, bot_id)

                # Execute clean up only when tasks have been scheduled
                if scheduler.sched:
                    scheduler.cleanup_sched()
                    
        else:
            output("Connection failed. Exception traceback printed above.")
            break

        output("Reconnecting...")    

if __name__ == "__main__":
    # execute only if run as script
    main()
