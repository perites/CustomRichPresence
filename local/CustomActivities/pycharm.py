import sys

from .logger import logger

try:
    from rpac import Activity, UpdateInfo
except Exception as exception:
    logger.exception(f"Failed to load external modules, exiting")
    sys.exit(1)


class PyCharmActivity(Activity):
    activity_name = "PyCharm"
    main_rp_app_name = "test"
    clear_delay_seconds = 60

    def __init__(self, priority):
        super().__init__(priority)

    def _handle_update(self, page_info):
        return True, UpdateInfo(
            details="programming in python",
            state=f"PYTHON",
        )

    def _handle_clean(self, page_info):
        return True, None
