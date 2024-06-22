import threading
import time

from .logger import logger

try:
    from Activity import ActivityInfo
except Exception as exception:
    logger.exception(f"Failed to load external modules, exiting")


class DelayManager:
    target_function: callable = NotImplemented

    ignore_activity_info = ActivityInfo(
        method="ignore",

        name="DelayThread",
        priority=-1,
        delay=-1,
        app_name="-"
    )

    def __init__(self):
        self.active_thread = None

    def set_target_function(self, target_function):
        self.target_function = target_function

    def process_activity_info(self, activity_info):
        if activity_info.method == "clear" and activity_info.delay:
            if self.active_thread:
                logger.warning("Clearing thread already running, ignoring")
                return self.ignore_activity_info

            self.active_thread = DelayThread(run_time=activity_info.delay,
                                             target_function=self.target_function,
                                             target_activity_info=activity_info,
                                             stop_thread=threading.Event())

            self.active_thread.start()
            logger.debug("Delay thread started")
            return self.ignore_activity_info

        if activity_info.method == "update" and self.active_thread:
            self.active_thread.stop_thread.set()
            self.active_thread = None
            logger.debug("Sending new update activity info, thread stopped")

        return activity_info


class DelayThread(threading.Thread):
    def __init__(self, run_time, target_function, target_activity_info, stop_thread):
        super().__init__()
        self.run_time = run_time
        self.target_function = target_function
        self.target_activity_info = target_activity_info
        self.stop_thread = stop_thread

    def run(self):
        try:
            start_time = time.time()
            while time.time() - start_time < self.run_time:
                if self.stop_thread.is_set():
                    logger.debug("Stopping thread as stop flag is set.")
                    return
                time.sleep(2)

            logger.info("Thread finished after the specified run time.")
            self.target_function(self.target_activity_info)

        except Exception as e:
            logger.critical(f"Exception raised while running thread")
            logger.exception(e)
