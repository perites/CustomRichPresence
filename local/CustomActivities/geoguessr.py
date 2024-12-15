import sys

from .logger import logger

try:
    from rpac import Activity, UpdateInfo

except Exception as exception:
    logger.exception(f"Failed to load external modules, exiting")
    sys.exit(1)


class GeoguessrActivity(Activity):
    activity_name = "Geoguessr"
    main_rp_app_name = "geoguessr"

    clear_delay_seconds = 20

    max_seconds_after = {"clear": 60 * 20,
                         "update": None}

    def __init__(self, priority):
        super().__init__(priority)

    def _handle_update(self, page_info):
        if page_info['status'] == "started":
            return True, UpdateInfo(
                start=self.get_start_time(),
                details="---",
                state="---",
            )
        else:
            return False, None

    def _handle_clean(self, page_info):
        if page_info['status'] == "finished":
            return True, None
        else:
            return False, None
