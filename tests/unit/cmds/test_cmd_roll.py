import string
import random
import json

from Bot import Bot

from cmds import roll as cmd_roll


class TestCmdRoll(object):
    cmd = "roll"
    uid = ''.join(random.choice(string.ascii_uppercase + string.digits)
                  for _ in range(9))
    bot = Bot(uid, None, None)

    def get_json_response(self, dice, total, rolls, modifier):
        expected = json.dumps([
            {
                "text": "<@{}> rolled *{}*".format(self.uid, total),
                "fields": [
                    {
                        "title": "Roll",
                        "value": "{}{}".format(dice, modifier or ""),
                        "short": "true"
                    },
                    {
                        "title": "Values",
                        "value": "{}".format(" ".join(str(roll) for roll in rolls)),
                        "short": "true"
                    },
                    {
                        "title": "Modifier",
                        "value": "{}".format(modifier),
                        "short": "true"
                    }
                ],
                "color": "good"
            }
        ])

        return expected

    def test_command(self):
        assert cmd_roll.command == self.cmd

    def test_public(self):
        assert cmd_roll.public

    def test_output_types_base(self):
        response = cmd_roll.execute(self.cmd, self.uid, self.bot)

        assert isinstance(response, tuple)
        assert isinstance(response[0], str)
        assert response[1] is None

    def test_output_types_roll(self):
        dice = "1d20"
        cmd = "{} {}".format(self.cmd, dice)

        response = cmd_roll.execute(cmd, self.uid, self.bot)

        assert isinstance(response, tuple)
        assert response[0] is None
        assert isinstance(response[1], str)

    def test_output_base(self):
        response = cmd_roll.execute(self.cmd, self.uid, self.bot)

        expected = "That roll is not valid. Try `<@{}> roll help`".format(
            self.uid)

        assert response[0] == expected

    def test_output_roll_one_no_modifier(self):
        dice = "1d1"
        modifier = None
        rolls = [1]
        total = 1

        cmd = "{} {}{}".format(self.cmd, dice, modifier or "")

        response = cmd_roll.execute(cmd, self.uid, self.bot)

        expected = self.get_json_response(dice, total, rolls, modifier)

        assert response[1] == expected

    def test_output_roll_two_no_modifier(self):
        dice = "2d1"
        modifier = None
        rolls = [1, 1]
        total = 2

        cmd = "{} {}{}".format(self.cmd, dice, modifier or "")

        response = cmd_roll.execute(cmd, self.uid, self.bot)

        expected = self.get_json_response(dice, total, rolls, modifier)

        assert response[1] == expected

    def test_output_roll_three_no_modifier(self):
        dice = "3d1"
        modifier = None
        rolls = [1, 1, 1]
        total = 3

        cmd = "{} {}{}".format(self.cmd, dice, modifier or "")

        response = cmd_roll.execute(cmd, self.uid, self.bot)

        expected = self.get_json_response(dice, total, rolls, modifier)

        assert response[1] == expected

    def test_output_roll_one_with_modifier(self):
        dice = "1d1"
        modifier = "+1"
        rolls = [1]
        total = 2

        cmd = "{} {}{}".format(self.cmd, dice, modifier or "")

        response = cmd_roll.execute(cmd, self.uid, self.bot)

        expected = self.get_json_response(dice, total, rolls, modifier)

        assert response[1] == expected

    def test_output_roll_two_with_negative_modifier(self):
        dice = "2d1"
        modifier = "-1"
        rolls = [1, 1]
        total = 1

        cmd = "{} {}{}".format(self.cmd, dice, modifier or "")

        response = cmd_roll.execute(cmd, self.uid, self.bot)

        expected = self.get_json_response(dice, total, rolls, modifier)

        assert response[1] == expected

    def test_output_roll_three_with_modifier(self):
        dice = "3d1"
        modifier = "+1"
        rolls = [1, 1, 1]
        total = 4

        cmd = "{} {}{}".format(self.cmd, dice, modifier or "")

        response = cmd_roll.execute(cmd, self.uid, self.bot)

        expected = self.get_json_response(dice, total, rolls, modifier)

        assert response[1] == expected

    def test_output_invalid_number_of_dice(self):
        dice_pools = ["0d20", "1000d20"]

        for dice in dice_pools:
            cmd = "{} {}".format(self.cmd, dice)
            expected = "That roll is not valid. Try `<@{}> roll help`".format(
                self.uid)

            response = cmd_roll.execute(cmd, self.uid, self.bot)

            assert response[0] == expected

    def test_output_invalid_number_of_sides(self):
        dice_pools = ["2d0", "2d1000"]

        for dice in dice_pools:
            cmd = "{} {}".format(self.cmd, dice)
            expected = "That roll is not valid. Try `<@{}> roll help`".format(
                self.uid)

            response = cmd_roll.execute(cmd, self.uid, self.bot)

            assert response[0] == expected

    def test_output_invalid_modifiers(self):
        modifiers = [".1", "&100", "PLUS ONE"]

        for mod in modifiers:
            cmd = "{} 1d20{}".format(self.cmd, mod)
            expected = "That roll is not valid. Try `<@{}> roll help`".format(
                self.uid)

            response = cmd_roll.execute(cmd, self.uid, self.bot)

            assert response[0] == expected

    # TODO: Write test to test random rolls
