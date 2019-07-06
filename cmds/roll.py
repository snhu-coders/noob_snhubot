import re
import random
import json

command = "roll"
public = True

def execute(command, user, bot):    
    bot_id = bot.id

    ROLL_REGEX = "^([1-9][0-9]{0,2})d([1-9][0-9]{0,2})(([+-])(\d+))?$"
    roll = command.split()

    attachment = None
    response = "That roll is not valid. Try `<@{}> roll help`".format(bot_id)

    if len(roll) > 1:
        roll = command.split()[1]
        
        if roll.lower().startswith("help"):
            # PEP8 style for long strings
            response = ("Let me show you how I roll:\n`roll XdY[±Z]` "
                "rolls X number of Y-Sided dice with an optional positive or "
                "negative Z modifier.\n"
                "Examples:\n`"
                "<@{0}> roll 2d6`\n`<@{0}> roll 1d10+3`\n`<@{0}> roll 20d4-5`"
                ).format(bot_id)
        else:
            match = re.match(ROLL_REGEX, roll)

            if match is not None:
                rolls = []
                num_dice = int(match.groups()[0])
                pips = int(match.groups()[1])            

                for x in range(num_dice):
                    rolls.append(random.randint(1, pips))

                total = sum(rolls)
                
                if match.groups()[2] is not None:
                    mod = int(match.groups()[4])

                    if match.groups()[3] == "+":
                        total += mod
                    else:
                        total -= mod            
                
                response = None
                attachment = json.dumps([
                    {
                        "text":"<@{}> rolled *{}*".format(user, total),
                        "fields":[
                            {
                                "title":"Roll",
                                "value":"{}".format(match.group()),
                                "short":"true"
                            },
                            {
                                "title":"Values",
                                "value":"{}".format(" ".join(str(roll) for roll in rolls)),
                                "short":"true"
                            },
                            {
                                "title":"Modifier",
                                "value":"{}".format(match.groups()[2]),
                                "short":"true"
                            }
                        ],
                        "color":"good"
                    }
                ])

    return response, attachment
