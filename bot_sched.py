import threading
import sched
import time
import datetime

class Scheduler:
    """
    Maintains the scheduled processes for the bot application
    """

    def has_task(self, task) -> bool:
        """
        Returns true or false if the a task is currently scheduled
        """    
        return any([task in v['arguments'] for v in self.sched.values()])    

    def cleanup_sched(self):
        """
        Removes expired events when their threds become inactive
        """
        sched = list(self.sched.items())

        for k, v in sched:
            if not v['thread'].is_alive():
                self.sched.pop(k, None)

    def add_task(self, id, thread, time, function, arguments):
        """
        Add a scheduled task to the scheduler
        """
        self.sched[id] = {
            'thread': thread,
            'time': time,
            'function': function,
            'arguments': arguments
        }

    def schedule_cmd(self, command, channel, sched_time, function, user_id, event_type='message'):
        """
        Scheduled a bot command for execution at a specific time
        """

        s = sched.scheduler(time.time, datetime.timedelta)

        now_time = datetime.datetime.now().time()
        sched_date = datetime.date.today()

        if now_time > sched_time:
            sched_date += datetime.timedelta(days=1)

        sched_combine = datetime.datetime.combine(sched_date, sched_time)

        # Add the task to the scheduler
        task = s.enterabs(
            sched_combine.timestamp(), 
            1, 
            function,
            (command, channel, user_id, event_type)
        )

        # Spawn a thread daemon to handle the task
        t = threading.Thread(target=s.run)
        t.daemon = True
        t.start()

        # Add task to SCHED
        self.add_task(t.ident, t, task.time, task.action.__name__, task.argument)

        print(task) 
        
    def __init__(self):
        self.sched = {}

