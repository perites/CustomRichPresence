import sys

from .activities import Activity, ActivitiesManager, UpdateInfo
from .rp_apps_controller import RPAppsController
from .delay_thread import DelayManager
from .logger import logger


class RichPresenceActivitiesController:
    activities_manager = NotImplemented
    rpapps_controller = NotImplemented
    delay_manager = DelayManager()

    def set_activities_manager(self, activities_manager):
        if not isinstance(activities_manager, ActivitiesManager):
            logger.error("activity_manager must be of type ActivitiesManager")
            sys.exit(1)
        self.activities_manager = activities_manager

    def set_rpapps_controller(self, rpapps_controller):
        if not isinstance(rpapps_controller, RPAppsController):
            logger.error("rpapps_controller must be of type RPAppsController")
            sys.exit(1)
        self.rpapps_controller = rpapps_controller

        self.delay_manager.set_target_function(self.rpapps_controller.change_state)

    def process_raw_data(self, data):
        activity_info = self.activities_manager.activity_handle(activity_name=data['activity'],
                                                                method=data['method'],
                                                                info=data['info'], )

        activity_info = self.delay_manager.process_activity_info(activity_info)

        self.rpapps_controller.change_state(activity_info)
