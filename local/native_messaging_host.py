# TODO separate file using Sockets

# todo function to add methods in Activity ?
# TODO add time support for WatchingAnime
# TODO add custom name from popup.html
#   TODO manual current episode
#   TODO button to clear status

# TODO support to youtube
# todo update readme
#      TODO Instalasion gude
# TODO extention for pycharm , using https://github.com/Almighty-Alpaca/JetBrains-Discord-Integration/tree/master ?

import os
import sys

import struct
import json

import logging

logging.basicConfig(
    format='%(asctime)s - %(levelname)s : %(message)s | func: %(funcName)s --- file: %(filename)s --- logger: %(name)s',
    datefmt='%d-%m-%y %H:%M:%S',
    filename="native_messaging_host.log",
    filemode='w', level=logging.DEBUG, encoding='utf-8')
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)

config_path_to_modules = '.venv\\Lib\\site-packages'
site_packages = os.path.join(config_path_to_modules)
sys.path.insert(0, site_packages)
try:
    import config
    from RPActivityController import RichPresenceActivitiesController, RPAppsController, ActivitiesManager
    from CustomActivities import WatchingAnimeJoyActivity, WatchingYoutubeActivity, PyCharmActivity
except Exception as exception:
    logging.exception(f"Failed to load modules, exiting")
    sys.exit(1)

rpac = RichPresenceActivitiesController()

rpac.set_activities_manager(
    ActivitiesManager(
        WatchingAnimeJoyActivity(2),
        WatchingYoutubeActivity(2),
        PyCharmActivity(1)
    ))

rpac.set_rpapps_controller(
    RPAppsController(config.rich_presence_apps)
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

        except Exception as exception:
            logging.exception(f"Caught exception in main loop")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.critical(f"Error in file, script ended")
        logging.exception(e)
