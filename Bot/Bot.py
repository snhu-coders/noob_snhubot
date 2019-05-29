import datetime
from BotHelper import Scheduler
from BotHelper import Response
from BotHelper import output

# Import bot cmds
import cmds

class Bot():
    # constants
    RTM_READ_DELAY = 1
    MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

    scheduler = Scheduler()

    def __init__(self, id, slack_client, db_conn=None):
        self.id = id
        self.slack_client = slack_client
        self.db_conn = db_conn
        self.commands = list(cmds.COMMANDS.values()) # list of available commands
        self.commands.sort()

    def execute_command(self, command, commands, user, log_id=None):
        """
        Executes the command and returns responses received from command output.

        Respones can be response, attachment, or channels, depending on command executed
        """
        response1 = None
        response2 = None
        
        for k, v in commands:     
            if command.lower().startswith(v):
                cmd = getattr(getattr(cmds, k), 'execute')
                
                response1, response2 = cmd(command, user, self)

        return response1, response2

    def handle_command(self, command, channel, user, msg_type):
        """
        Executes bot command if the command is known
        """
        # Default response is help text for the user    
        default_response = "Does not compute. Try `<@{}> help` for command information.".format(self.id)

        response = None
        attachment = None

        output(f"Command: '{command}' - User: {user} - Channel: {channel}")

        if self.db_conn:
            #TODO: create a document generator
            doc = {
                'date': datetime.datetime.utcnow(), 
                'command': command, 
                'user': user, 
                'channel': channel
                }

            result = self.db_conn.log_to_collection(doc, self.db_conn.CONFIG['db'], self.db_conn.CONFIG['collections']['cmds'])

            #TODO: Fix logging output for DB stuff
            output(f"[{self.db_conn.db}: {self.db_conn.collection}] - Inserted: {result.inserted_id}")

        if msg_type == "message":
            response, attachment = self.execute_command(command, cmds.COMMANDS.items(), user)
        else:
            response, channel = self.execute_command(command, cmds.COMMANDS_HIDDEN.items(), user)

        #TODO: Make a better name for out
        out = Response(channel, response or default_response, attachment)

        # Log response
        if self.db_conn:
            response_type = "attachment" if out.attachment else "response"
            update = {'$set': {
                    'response': {
                    'date': datetime.datetime.now(),
                    'type': response_type,
                    'message': out.attachment or out.message or default_response, 
                    'channel': out.channel
                }
            }}
            
            result = self.db_conn.update_document_by_oid(result.inserted_id, update)
             
            output(f"[{self.db_conn.db}: {self.db_conn.collection}] - Updated: {result.raw_result}")

        return out

    def handle_scheduled_command(self, command, channel, user, msg_type):
        response = self.handle_command(command, channel, user, msg_type)
        self.slack_client.response_to_client(response)
