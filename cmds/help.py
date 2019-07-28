
command = "help"
public = True


def execute(command, user, bot):
    attachment = None
    response = 'Here are all the commands I know how to execute:\n'

    for command in bot.commands:
        response += "  - `{}`\n".format(command)

    return response, attachment
