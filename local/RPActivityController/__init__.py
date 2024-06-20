from .activities import Activity, ActivitiesManager, UpdateInfo
from .rp_apps_controller import RPAppsController


class RichPresenceActivityController:
    activities_manager = NotImplemented
    rpapps_controller = NotImplemented

    def set_activities_manager(self, activities_manager):
        self.activities_manager = activities_manager

    def set_rpapps_controller(self, rpapps_controller):
        self.rpapps_controller = rpapps_controller

    def process_raw_data(self, data):
        activity_info = self.activities_manager.activity_handle(activity_name=data['activity'],
                                                                method=data['method'],
                                                                info=data['info'], )
        self.rpapps_controller.change_state(activity_info)
