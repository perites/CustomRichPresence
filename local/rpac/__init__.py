import threading

from .logger import logger

from .activity import Activity
from .custom_dataclasses import ActivityInfo, UpdateInfo
from .activities_manager import ActivitiesManager
from .rp_apps_controller import RPAppsController
from .delay_manager import DelayManager


class RichPresenceActivitiesController:
    activities_manager = NotImplemented
    rpapps_controller = NotImplemented
    delay_manager = DelayManager()

    def __init__(self, data_queue):
        self.data_queue = data_queue

    def set_activities(self, *activities):
        self.activities_manager = ActivitiesManager(*activities)

    def set_rich_presence_apps(self, raw_apps):
        self.rpapps_controller = RPAppsController(raw_apps)

        self.delay_manager.set_target_function(self.rpapps_controller.change_state)

    def process_raw_data(self, data):
        # match REQUEST :
        # case UPDATE_RP
        # case GET_INFO
        activity_info = self.activities_manager.handle_data(activity_name=data['activity_name'], method=data['method'],
                                                            info=data['info'])
        activity_info = self.delay_manager.process_activity_info(activity_info)

        self.rpapps_controller.change_state(activity_info)

    def _start_processing_data_from_queue(self):
        while True:
            try:
                data = self.data_queue.get()
                self.process_raw_data(data)

            except Exception as exception:
                logger.exception("Error while processing data from queue")

    def start_processing_data_from_queue(self, daemon):
        threading.Thread(target=self._start_processing_data_from_queue, daemon=daemon).start()
        logger.info('rpac started processing data from queue')
