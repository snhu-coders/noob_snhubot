import string
import random

from Bot import Bot

from cmds import airspeed_velocity as cmd_airspeed_velocity


class TestCmdAirspeedVelocity(object):
    cmd = "what is the airspeed velocity of an unladen swallow?"
    uid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
    bot = Bot(uid, None, None)

    def test_command(self):
        assert cmd_airspeed_velocity.command == self.cmd

    def test_public(self):
        assert cmd_airspeed_velocity.public

    def test_output_types(self):
        response = cmd_airspeed_velocity.execute(self.cmd, self.uid, self.bot)

        assert type(response) == tuple
        assert type(response[0]) == str
        assert response[1] is None

    def test_output(self):
        response = cmd_airspeed_velocity.execute(self.cmd, self.uid, self.bot)

        assert response[0] == "https://youtu.be/_7iXw9zZrLo?t=182"
