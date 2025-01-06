from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from config import MONITOR_WAKE, MONITOR_SLEEP
from scripts.monitor_control import set_monitor_state
from scripts.utils import convert_to_24_hour

scheduler = BackgroundScheduler()


def setup_jobs():
    # Add jobs to the scheduler
    if MONITOR_WAKE:
        monitor_wake_time_24hr = convert_to_24_hour(MONITOR_WAKE)
        wake_hour, wake_minute = map(int, monitor_wake_time_24hr.split(":"))
        scheduler.add_job(
            lambda: set_monitor_state("on_rotate_left"),
            "cron",
            hour=wake_hour,
            minute=wake_minute,
            misfire_grace_time=60,
            id="monitor_on_job",
            replace_existing=True,  # Ensure job replacement on restart
        )

    if MONITOR_SLEEP:
        sleep_time_24hr = convert_to_24_hour(MONITOR_SLEEP)
        sleep_hour, sleep_minute = map(int, sleep_time_24hr.split(":"))
        scheduler.add_job(
            lambda: set_monitor_state("off"),
            "cron",
            hour=sleep_hour,
            minute=sleep_minute,
            misfire_grace_time=60,
            id="monitor_off_job",
            replace_existing=True,  # Ensure job replacement on restart
        )

    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
