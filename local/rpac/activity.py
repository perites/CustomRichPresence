import sys
import time

from .logger import logger
from .custom_dataclasses import ActivityInfo, UpdateInfo


class Activity:
    activity_name = NotImplemented
    main_rp_app_name = NotImplemented

    clear_delay_seconds = None

    max_seconds_after = {"clear": 2,
                         "update": None}

    def __init__(self, priority):
        self.priority = priority

        self._start_time = None
        self.last_method_call = None
        self.last_method = None

        self.handled_methods = {"clear": self._handle_clean,
                                "update": self._handle_update}

        self.validate_parameters()

    def validate_parameters(self):
        self.clear_delay_seconds = self.validate(self.clear_delay_seconds, 1, "Clear delay")
        self.priority = self.validate(self.priority, 0, "Priority", disable=False)

        for k, v in self.max_seconds_after.items():
            self.validate(v, 1, f"Max_seconds_after[{k}]")

    def validate(self, variable_to_validate, min_value, variable_name, disable=True):
        try:
            if disable and (not variable_to_validate):
                return variable_to_validate

            variable_to_validate = int(variable_to_validate)
            if variable_to_validate <= min_value:
                raise ValueError

            return variable_to_validate
        except Exception as exception:
            disable_str = "Use None to disable it" if disable else ""
            logger.error(
                f"{self.activity_name} : {variable_name} must be an integer and greater than {min_value}. {disable_str}")

            sys.exit(1)

    def handle(self, method, data) -> ActivityInfo:
        logger.debug(f"Need to handle method : {method}")

        success, data = self.handled_methods[method](data)
        if success:
            self.last_method = method
            self.last_method_call = time.time()

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
        return True, None

    def get_start_time(self):
        self.update_start_time()
        return self._start_time

    def update_start_time(self):
        current_time = time.time()

        if not self._start_time:
            self._start_time = current_time
            self.last_method_call = current_time
            self.last_method = "update"
            logger.debug("No started time, set current")

        elif (self.max_seconds_after[self.last_method]) and (
                current_time - self.last_method_call > self.max_seconds_after[self.last_method]):

            self._start_time = current_time
            logger.debug(
                f"Current time has been set as start time, too much time passed since last method '{self.last_method}' call")
