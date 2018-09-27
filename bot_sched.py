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

    def __init__(self):
        self.sched = {}

