import sys
import logging

import json
import struct
import urllib.parse

from dataclasses import dataclass

try:
    from pypresence import Presence
    from mal import Anime
except Exception as e:
    logging.error(f"Failed to load external modules, exiting | Exception:{e} ")
    sys.exit(1)


class NativeMessagesToRPS:
    activities_manager = NotImplemented
    rpapps_controller = NotImplemented

    def set_activities_manager(self, activities_manager):
        self.activities_manager = activities_manager

    def set_rpapps_controller(self, rpapps_controller):
        self.rpapps_controller = rpapps_controller

    @staticmethod
    def get_native_message():
        raw_length = sys.stdin.buffer.read(4)
        if len(raw_length) == 0:
            sys.exit(0)
        message_length = struct.unpack("@I", raw_length)[0]
        message = sys.stdin.buffer.read(message_length).decode("utf-8")
        return json.loads(message)

    def start_loop(self):
        logging.info('\nStarting native_messaging_host')
        while True:
            try:
                json_data = self.get_native_message()
                logging.debug(f"Data parsed: {json_data}")

                activity_info = self.activities_manager.activity_handle(activity_name=json_data['activity'],
                                                                        method=json_data['method'],
                                                                        info=json_data['info'], )

                self.rpapps_controller.change_state(activity_info)

            except Exception as e:
                logging.error(f"Error in main loop | Exception: {e}")


class RPAppsController:
    def __init__(self, apps):
        try:
            self.apps = {name: Presence(app_id) for name, app_id in apps.items()}
        except Exception as e:
            logging.error(
                "Exception while initializing RPAppsController, couldn`t made Presence object, most likely wrong ID")
            logging.error(e)

        self.connected_rp_app_name = None
        self.previous_activity_info = None

    def change_state(self, activity_info):
        if self.previous_activity_info == activity_info:
            logging.info("New data identical to previous, no changes done")
            return

        match activity_info.method:
            case "update":
                if not self.connected_rp_app_name:
                    self.apps[activity_info.app_name].connect()
                    self.connected_rp_app_name = activity_info.app_name
                    logging.debug(f"First connection,  to app : {self.connected_rp_app_name}")

                elif not (self.connected_rp_app_name == activity_info.app_name):
                    self.apps[self.connected_rp_app_name].close()
                    logging.debug(f"Disconnected from app : {self.connected_rp_app_name}")

                    self.apps[activity_info.app_name].connect()
                    self.connected_rp_app_name = activity_info.app_name
                    logging.debug(f"Connected to app : {self.connected_rp_app_name}")

                self.apps[self.connected_rp_app_name].update(**activity_info.data.__dict__)
                logging.info(f"Updated RP for app : {self.connected_rp_app_name}")

            case "clear":
                if not (self.connected_rp_app_name == activity_info.app_name):
                    logging.warning(
                        f"App that need to be cleared is NOT connected | App name : {activity_info.app_name}")
                    return
                self.apps[self.connected_rp_app_name].clear()
                self.previous_activity_info = None
                logging.info(f"Cleared RP for app : {self.connected_rp_app_name}")

            case "ignore":
                logging.debug("Got 'ignore' method, no changes done")
                return

            case _:
                logging.warning(f"Wrong method in state info | Method : {activity_info.method}")
                return

        self.previous_activity_info = activity_info


@dataclass(frozen=True)
class UpdateInfo:
    details: str
    state: str

    start: int = None
    party_size: list = None

    large_image: str = None
    large_text: str = None

    buttons: list[dict] = None


@dataclass(frozen=True)
class ActivityInfo:
    app_name: str
    method: str
    activity_priority: int
    # max_stays_idle
    data: UpdateInfo = None


class ActivitiesManager:
    current_activity_info = None

    ignore_activity_info = ActivityInfo(
        app_name="ActivitiesManager",
        method="ignore",
        activity_priority=-1,
    )

    # last_updated_at : datetime
    # thread check_last_apdated | while las_updated+current_activity_max_idle minute > now()
    def __init__(self, *raw_activities):
        self.activities = self.set_activities(*raw_activities)

    @staticmethod
    def set_activities(*raw_activities):
        activities = {}

        used_priorities = []
        for activity in raw_activities:
            if not isinstance(activity, Activity):
                logging.error(f"ActivitiesManager set wrong type: {type(activity)} | Must be an Activity")
                sys.exit(1)
            try:
                int(activity.priority)
            except ValueError:
                logging.error(f"Priority must be an integer")
                sys.exit(1)

            if activity.priority in used_priorities:
                logging.error(
                    f"Activities manager already has priority {activity.priority}, Activity priority must be unique")
                sys.exit(1)

            used_priorities.append(activity.priority)
            activities[activity.activity_name] = activity

        logging.debug(f"Activities manager initialized with {len(activities)} activities")
        return activities

    def activity_handle(self, activity_name, method, info) -> ActivityInfo:
        new_activity_info = self.activities[activity_name].handle(method, info)

        result = self.process_activity_info(new_activity_info)
        return result

    def process_activity_info(self, activity_info) -> ActivityInfo:
        match activity_info.method:
            case "ignore":
                logging.debug("Got activity method 'ignore', proceed")
                response_activity_info = activity_info

            case "update":
                if not self.current_activity_info:
                    self.current_activity_info = activity_info
                    response_activity_info = activity_info

                    logging.debug("No current activity info, set new")

                elif activity_info.activity_priority <= self.current_activity_info.activity_priority:
                    self.current_activity_info = activity_info
                    response_activity_info = activity_info

                    logging.debug(
                        f"New activity has higher priority, updating current activity | activity_info : {activity_info}")

                else:
                    response_activity_info = self.ignore_activity_info
                    logging.debug("New activity info doesn't have higher priority, ignoring")

            case "clear":
                if not self.current_activity_info:
                    logging.warning("Attempt to clear, but no active activity, ignoring")
                    response_activity_info = self.ignore_activity_info

                elif activity_info.activity_priority == self.current_activity_info.activity_priority:
                    self.current_activity_info = None
                    response_activity_info = activity_info
                    logging.debug("Clearing current activity")

                else:
                    response_activity_info = self.ignore_activity_info
                    logging.debug("Can`t clear activity which is not current, ignoring")

            case _:
                response_activity_info = self.ignore_activity_info
                logging.warning(
                    f"Wrong method in activity info, sent ignore_activity_info | Method : {activity_info.method}")

        return response_activity_info


class Activity:
    activity_name = NotImplemented
    start_stays_minutes = NotImplemented
    max_idle_minutes = NotImplemented
    main_rp_app_name = NotImplemented

    def __init__(self, priority=0):
        self.priority = priority

        self.started_at = None
        self.last_clean_call = None
        self.last_update_call = None

        self.handled_methods = {"clear": self._handle_clean,
                                "update": self._handle_update}

    def handle(self, method, data) -> ActivityInfo:
        logging.debug(f"Need to handle method : {method}")
        try:
            success, data = self.handled_methods[method](data)

            return ActivityInfo(
                activity_priority=self.priority,
                app_name=self.main_rp_app_name,

                method=method if success else "ignore",
                data=data
            )
        except Exception as e:
            logging.error(f"Exception while handling method : {method} | Exception : {e}")

    def _handle_update(self, data) -> (bool, UpdateInfo):
        raise NotImplementedError

    def _handle_clean(self, data) -> (bool, None):
        raise NotImplementedError


class WatchingAnimeJoyActivity(Activity):
    activity_name = "WatchingAnimeJoy"
    main_rp_app_name = "watching"

    def __init__(self, priority=0):
        super().__init__(priority)
        self.current_title = None

    def _handle_update(self, page_info):
        if (not isinstance(self.current_title, Title) or
                self.current_title.mal_title_id != page_info['mal_title_id']):
            self.current_title = Title(page_info['mal_title_id'], page_info['title_name'], page_info['current_episode'])
            logging.debug(f'Created new Title with page_info : {page_info}')

        elif self.current_title.current_episode != page_info['current_episode']:
            self.current_title.current_episode = page_info['current_episode']
            logging.debug(f'Updated Title current_episode: {page_info}')

        # else:
        #     logging.warning("No changes detected in page_info, returning False")
        #     return False

        return True, UpdateInfo(
            details=self.current_title.title_name,
            state=f"{self.current_title.media_type}, episode",
            party_size=[self.current_title.current_episode, self.current_title.episodes_amount],
            large_image=self.current_title.poster_url,
            large_text="Poster",
            buttons=[{"label": "Page on MAL", "url": self.current_title.url_to_mal},
                     {"label": "Progress", "url": self.current_title.url_to_progress},
                     ]
        )

    def _handle_clean(self, page_info):
        if not self.current_title or page_info['mal_title_id'] != self.current_title.mal_title_id:
            logging.warning("Was not cleaned, current_title and title to clean are not the same")
            return False, None

        self.current_title = None
        logging.debug(f"Clean method called on {self.main_rp_app_name}, current_title became None")
        return True, None


@dataclass()
class Title:
    mal_title_id: int
    raw_title_name: str = ""
    current_episode: int = -1

    def __post_init__(self):
        self.mal_title = Anime(self.mal_title_id)
        self.title_name = self.mal_title.title_english or self.mal_title.title

        self.episodes_amount = self.mal_title.episodes

        self.poster_url = self.mal_title.image_url
        self.media_type = self.mal_title.type

        self.url_to_mal = self.mal_title.url
        self.url_to_progress = f"https://myanimelist.net/animelist/perite?s={urllib.parse.quote(self.title_name or self.raw_title_name)}"


class WatchingYoutubeActivity(Activity):
    activity_name = "WatchingYoutube"
    main_rp_app_name = "test"

    def __init__(self, priority=0):
        super().__init__(priority)

    def _handle_update(self, page_info):
        return True, UpdateInfo(
            details="watching_youtube",
            state=f"videos",
        )

    def _handle_clean(self, page_info):
        return True, None
