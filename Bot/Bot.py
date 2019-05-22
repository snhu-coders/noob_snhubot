from BotHelper import Scheduler
from BotHelper import Response

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

        print(f"Command: '{command}' - User: {user} - Channel: {channel}")

        if msg_type == "message":
            response, attachment = self.execute_command(command, cmds.COMMANDS.items(), user)
        else:
            response, channel = self.execute_command(command, cmds.COMMANDS_HIDDEN.items(), user)

        return Response(channel, response or default_response, attachment)

    def handle_scheduled_command(self, command, channel, user, msg_type):
        response = self.handle_command(command, channel, user, msg_type)
        self.slack_client.response_to_client(response)
