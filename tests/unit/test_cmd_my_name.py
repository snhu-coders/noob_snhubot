import pytest
import string
import random

from cmds import my_name

class TestCmdMyName(object):
    cmd = "what's my name?"
    uid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))

    def test_command(self):
        assert my_name.command == self.cmd

    def test_public(self):
        assert my_name.public

    def test_output(self):        
        outstring = "Your name is <@{}>! Did you forget or something?".format(self.uid)
        response = my_name.execute(self.cmd, self.uid)

        assert response == (outstring, None)
        