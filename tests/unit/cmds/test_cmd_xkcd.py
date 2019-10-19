import json
import string
import random

from Bot import Bot

from cmds import xkcd as cmd_xkcd


class TestCmdXkcd(object):


    cmd = "xkcd"

    uid = ''.join(random.choice(string.ascii_uppercase + string.digits)
                  for _ in range(9))
    bot = Bot(uid, None, None)

    def test_command(self):
        assert cmd_xkcd.command == self.cmd

    def test_public(self):
        assert cmd_xkcd.public

    def test_output_types(self):
        response = cmd_xkcd.execute(self.cmd, self.uid, self.bot)

        assert isinstance(response, tuple)
        assert response[0] is None
        assert isinstance(response[1], str)

    def test_output(self):
        response = cmd_xkcd.execute(self.cmd, self.uid, self.bot)

        data = json.loads(response[1])
        assert data is not None
