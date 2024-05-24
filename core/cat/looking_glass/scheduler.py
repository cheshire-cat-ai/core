from pytz import utc
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from cat.log import log

from cat.utils import singleton

@singleton
class Scheduler:
    """ The Scheduler
    Here the cron magic happens
    """
    
    def __init__(self):
        log.info("Initializing scheduler...")
        
        jobstores = {
            'default': MemoryJobStore()
        }
        
        executors = {
            'default': ThreadPoolExecutor(20),
            'processpool': ProcessPoolExecutor(5)
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }

        self.scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
        
        log.info("Starting scheduler")
        
        try:
            self.scheduler.start()
            log.info("Scheduler started")
        except e:
            log.error("Error during scheduer start: ", e)
            
        def hello(text):
            log.info(f"Hello from the scheduler: {text}")
            
        schedule = datetime.today() + timedelta(seconds=10)

        self.scheduler.add_job(hello, 'date', run_date=schedule, kwargs={'text': 'prova'})