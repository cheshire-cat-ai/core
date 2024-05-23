from cat.log import log

from cat.utils import singleton

@singleton
class Scheduler:
    """ The Scheduler
    Here the cron magic happens
    """
    
    def __init__(self):
        log.info("Initializing scheduler...")

        self.jobs = ["This", "is", "a", "start"]
        
    def add_job(self, name: str) -> bool:
        self.jobs.append(name)
        return True
        
    def get_jobs(self) -> list[str]:
        return self.jobs