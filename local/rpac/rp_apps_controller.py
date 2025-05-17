import sys

from .logger import logger

try:
    from pypresence import Presence
except (ModuleNotFoundError or ImportError) as exception:
    logger.exception(f"Failed to load pypresence module")
    sys.exit(1)


class RPAppsController:
    def __init__(self, raw_apps):
        try:
            self.apps = {name: Presence(app_id) for name, app_id in raw_apps.items()}
        except Exception as exception:
            logger.exception(
                "Exception while initializing RPAppsController, couldn`t made Presence object, most likely wrong ID")
            sys.exit(1)

        self.connected_rp_app_name = None
        self.previous_activity_info = None

    def change_state(self, activity_info):
        if self.previous_activity_info == activity_info:
            logger.warning("New data identical to previous, no changes done")
            return

        self.previous_activity_info = activity_info

        if (not activity_info.method == "ignore") and (not self.apps.get(activity_info.app_name)):
            logger.error(f"App '{activity_info.app_name}' does not exist")
            sys.exit(1)

        match activity_info.method:
            case "update":
                if not self.connected_rp_app_name:
                    self.apps[activity_info.app_name].connect()
                    self.connected_rp_app_name = activity_info.app_name
                    logger.debug(f"First connection,  to app : {self.connected_rp_app_name}")

                elif not (self.connected_rp_app_name == activity_info.app_name):
                    self.apps[self.connected_rp_app_name].close()
                    logger.debug(f"Disconnected from app : {self.connected_rp_app_name}")

                    self.apps[activity_info.app_name].connect()
                    self.connected_rp_app_name = activity_info.app_name
                    logger.debug(f"Connected to app : {self.connected_rp_app_name}")

                self.apps[self.connected_rp_app_name].update(**activity_info.data.__dict__)
                logger.info(f"Updated RP for app : {self.connected_rp_app_name}")

            case "clear":
                if not (self.connected_rp_app_name == activity_info.app_name):
                    logger.warning(
                        f"App that need to be cleared is NOT connected | App name : {activity_info.app_name}")
                    return
                self.apps[self.connected_rp_app_name].clear()
                # self.previous_activity_info = None
                logger.info(f"Cleared RP for app : {self.connected_rp_app_name}")

            case "ignore":
                logger.debug("Got 'ignore' method, no changes done")
                return
            case _:
                logger.warning(f"Wrong method in state info '{activity_info.method}'")
                return
