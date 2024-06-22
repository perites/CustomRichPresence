import sys

from dataclasses import dataclass, field
from .logger import logger


@dataclass(frozen=True)
class UpdateInfo:
    details: str
    state: str

    start: int = None
    party_size: list[int] = None
    large_image: str = None
    large_text: str = None
    buttons: list[dict[str, str]] = None


@dataclass(frozen=True)
class ActivityInfo:
    method: str

    name: str
    priority: int
    delay: int
    app_name: str

    data: UpdateInfo = None


@dataclass(frozen=False)
class ActivityInfoBuffer:
    _buffer: dict[str, ActivityInfo] = field(default_factory=dict)

    def put(self, activity_info: ActivityInfo):
        self._buffer[activity_info.name] = activity_info

    def find_higher_or_none(self):
        if not self._buffer:
            return

        higher_activity_info = None
        for activity_info in self._buffer.values():
            if not higher_activity_info:
                higher_activity_info = activity_info

            if activity_info.priority >= higher_activity_info.priority:
                higher_activity_info = activity_info

        del self._buffer[higher_activity_info.name]
        return higher_activity_info

    def clear(self, activity_info: ActivityInfo):
        result = self._buffer.pop(activity_info.name, False)
        return result


class ActivitiesManager:
    ignore_activity_info = ActivityInfo(
        method="ignore",

        name="ActivitiesManager",
        priority=-1,
        delay=-1,
        app_name="-"
    )
    activity_info_buffer = ActivityInfoBuffer()

    def __init__(self, *raw_activities):
        self.current_activity_info = None
        self.activities = self.set_activities(*raw_activities)

    @staticmethod
    def set_activities(*raw_activities):
        activities = {}

        for activity in raw_activities:
            if not isinstance(activity, Activity):
                logger.error(f"ActivitiesManager got wrong type: {type(activity)}. Must be Activity type")
                sys.exit(1)
            try:
                int(activity.priority)
            except ValueError:
                logger.error(f"Activity`s priority must be an integer")
                sys.exit(1)

            activities[activity.activity_name] = activity

        logger.debug(f"Activities manager initialized with {len(activities)} activities")
        return activities

    def activity_handle(self, activity_name, method, info) -> ActivityInfo:
        new_activity_info = self.activities[activity_name].handle(method, info)

        result = self.process_activity_info(new_activity_info)
        return result

    def process_activity_info(self, activity_info) -> ActivityInfo:
        match activity_info.method:
            case "ignore":
                logger.debug("Got activity method 'ignore', proceed")
                response_activity_info = activity_info

            case "update":
                if not self.current_activity_info:
                    self.current_activity_info = activity_info
                    response_activity_info = activity_info

                    logger.debug("No current activity info, set new")

                elif activity_info.priority >= self.current_activity_info.priority:
                    logger.debug(
                        f"Updating current activity, activity info has higher or same priority")

                    if self.current_activity_info.name != activity_info.name:
                        self.activity_info_buffer.put(self.current_activity_info)
                        logger.debug("Putting current activity info to buffer")

                    self.current_activity_info = activity_info
                    response_activity_info = activity_info

                else:
                    logger.debug("New activity info has lower priority, putting to buffer and ignoring")
                    self.activity_info_buffer.put(activity_info)
                    response_activity_info = self.ignore_activity_info

            case "clear":
                if not self.current_activity_info:
                    logger.warning("Attempt to clear, but no active activity, ignoring")
                    response_activity_info = self.ignore_activity_info

                elif activity_info.name == self.current_activity_info.name:
                    buffer_activity_info = self.activity_info_buffer.find_higher_or_none()
                    if buffer_activity_info:
                        self.current_activity_info = buffer_activity_info
                        response_activity_info = buffer_activity_info
                        logger.debug("Found activity in _buffer, updating rp with it")

                    else:
                        self.current_activity_info = None
                        response_activity_info = activity_info
                        logger.debug("Clearing current activity, nothing in _buffer")

                else:
                    result = self.activity_info_buffer.clear(activity_info)
                    if result:
                        logger.debug("Activity cleared in buffer")

                    else:
                        logger.debug("Activity not active, not in _buffer, ignoring")

                    response_activity_info = self.ignore_activity_info

            case _:
                response_activity_info = self.ignore_activity_info
                logger.warning(
                    f"Wrong method '{activity_info.method}' in activity info, ignoring")

        return response_activity_info


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
