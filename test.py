import cmds

commands = list(cmds.COMMANDS.values())
commands.sort()
print(commands)

command = "do"
user = "test"


for k, v in cmds.COMMANDS.items():        
    if command.lower().startswith(v):
        sub = getattr(cmds, k)
        cmd = getattr(sub, 'execute')
        response, attachment = cmd(command, user)

if attachment:
    print(attachment)
else:
    print(response)
