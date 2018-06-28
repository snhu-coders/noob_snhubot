
command = "help"

def execute(command, user):
    # import on execution
    from cmds import COMMANDS

    commands = list(COMMANDS.values())
    commands.sort()

    attachment = None    
    response = 'Here are all the commands I know how to execute:\n'

    for command in commands:
        response += "  - `{}`\n".format(command)

    return response, attachment