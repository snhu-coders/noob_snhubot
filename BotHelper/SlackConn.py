import re

from slackclient import SlackClient

from .Output import output

class SlackConn(SlackClient):    
    MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

    def parse_bot_commands(self, slack_events, bot_id):
        """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If it's not found, then this function returns None, None.
        """
        for event in slack_events:
            if event["type"] == "message" and not "subtype" in event:
                user_id, message = self.parse_direct_mention(event["text"])
                if user_id == bot_id:
                    return message, event["channel"], event["user"], event["type"]
            elif event["type"] == "team_join":
                return "greet user", None, event["user"].get("id"), event["type"]
        
        return None, None, None, None

    def parse_direct_mention(self, message_text):
        """
        Finds a direct mention in message text and returns the user ID which 
        was mentioned. If there is no direct mentions, returns None
        """
        matches = re.search(self.MENTION_REGEX, message_text)

        # the first group contains the username, the second groups contains the remaining message
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

    def response_to_client(self, response):
        """
        Sends a response back to the channel on the provided slack_client
        """    
        if response.attachment:
            output(f"Sending attachment: {response.attachment}")        
            self.api_call(
                "chat.postMessage",
                channel=response.channel,
                attachments=response.attachment
            )
        else:
            output(f"Sending response: {response.message}")
            self.api_call(
                "chat.postMessage",
                channel=response.channel,
                text=response.message
            )
