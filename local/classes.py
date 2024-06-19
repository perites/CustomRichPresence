import sys
import logging

import urllib.parse
from dataclasses import dataclass

try:
    from pypresence import Presence
    from mal import Anime
except Exception as e:
    logging.error(f"Failed to load external modules, exiting | Exception:{e} ")
    sys.exit(1)


class RPAppsController:
    def __init__(self, apps):
        try:
            self.apps = {name: Presence(app_id) for name, app_id in apps.items()}
        except Exception as e:
            logging.error(
                "Exception while initializing RPAppsController, couldn`t made Presence object, most likely wrong ID")
            logging.error(e)

        self.connected_rp_app_name = None
        self.previous_data = None

    def change_state(self, state_info):
        if self.previous_data == state_info:
            logging.warning("New data identical to previous, no changes done")
            return

        self.previous_data = state_info

        match state_info.method:
            case "update":
                if not self.connected_rp_app_name:
                    self.apps[state_info.app_name].connect()
                    self.connected_rp_app_name = state_info.app_name
                    logging.debug(f"First connection,  to app : {self.connected_rp_app_name}")

                elif not (self.connected_rp_app_name == state_info.app_name):
                    self.apps[self.connected_rp_app_name].close()
                    logging.debug(f"Disconnected from app : {self.connected_rp_app_name}")

                    self.apps[state_info.app_name].connect()
                    self.connected_rp_app_name = state_info.app_name
                    logging.debug(f"Connected to app : {self.connected_rp_app_name}")

                self.apps[self.connected_rp_app_name].update(**state_info.data.__dict__)
                logging.info(f"Updated RP for app : {self.connected_rp_app_name}")

            case "clear":
                if not (self.connected_rp_app_name == state_info.app_name):
                    logging.warning(f"App that need to be cleared is NOT connected | App name : {state_info.app_name}")
                    return
                self.apps[self.connected_rp_app_name].clear()
                self.previous_data = None
                logging.info(f"Cleared RP for app : {self.connected_rp_app_name}")

            case _:
                logging.warning(f"Wrong method in state info | Method : {state_info.method}")
                return


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

    # last_updated_at : datetime
    # thread check_last_apdated | while las_updated+current_activity_max_idle minute > now()
    def __init__(self, *args):
        self.activities = {activity.activity_name: activity for activity in args}
        # todo check if priorities unique

    def activity_handle(self, activity_name, method, info):
        new_activity_info = self.activities[activity_name].handle(method, info)
        return self.process_new_activity_info(new_activity_info)

    def process_new_activity_info(self, new_activity_info):
        if not new_activity_info:
            logging.debug("No new activity info")
            return False

        if not self.current_activity_info:
            self.current_activity_info = new_activity_info

            logging.debug("No current activity info, set new")
            return self.current_activity_info

        match new_activity_info.method:
            case "update":
                if new_activity_info.activity_priority <= self.current_activity_info.activity_priority:
                    self.current_activity_info = new_activity_info
                    logging.debug(
                        f"New activity has higher priority, updating current activity | activity_info : {new_activity_info}")
                    return new_activity_info
                else:
                    logging.debug("New activity info doesn't have higher priority, doing nothing")
                    return False

            case "clear":
                if new_activity_info.activity_priority == self.current_activity_info.activity_priority:
                    self.current_activity_info = None
                    logging.debug("Current activity and new to clean is same,  info cleared")
                    return new_activity_info
                else:
                    logging.debug("Current activity isn`t new activity, doing nothing")
                    return False

            case _:
                logging.warning(f"Wrong method in state info | Method : {new_activity_info.method}")
                return False


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
        logging.debug(f"Need to handle method : {method} | Data : {data}")
        try:
            return self.handled_methods[method](data)
        except Exception as e:
            logging.error(f"Exception while handling method : {method} | Exception : {e}")

    def _handle_clean(self, data):
        raise NotImplementedError

    def _handle_update(self, data):
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

        return ActivityInfo(
            app_name=self.main_rp_app_name,
            method="update",
            activity_priority=self.priority,
            data=UpdateInfo(
                details=self.current_title.title_name,
                state=f"{self.current_title.media_type}, episode",
                party_size=[self.current_title.current_episode, self.current_title.episodes_amount],
                large_image=self.current_title.poster_url,
                large_text="Poster",
                buttons=[{"label": "Page on MAL", "url": self.current_title.url_to_mal},
                         {"label": "Progress", "url": self.current_title.url_to_progress},
                         ]
            )
        )

    def _handle_clean(self, page_info):
        if not self.current_title or page_info['mal_title_id'] != self.current_title.mal_title_id:
            logging.warning("Was not cleaned, current_title and title to clean are not the same")
            return False

        self.current_title = None
        logging.debug(f"Clean method called on {self.main_rp_app_name}, current_title became None")
        return ActivityInfo(app_name=self.main_rp_app_name,
                            method="clear",
                            activity_priority=self.priority,
                            )


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
    main_rp_app_name = "watching"

    def __init__(self, priority=0):
        super().__init__(priority)

    def _handle_update(self, page_info):
        return ActivityInfo(
            app_name=self.main_rp_app_name,
            method="update",
            activity_priority=int(page_info),
            data=UpdateInfo(
                details="watching_youtube",
                state=f"videos",

            )
        )

    def _handle_clean(self, page_info):
        return ActivityInfo(
            app_name=self.main_rp_app_name,
            method="clear",
            activity_priority=int(page_info),
        )
