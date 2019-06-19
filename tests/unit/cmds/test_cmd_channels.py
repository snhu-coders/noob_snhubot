import string
import random
import os
import re

from Bot import Bot
from BotHelper import SlackConn

from cmds import channels as cmd_channels


class TestCmdChannels(object):
    cmd = "channels"
    uid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
    slack_client = SlackConn(os.environ["SLACK_CLIENT"])
    bot = Bot(uid, slack_client, None)
    channels_info = bot.slack_client.api_call("channels.list")

    def test_command(self):
        assert cmd_channels.command == self.cmd

    def test_public(self):
        assert cmd_channels.public

    def test_output_types(self):
        response = cmd_channels.execute(self.cmd, self.uid, self.bot)

        assert type(response) == tuple
        assert type(response[0]) == str
        assert response[1] is None

    def test_output(self):
        response = cmd_channels.execute(self.cmd, self.uid, self.bot)

        assert response[0].startswith("\n_*Here's a detailed list of our channels for your convenience.*_")

        channel_match = re.compile(r"<#[0-9A-Z]{9}>")
        matches = channel_match.findall(response[0])

        assert len(self.channels_info.get("channels")) == len(matches)
