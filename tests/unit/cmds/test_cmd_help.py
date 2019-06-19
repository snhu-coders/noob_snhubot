import string
import random

from Bot import Bot

from cmds import help as cmd_help, COMMANDS


class TestCmdHelp(object):
    cmd = "help"
    uid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
    bot = Bot(uid, None, None)

    def test_command(self):
        assert cmd_help.command == self.cmd

    def test_public(self):
        assert cmd_help.public

    def test_output_types(self):
        response = cmd_help.execute(self.cmd, self.uid, self.bot)
        
        assert type(response) == tuple
        assert type(response[0]) == str
        assert response[1] is None

    def test_output(self):
        response = cmd_help.execute(self.cmd, self.uid, self.bot)
        text = [x.replace('`', '').replace('-', '').strip() for x in response[0].split('\n')[1:-1]]

        assert response[0].startswith("Here are all the commands I know how to execute:\n")
        assert len(text) == len(COMMANDS)
        
        for cmd in list(COMMANDS.values()):
            assert cmd in text
