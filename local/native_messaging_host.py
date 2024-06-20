# TODO add time support for WatchingAnime

# TODO add custom activity_name from popup.html
#   TODO manual current episode
#   TODO button to clear status


# TODO confg file
#   TODO application ID setting
# todo Clear after some delay ?
# TODO support to youtube
# TODO Instalasion gude
# TODO extention for pycharm
# TODO separate file using Sockets

import sys
import os

import struct
import json

import logging

confg_path_to_modules = '.venv\\Lib\\site-packages'
site_packages = os.path.join(confg_path_to_modules)
sys.path.insert(0, site_packages)

logging.basicConfig(
    format='%(asctime)s - %(levelname)s : %(message)s | func: %(funcName)s --- file: %(filename)s --- logger: %(name)s',
    datefmt='%d-%m-%y %H:%M:%S',
    filename="native_messaging_host.log",
    filemode='w', level=logging.DEBUG, encoding='utf-8')

logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("rpac").setLevel(logging.DEBUG)

try:
    from RPActivityController import RichPresenceActivityController, RPAppsController, ActivitiesManager
    from my_activities import WatchingAnimeJoyActivity, WatchingYoutubeActivity
except Exception as e:
    logging.exception(f"Failed to load modules, exiting")
    sys.exit(1)

config_apps = {"watching": "1250924979776786514",
               "test": "1252626262346694686"}

rpac = RichPresenceActivityController()
rpac.set_activities_manager(
    ActivitiesManager(
        WatchingAnimeJoyActivity(2),
        WatchingYoutubeActivity(1),
    ))

rpac.set_rpapps_controller(
    RPAppsController(config_apps)
)


def get_native_message():
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        sys.exit(0)
    message_length = struct.unpack("@I", raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode("utf-8")
    return json.loads(message)


def main():
    logging.info(f'Starting main loop')
    while True:
        try:
            json_data = get_native_message()
            logging.debug(f"Data parsed: {json_data}")

            rpac.process_raw_data(json_data)
            # activity_info = self.activities_manager.activity_handle(activity_name=json_data['activity'],
            #                                                         method=json_data['method'],
            #                                                         info=json_data['info'], )
            #
            # self.rpapps_controller.change_state(activity_info)

        except Exception as e:
            logging.exception(f"Caught exception in main loop")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.critical(f"Error in file, script ended")
        logging.exception(e)
