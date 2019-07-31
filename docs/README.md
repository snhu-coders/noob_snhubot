# Noob SNHUbot

[![Build Status](https://travis-ci.com/gsfellis/noob_snhubot.svg?branch=noob_snhubot_2.0)](https://travis-ci.com/gsfellis/noob_snhubot)

A simple Slack bot written in Python for the [snhu_coders](https://snhu_coders.slack.com) Slack workgroup. It's a fun 
side project for me and I welcome anyone interested to participate. Contact me on Slack or open an issue if you'd like 
to see an enhancement to the bot.

## Getting Started

To get started, [fork](https://help.github.com/en/articles/fork-a-repo) this repository to your own account. From there, 
[clone](https://help.github.com/en/articles/cloning-a-repository) your repository to your workstation and begin making 
changes. Follow the instructions in the links provided for more details.

### Python Version

The production environment runs `Python 3.6.7`. Keep this in mind while developing as some features from later versions 
may not be available in production.

### Installing

It's recommended to use a virtual environment when working on this project to separate the requirements and avoid 
conflicts you may have with other projects.

I've used the [venv](https://docs.python.org/3/library/venv.html) module on `Windows 10` for my own development 
environment, but other methods like [virtualenv](https://virtualenv.pypa.io/en/latest/) should suffice.

Once you're setup, update your `pip` version and install the packages in the `requirements.txt` file into your 
environment:

```bash
pip install -r requirements.txt
```

## Contributing

Be sure to check out our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for 
submitting pull requests to us.

## Current State

Noob SNHUbot loads a series of commands and can execute them when prompted by a user through the Slack channel.  It only 
utilizes the Slack Client [RTM API](https://api.slack.com/rtm). The [Events](https://api.slack.com/events) and 
[Web](https://api.slack.com/web) APIs have not been utilized, but may be implemented at a later time.

## Functionality

Noob SNHUbot will respond to the following direct messages. To begin a conversation, start a message in the channel 
with `@Noob SNHUbot`:

* catalog
  * Uses SNHU Course Catalog Data to fetch details about course subjects and course IDs.
  * catalog `subject` returns a list of Course IDs for the given subject:
    * `catalog Computer Science`
  * catalog `courseID` will return an attachment with catalog data for the course:
    * `catalog CS499`
  * catalog `courseID1 courseID2 courseID3` will return attachments for up to three course IDs.
  * Acceptable formats for course ID are: `ABC-123`, `ABC 123`, or `ABC123`, case insensitive.
* channels
  * Displays a detailed list of channels in the Slack workgroup.
* help
  * Shows a list of known commands.
* it140
  * Gives links to tutorial videos pertaining to course material in IT-140.
  * Requires secondary command to indicate desired topic: `@Noob SNHUbot it140 topic`.
    * Calling the command with no topic, `@Noob SNHUbot it140`, gives a help list with valid topics.
  * Valid secondary commands are:
    * `basics`: gives video links pertaining to Python basics.
    * `dicts`: gives video links pertaining to Python dictionaries.
    * `files`: gives video links pertaining to Python file handling.
    * `functions`: gives video links pertaining to Python functions.
    * `lists`: gives video links pertaining to Python lists.
    * `project`: gives video links pertaining to the various script projects in IT-140.
    * `regex`: gives video links pertaining to regular expressions in Python. 
* packtbook
  * Reaches out to the Packtbook Website to display the latest free book of the day.
  * Automatically scheduled to launch at 8:30PM Eastern Time.
  * Supports secondary `request` command:
    * Enabled by adding a `book_requests` section to the mongo configuration as seen below.  Requests can be disabled independently of mongo by simply omitting `book_requests`.
    * `@Noob SNHUbot packtbook request [list, of, words, here]` adds request words for the requsting user.
    * `@Noob SNHUbot packtbook request (-d/--delete) [list, of, words, here]` deletes the given word(s) from the user's requests.
    * `@Noob SNHUbot packtbook request (-c/--clear)` clears all of the user's requests.
    * `@Noob SNHUbot packtbook request --justforfun` prints out an ugly list of all of the current requests.
  * If requests are enabled in the configuration, users are tagged when books are posted if words in the book's title match a user's request words.
* roll `XdY[±Z]`
  * Rolls X number of Y-Sided dice with a + or - Z modifier!
  * Invalid rolls will respond with _"That roll is not valid. Try `@Noob SNHUbot roll help`"_
  * `roll help` will respond with a help message that explains the syntax with examples
  * Valid rolls respond with a Slack [Attachment](https://api.slack.com/docs/message-attachments) message indicated the 
  total value of the roll, what roll is operated on, individual roll values, and the modifier applied
* what is the airspeed velocity of an unladen swallow?
  * A clever joke.
  * Responds with a Youtube video to a Monty Python and the Holy Grail clip.
* what's my name?
  * Simple call and response.
  * Responds with: _"Your name is `<@{name}>`! Did you forget or something?"_

## Modular Commands

Commands are now modular! Command scripts are stored in the `cmds` module.  When loaded, the module
will dynamically load all commands and store them in a series of lists depending on their public flag.
In order to use them, the command script must follow these strict guidelines:

* `command` variable
  * The `command` variable must be defined. It is used to identify the command trigger for the bot.
* `public` variable
  * Boolean value if the command should be publicly callable by users or privately used internally by the bot itself.
* `execute(command, user, bot)`
  * The `execute()` function must be defined with `command`, `user`, and `bot` parameters so the bot can call the 
  command.
    * `bot` was added so the command can make references to the bot, such as the bot's `id`, which was pretty common. 
  * The `execute()` function must return `response` and `attachment`. These can be set to `None`.

### Command Module Example

```python
command = "test"
public = True

def execute(command, user, bot):
    attachment = None
    response = "This is just an example."

    return response, attachment
```

## Configuration

The preferred method to configure the bot is now YAML. Configuration files can be created and passed as arguments
when launching the application (see next section).

Sample `app.yml`:
```yaml
bot_name:       "Noob SNHUbot"
mail_user:     "example@example.com"
mail_pass:     "SUPER_SECRET_PASSWORD"
smtp_address:   "smtp.gmail.com"
smtp_port:      465
admin_emails:   ['example@example.com']
```

Sample `slack.yml`:

```yaml
token: xoxb-123456789012-aBcDeFgHiJkLmNoPqRsTuVwXyZ  
```

Sample `mongo.yml`:

```yaml  
db: my_database
collections:
  conn: conn_log
  cmds: cmd_log
  book_requests: book_requests
hostname: my_db_server
port: 27017
```

## Launching the Bot

With decoupling the Bot, Slack and Mongo tasks, the primary script, `noob_snhubot.py`, contains only that which it needs 
to process the primary loop.  Optional command line arguments have been added with the use of the `argparse` library.

```bash
usage: noob_snhubot.py [-h] [-a APP_CONFIG] [-m MONGO_CONFIG]
                       [-c SCHED_CONFIG] [-d DELAY]
                       [-s SLACK_CONFIG | -e SLACK_ENV_VARIABLE]

Launch the Noob SNHUBot application.

optional arguments:
  -h, --help            show this help message and exit
  -a APP_CONFIG, --app_config APP_CONFIG
                        Relative path to Bot Application configuration file.
  -m MONGO_CONFIG, --mongo_config MONGO_CONFIG
                        Relative path to Mongo Database configuration file.
  -c SCHED_CONFIG, --sched_config SCHED_CONFIG
                        Relative path to Scheduler Configuration file.
  -d DELAY, --delay DELAY
                        Sets the delay between RTM reads.
  -s SLACK_CONFIG, --slack_config SLACK_CONFIG
                        Relative path to Slack configuration file.
  -e SLACK_ENV_VARIABLE, --slack_env_variable SLACK_ENV_VARIABLE
                        Environment variable holding the Slack client token.
```

### Examples command execution

```bash
python noob_snhubot.py --app_config config\app.yml --slack_config config\slack.yml --mongo_config config\mongo.yml
python noob_snhubot.py -a config\app.yml -s config\slack.yml -m config\mongo.yml

python noob_snhubot.py -a config\app.yml

python noob_snhubot.py -s config\slack.yml

python noob_snhubot.py -e SLACK_ENV_VARIABLE

python noob_snhubot.py -c config\schedule.yml

python noob_snhubot.py -d 5

python noob_snhubot.py --help
```

## Scheduled Commands

It's here! (No, seriously, I finally did it).

The Scheduler has been greatly improved for Noob_SNHUbot 2.0. It now uses a YAML config file (explained below), 
passed to the primary script. Threads will be spun up `10` minutes before a scheduled task, so no more threads hanging 
around idle forever. Additionally, `schedule` cleanup will only occur after the time for a scheduled task has passed, 
reducing the number of calls to a threads `is_active()` method.

### Scheduler YAML config

The configuration is a series of YAML dictionaries (mappings). Each command to be setup in the scheduler should be the 
top-level `key`, and then within that will be three additional mappings `args`, `channel`, and `schedule`.
 - `args` represents additional data passed to the command.
   - For example, the `roll` command takes a dice roll to process, so something like "1d20" can be passed into `args`,
   otherwise, simply leave blank `""`
 - `channel` is the Slack Channel ID that the command output will be sent to. This can be retrieved from the a browser's
 address bar when viewing the Slack channel.
 - `schedule` follows standard `cron` expression time, and will be processed by 
 the [`croniter`](https://pypi.org/project/croniter/) library to schedule the command.
   - Basic `cron` syntax is as follows:
```
 ┌───────────── minute (0 - 59)
 │ ┌───────────── hour (0 - 23)
 │ │ ┌───────────── day of the month (1 - 31)
 │ │ │ ┌───────────── month (1 - 12)
 │ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday;
 │ │ │ │ │                                   7 is also Sunday on some systems)
 │ │ │ │ │
 │ │ │ │ │
"* * * * *"   <= String representation of cron schedule
```
 - The `packtbook` schedule, which runs each day at 8:30pm, would be `"30 20 * * *"`
 - See the [`cron Wikipedia page`]((https://en.wikipedia.org/wiki/Cron)) for more details on `cron` scheduling
 
 Sample `schedule.yml`:
 
```yaml
"packtbook":
  args:       ""
  channel:    "ABCD12345"  
  schedule:   "30 20 * * *"
  
"roll":
  args:       "1d20"
  channel:    "ABCD12345"  
  schedule:   "0 1 27 10 *"  
```
