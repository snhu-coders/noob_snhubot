import string
import random
import json

from Bot import Bot

from cmds import it140 as cmd_it140


class TestCmdIt140(object):
    cmd = "it140"
    uid = ''.join(random.choice(string.ascii_uppercase + string.digits)
                  for _ in range(9))
    bot = Bot(uid, None, None)

    def get_json_response(self, topic):
        data = cmd_it140.data.get(topic)
        pretext = data[0][1]
        title = data[0][0]
        links = "".join([item[0] + item[1] for item in data[1]])

        json_response = json.dumps([
            {
                "pretext": pretext,
                "fields": [
                    {
                        "title": title + " Videos",
                        "value": "You may find these videos helpful:\n\n" + links,
                    }
                ],
                "color": "#0a3370"
            }
        ])

        return json_response

    def test_command(self):
        assert cmd_it140.command == self.cmd

    def test_public(self):
        assert cmd_it140.public

    def test_output_types_base_command(self):
        response = cmd_it140.execute(self.cmd, self.uid, self.bot)

        assert isinstance(response, tuple)
        assert isinstance(response[0], str)
        assert response[1] is None

    def test_output_types_with_topic(self):
        cmd = self.cmd + " basics"
        response = cmd_it140.execute(cmd, self.uid, self.bot)

        assert isinstance(response, tuple)
        assert response[0] is None
        assert isinstance(response[1], str)

    def test_output_base_command(self):
        response = cmd_it140.execute(self.cmd, self.uid, self.bot)
        response_topics = [x.replace('`', '').replace(
            '-', '').strip() for x in response[0].split('\n')[2:]]

        assert response[0].startswith(
            "Here is a list of valid IT-140 topics.  Proceed by entering: `<@{}> it140 topic`.".format(self.uid))
        assert len(response_topics) == len(cmd_it140.data) - \
            1  # because of hidden IT140 command

        for topic in list(cmd_it140.data.keys()):
            if topic != "it140":  # again because of hidden IT140 command
                assert topic in response_topics

    def test_output_basics(self):
        topic = "basics"
        cmd = "{} {}".format(self.cmd, topic)

        response = cmd_it140.execute(cmd, self.uid, self.bot)

        assert response[1] == self.get_json_response(topic)

    def test_output_dicts(self):
        topic = "dicts"
        cmd = "{} {}".format(self.cmd, topic)

        response = cmd_it140.execute(cmd, self.uid, self.bot)

        assert response[1] == self.get_json_response(topic)

    def test_output_files(self):
        topic = "files"
        cmd = "{} {}".format(self.cmd, topic)

        response = cmd_it140.execute(cmd, self.uid, self.bot)

        assert response[1] == self.get_json_response(topic)

    def test_output_functions(self):
        topic = "functions"
        cmd = "{} {}".format(self.cmd, topic)

        response = cmd_it140.execute(cmd, self.uid, self.bot)

        assert response[1] == self.get_json_response(topic)

    def test_output_lists(self):
        topic = "lists"
        cmd = "{} {}".format(self.cmd, topic)

        response = cmd_it140.execute(cmd, self.uid, self.bot)

        assert response[1] == self.get_json_response(topic)

    def test_output_projects(self):
        topic = "projects"
        cmd = "{} {}".format(self.cmd, topic)

        response = cmd_it140.execute(cmd, self.uid, self.bot)

        assert response[1] == self.get_json_response(topic)

    def test_output_regex(self):
        topic = "regex"
        cmd = "{} {}".format(self.cmd, topic)

        response = cmd_it140.execute(cmd, self.uid, self.bot)

        assert response[1] == self.get_json_response(topic)

    def test_output_it140(self):
        topic = "it140"
        cmd = "{} {}".format(self.cmd, topic)

        response = cmd_it140.execute(cmd, self.uid, self.bot)

        assert response[1] == self.get_json_response(topic)

    def test_output_bad_topic(self):
        topic = "BAD TOPIC"
        cmd = "{} {}".format(self.cmd, topic)

        response = cmd_it140.execute(cmd, self.uid, self.bot)
        expected = "I'm sorry, Dave.  I'm afraid I can't do that. Try `<@{}> it140` for a list of valid topics."\
            .format(self.uid)

        assert response[0] == expected
