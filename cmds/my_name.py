
command = "what's my name?"
public = True


def execute(command, user, bot):
    attachment = None
    response = "Your name is <@{}>! Did you forget or something?".format(user)

    return response, attachment
