import re

from slackclient import SlackClient

from .Output import output


class SlackConn(SlackClient):
    MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

    def parse_bot_commands(self, slack_events, bot_id):
        """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command, channel, user id, and event type.
        If it's not found, then this function returns None, None, None, None.

        Args:
            slack_events (list): A list of Slack events, generally from the rtm_read() method of a Slack client
            bot_id (str): The Slack user ID of the bot

        Returns:
            (tuple) command, channel, user_id, event_type
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
        Processes a direct mention of the bot. Splits the message into two parts, the user ID that matches
        and the rest of the message passed in (for processing the command).

        Args:
            message_text (str): Text representation of the message to be parsed

        Returns:
            (tuple) user_id, message
        """
        matches = re.search(self.MENTION_REGEX, message_text)

        # the first group contains the username, the second groups contains the remaining message
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

    def response_to_client(self, response):
        """
        Sends a response back to the channel on the provided slack_client

        Args:
            response (Response): A response object to be sent back to Slack

        Returns:
            None
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
                text=response.message,
                unfurl_links=True
            )
