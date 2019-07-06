import string
import random
import os

from Bot import Bot
from BotHelper import SlackConn

from cmds import greet_user as cmd_greet_user


class TestCmdGreetUser(object):
    cmd = "greet user"
    user = "UAP2Y9R96"  #gsfellis_snhu user
    uid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
    slack_client = SlackConn(os.environ["SLACK_CLIENT"])
    bot = Bot(uid, slack_client, None)
    team_info = bot.slack_client.api_call("team.info")
    channels_info = bot.slack_client.api_call("channels.list")
    team_name = team_info.get("team").get("name")
    im_channel = bot.slack_client.api_call("im.open", user=user)

    def get_general(self):
        # Get the general channel ID
        if self.channels_info.get("ok"):
            for channel in self.channels_info.get("channels"):
                channel_id = channel.get("id")
                name = channel.get("name")

                if name == "general":
                    return channel_id

    def test_command(self):
        assert cmd_greet_user.command == self.cmd

    def test_public(self):
        assert not cmd_greet_user.public

    def test_output_types(self):
        response = cmd_greet_user.execute(self.cmd, self.user, self.bot)

        assert type(response) == tuple
        assert type(response[0]) == str
        assert type(response[1]) == str

    def test_output(self):

        greeting = """
_Welcome to *{0}*, <@{1}>!_ 

We're so happy that you've joined our community! Please introduce yourself in <#{3}>, and let us know what brings you to the team! 
*{0}* is a place for people to _*learn*_, _*collaborate*_, _*network*_, and just hang out. Please be kind to each other, and _encourage_ learning!

I am <@{2}>, your friendly protocol droid. You may issue commands to me in any channel I'm present in _(even this one)_!
Use `<@{2}> help` to _*learn more about the commands*_ I respond to. For a _*detailed list of our channels*_, please issue the `<@{2}> channels` command.

*RULES TO LIVE BY:*
1. *Do not give away, nor expect, direct answers to homework assignments*. This is a learning community and cheating will not be tolerated.
2. *Do not post requests for help in multiple channels*. Find an appropriate channel for your request and be patient. Someone will be along to help you in time.
3. *Use code snippets*! See below for help posting code snippets. *Do not cut and paste code samples directly into chat*. It's impossible to read.

*More about Slack:*
_If you're new to Slack_, please check out the <https://get.slack.help/hc/en-us/articles/217626358-Tour-the-Slack-app#windows-app-1|Slack Tour>.
_A handy feature of Slack_ is the ability to <https://get.slack.help/hc/en-us/articles/204145658-Create-a-snippet|Create a Snippet>.

""".format(self.team_name, self.user, self.uid, self.get_general())

        response = cmd_greet_user.execute(self.cmd, self.user, self.bot)

        assert response[0] == greeting
        assert response[1] == self.im_channel.get("channel").get("id")

    def test_bad_user(self):
        im_channel = self.bot.slack_client.api_call("im.open", user="BAD USER")
        response = cmd_greet_user.execute(self.cmd, "BAD USER", self.bot)


        assert response[0] is None
        assert response[1] is None
