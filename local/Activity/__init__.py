import sys

from .logger import logger
from .custom_dataclasses import ActivityInfo, UpdateInfo


class Activity:
    activity_name = NotImplemented
    clear_delay_seconds = None
    max_idle_minutes = NotImplemented
    main_rp_app_name = NotImplemented

    def __init__(self, priority):
        self.priority = priority

        self.validate_clear_delay()
        self.started_at = None
        self.last_clean_call = None
        self.last_update_call = None

        self.handled_methods = {"clear": self._handle_clean,
                                "update": self._handle_update}

    def validate_clear_delay(self):
        if self.clear_delay_seconds:
            try:
                int(self.clear_delay_seconds)
            except ValueError:
                logger.error(f"Clear delay must be an integer")
                sys.exit(1)

            if self.clear_delay_seconds < 1:
                logger.error("Clear delay must be greater than one second. Use None to disable delay.")
                sys.exit(1)

    def handle(self, method, data) -> ActivityInfo:
        logger.debug(f"Need to handle method : {method}")

        success, data = self.handled_methods[method](data)

        return ActivityInfo(
            method=method if success else "ignore",

            name=self.activity_name,
            priority=self.priority,
            delay=self.clear_delay_seconds,
            app_name=self.main_rp_app_name,

            data=data
        )

    def _handle_update(self, data) -> (bool, UpdateInfo):
        raise NotImplementedError

    def _handle_clean(self, data) -> (bool, None):
        raise NotImplementedError
