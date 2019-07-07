import threading
import sched
import time
import datetime

from croniter import croniter
from .Output import output


class Scheduler:

    def __init__(self, config=None):
        """
        Maintains the scheduled tasks for the bot

        Args:
            config (dict): Configuration containing tasks to schedule
        """
        self.CONFIG = config
        self.schedule = {}

    def get_num_of_tasks(self):
        """
        Returns: Length of schedule

        """
        return len(self.schedule)

    def has_task(self, task, sched_time=None):
        """
        Returns true or false if the a task is currently scheduled

        """            
        if sched_time:
            return any([task in v['arguments'] and sched_time == v['time'] for v in self.schedule.values()])

        return any([task in v['arguments'] for v in self.schedule.values()])

    def cleanup_sched(self):
        """
        Removes expired events from the schedule when their threads become inactive

        """

        schedule = list(self.schedule.items())

        for k, v in schedule:
            if datetime.datetime.now().timestamp() >= v['time']:

                if not v['thread'].is_alive():
                    self.schedule.pop(k, None)

                    output("Scheduled Tasks: {}".format(self.get_num_of_tasks()))

    def add_task(self, id, thread, time, function, arguments):
        """
        Add a scheduled task to the scheduler dictionary

        Args:
            id (int): Thread identifier
            thread (threading.Thread): Reference to the thread object
            time (float): Timestamp representation of when to execute the command
            function (function): Reference to function used to process the command (usually Bot.handle_scheduled_cmd)
            arguments (tuple): Arguments that were passed to the thread

        """
        self.schedule[id] = {
            'thread': thread,
            'time': time,
            'function': function,
            'arguments': arguments
        }

        output("Scheduled Tasks: {}".format(self.get_num_of_tasks()))

    def schedule_cmd(self, command, channel, sched_time, function, user_id, event_type='message', args=None):
        """
        Creates a thread to execute a bot command at a specific time.

        Args:
            command (str): Name of the command to be executed
            channel (str): Slack Channel ID to execute the command in
            sched_time (float): Timestamp representation of when to execute the command
            function (function): Reference to function used to process the command (usually Bot.handle_scheduled_cmd)
            user_id (str): Slack User ID to use when executing the command (usually the ID of the Bot)
            event_type (str): Slack event type (default: "message")
            args (str): Argumnets to be appended to the command when executed
                (i.e. The "roll" command takes a valid die roll as an argument. "1d20" could be passed here

        """
        s = sched.scheduler(time.time, datetime.timedelta)

        # Add the task to the scheduler
        task = s.enterabs(
            sched_time,
            1, 
            function,
            (command, channel, user_id, event_type, args)
        )

        # Spawn a thread daemon to handle the task
        t = threading.Thread(target=s.run)
        t.daemon = True
        t.start()

        # Add task to SCHED
        self.add_task(t.ident, t, task.time, task.action.__name__, task.argument)

        print(task)

    def process_schedule(self, bot_id, bot_commands, schedule_function, schedule_delay=600):
        """
        Read active configuration for Scheduler, determine next run iteration,
        and created the scheduled command as necessary within the allotted schedule_delay time period.

        Args:
            bot_id (str): The ID of the bot to be passed to the scheduled command as the "user".
            bot_commands (list): List of command values, for validation of config file.
            schedule_function (function): Function to be called by the scheduled task.
            schedule_delay (int): Time, in seconds, before a scheduled task time to spawn a scheduled task thread

        """
        if self.CONFIG:
            for cmd in self.CONFIG.keys():
                if cmd in bot_commands:
                    cmd_data = self.CONFIG.get(cmd)

                    cmd_time = croniter(cmd_data.get("schedule"))
                    next_run = cmd_time.get_next()
                    now = datetime.datetime.now()

                    # if within the schedule_delay time period
                    if datetime.timedelta(seconds=schedule_delay) >= datetime.datetime.fromtimestamp(next_run) - now:
                        # if not already scheduled
                        if not self.has_task(cmd, next_run):
                            self.schedule_cmd(cmd, cmd_data.get("channel"), next_run, schedule_function,
                                              bot_id, args=cmd_data.get("args"))
                else:
                    output("No command found for: {}".format(cmd))
