import sys

from .logger import logger

try:
    from Activity import Activity, UpdateInfo
except Exception as exception:
    logger.exception(f"Failed to load external modules, exiting")
    sys.exit(1)


class WatchingYoutubeActivity(Activity):
    activity_name = "WatchingYoutube"
    main_rp_app_name = "watching"
    clear_delay_seconds = 60

    def __init__(self, priority):
        super().__init__(priority)

    def _handle_update(self, page_info):
        return True, UpdateInfo(
            details="watching_youtube",
            state=f"videos",
        )

    def _handle_clean(self, page_info):
        return True, None
