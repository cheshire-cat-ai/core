from pytz import utc
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from cat.log import log

from cat.utils import singleton

# I'm late, I'm late, for a very important date!
@singleton
class WhiteRabbit:
    """ The WhiteRabbit
    
    Here the cron magic happens
    
    """
    
    def __init__(self):
        log.info("Initializing WhiteRabbit...")
        
        # Where the jobs are stored. We can also use an external db to have persistency
        jobstores = {
            'default': MemoryJobStore()
        }
        
        # Define execution pools
        executors = {
            'default': ThreadPoolExecutor(20),
            'processpool': ProcessPoolExecutor(5)
        }
        
        # Define basic rules for jobs
        job_defaults = {
            'coalesce': False,
            'max_instances': 10
        }

        # Creating the effective scheduler
        self.scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
        
        log.info("Starting scheduler")
        
        # Start the scheduler
        try:
            self.scheduler.start()
            log.info("Scheduler started")
        except e:
            log.error("Error during scheduler start: ", e)
            
        
    def schedule_chat_message(self, content: str, cat, days=0, hours=0, minutes=0, seconds=0, milliseconds=0, microseconds=0):
        """
        Schedule a chat message
        
        Parameters
        ----------
        content: str
            The message to be sent.
        cat: StrayCat
            Stray Cat instance.
        days: int
            Days to wait.
        hours: int
            Hours to wait.
        minutes: int
            Minutes to wait.
        seconds: int
            Seconds to wait.
        milliseconds: int
            Milliseconds to wait.
        microseconds: int
            Microseconds to wait.
        """
        
        # Calculate time
        schedule = datetime.today() + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds, microseconds=microseconds)
        
        # Schedule the job
        self.scheduler.add_job(cat.send_ws_message, 'date', run_date=schedule, kwargs={'content': content, 'msg_type': 'chat'})