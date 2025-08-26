import logging
import sys
from config import Config
from scheduler import CollectorScheduler

def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level.upper())
    handler = logging.StreamHandler(sys.stdout)
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    root.addHandler(handler)

def main() -> None:
    setup_logging()
    config = Config()
    scheduler = CollectorScheduler(config)
    scheduler.start(interval_minutes=1)

if __name__ == "__main__":
    main()
