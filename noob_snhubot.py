import argparse
import datetime
import os
import time
import sys

import websocket._exceptions as ws_exceptions
import yaml

from Bot import Bot
from BotHelper import MongoConn, Scheduler, SlackConn, output


def get_token(slack_config=None, slack_env_variable='SLACK_CLIENT'):
    """
    Get the Slack token used for connection

    Args:
        slack_config (str): Path of the Slack configuration file
        slack_env_variable (str): The environment variable used for the Slack client token

    Returns:
        The token from the configuration file or the environment variable
    """
    try:
        if slack_config:
            return load_config(slack_config)['token']    
        else:
            #v = args.slack_env_variable if args.slack_env_variable else 'slack_client'
            return os.environ[slack_env_variable.upper()]
    except KeyError as e:        
        sys.exit("No environment variable {} defined. Exiting...".format(e))


def load_config(config):
    """
    Process the YAML contents of a configuration file.
    Exit's the program if an invalid file is passed.

    Args:
        config (str): Path of the configuration file to be processed

    Returns:
        Python object representing the YAML configuration
    """
    try:
        with open(os.path.realpath(config), 'r') as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)
    except FileNotFoundError as e:
        sys.exit("Could not find configuration file: {}".format(e.filename))            


if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description='Launch the Noob SNHUBot application.')
    parser.add_argument("-m", "--mongo_config", required=False, help="Relative path to Mongo Database configuration file.")
    parser.add_argument("-c", "--sched_config", required=False, help="Relative path to Scheduler Configuration file.")
    parser.add_argument("-d", "--delay", required=False, default=1, type=int, help="Sets the delay between RTM reads.")
    
    sc = parser.add_mutually_exclusive_group()
    sc.add_argument("-s", "--slack_config", required=False, help="Relative path to Slack configuration file.")
    sc.add_argument("-e", "--slack_env_variable", required=False, help="Environment variable holding the Slack client token.")

    # noise = parser.add_mutually_exclusive_group()
    # noise.add_argument("-v", "--verbosity", action="count", default=1)
    # noise.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args()

    # Process Token
    if args.slack_config:
        token = get_token(slack_config = args.slack_config)
    elif args.slack_env_variable:
        token = get_token(slack_env_variable = args.slack_env_variable)
    else:
        token = get_token()    

    # create new Slack Client object
    slack_client = SlackConn(token) 
    
    # Setup Mongo DB if present
    mongo = None
    
    if args.mongo_config:
        mc = load_config(args.mongo_config)

        mongo = MongoConn(mc,           
            db = mc['db'],
            collection = mc['collections']['conn'],
            hostname = mc['hostname'],
            port = mc['port']
            )

    # Setup Scheduler if config present
    if args.sched_config:
        sc = load_config(args.sched_config)

        scheduler = Scheduler(sc)
    else:
        scheduler = Scheduler()

    # Primary Loop
    while True:
        if slack_client.rtm_connect(with_team_state=False, auto_reconnect=True):            
            output("Noob SNHUbot connected and running!")

            # Instantiate Bot with user id from Web API method 'auth.test', and slack and mongo connections
            bot = Bot(slack_client.api_call("auth.test")["user_id"], slack_client, scheduler, mongo)
            output(f"Bot ID: {bot.id}")

            # Log Connection
            if mongo:
                doc = {
                    'date': datetime.datetime.utcnow(),
                    'type': 'connection',
                    'token': token,
                    'bot_id': bot.id
                    }

                mongo.log_to_collection(doc, mc['db'], mc['collections']['conn'])

            while slack_client.server.connected:
                # Exceptions: TimeoutError, ConnectionResetError, WebSocketConnectionClosedException
                try:
                    command, channel, user, msg_type = slack_client.parse_bot_commands(slack_client.rtm_read(), bot.id)

                    if command:
                        slack_client.response_to_client(bot.handle_command(command, channel, user, msg_type))
                    time.sleep(args.delay)        
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
                    bot.cleanup_your_mess()
                    sys.exit()

                # schedule tasks if the bot is running a scheduler
                if bot.scheduler:
                    bot.scheduler.process_schedule(bot.id, bot.commands, bot.handle_scheduled_command)

                    # Execute clean up only when tasks have been scheduled
                    if bot.scheduler.schedule:
                        bot.scheduler.cleanup_sched()

        else:
            output("Connection failed. Exception traceback printed above.")
            break

        output("Reconnecting...")    
