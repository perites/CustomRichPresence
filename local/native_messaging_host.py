# TODO add time support

# TODO check how two rps Presence interact
# TODO add custom activity_name from popup.html
#   TODO manual current episode
#   TODO button to clear status


# TODO confg file
#   TODO application ID setting

# TODO support to youtube

# TODO Instalasion gude


import sys
import os

import struct
import json

import logging

venv_path = "C:\\Users\\nikit\\PycharmProjects\\CustomRichPresence\\local\\.venv"
site_packages = os.path.join(venv_path, 'Lib', 'site-packages')
sys.path.insert(0, site_packages)

logging.basicConfig(format='%(levelname)s: %(asctime)s - %(message)s | func: %(funcName)s', datefmt='%d-%b-%y %H:%M:%S',
                    filename="C:\\Users\\nikit\PycharmProjects\\CustomRichPresence\\local\\native_messaging_host.log",
                    filemode='w', level=logging.DEBUG, encoding='utf-8')

logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)

try:
    from classes import WatchingAnimeJoyActivity, WatchingYoutubeActivity, ActivitiesManager, RPAppsController
except Exception as e:
    logging.error(f"Failed to load module, exiting | Exception:{e} ")
    sys.exit(1)

config_apps = {"watching": "1250924979776786514",
               "test": "1252626262346694686"}
rpapps_controller = RPAppsController(config_apps)

am = ActivitiesManager(
    WatchingAnimeJoyActivity(2),
    WatchingYoutubeActivity(1),
)


def get_message():
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        sys.exit(0)
    message_length = struct.unpack("@I", raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode("utf-8")
    return json.loads(message)


def main():
    logging.info('Starting native_messaging_host')
    while True:
        try:
            json_data = get_message()
            logging.debug(f"Data parsed: {json_data}")

            activity_info = am.activity_handle(activity_name=json_data['activity'],
                                               method=json_data['method'],
                                               info=json_data['info'], )

            if not activity_info:
                logging.info("Activity handle returned False, process to next cycle")
                continue

            rpapps_controller.change_state(activity_info)

        except Exception as e:
            logging.error(f"Error in main loop | Exception: {e}")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.critical(f"Error in file, script ended | Exception: {e}")
