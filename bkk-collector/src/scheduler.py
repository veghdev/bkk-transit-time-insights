import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config import Config
from bkk_client import BkkClient
from db_client import DBHandler

logger = logging.getLogger(__name__)

class CollectorScheduler:
    def __init__(self, config: Config):
        self.config = config
        self.client = BkkClient(config)
        self.scheduler = BackgroundScheduler(timezone=config.TZ)

    def start(self, interval_minutes: int = 1):
        with DBHandler(self.config) as db:
            self.db = db
            for route_id in self.config.ROUTE_IDS:
                self.scheduler.add_job(
                    func=lambda rid=route_id: self._run_job_safe(rid),
                    trigger=IntervalTrigger(minutes=interval_minutes),
                    id=f"collector_job_{route_id}",
                    replace_existing=True,
                    max_instances=1,
                    coalesce=True,
                )
                self._run_job_safe(route_id)

            self.scheduler.start()
            logger.info("Scheduler started. Interval: every %d minute(s)", interval_minutes)

            try:
                import threading
                for t in threading.enumerate():
                    if t is threading.current_thread():
                        continue
                    t.join()
            except KeyboardInterrupt:
                logger.info("Shutting down collector service")

    def _run_job_safe(self, route_id: str) -> None:
        try:
            trips = self.client.fetch_tripupdates(route_id)
            self.db.insert_trips(trips)
            logger.info("Job finished for route %s. Inserted %d trips.", route_id, len(trips))
        except Exception as e:
            logger.exception("Collector job failed for route %s: %s", route_id, e)
