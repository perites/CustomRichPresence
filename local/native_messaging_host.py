# TODO add time support

# TODO check how two rps Presence interact
# TODO add custom activity_name from popup.html
#   TODO manual current episode
#   TODO button to clear status


# TODO confg file
#   TODO application ID setting

# TODO support to youtube
# TODO check how many same packages arrived, max ?
# TODO Instalasion gude


import sys
import os

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
    from classes import NativeMessagesToRPS, WatchingAnimeJoyActivity, WatchingYoutubeActivity, ActivitiesManager, \
        RPAppsController
except Exception as e:
    logging.error(f"Failed to load module, exiting | Exception:{e} ")
    sys.exit(1)

config_apps = {"watching": "1250924979776786514",
               "test": "1252626262346694686"}

main = NativeMessagesToRPS()
main.set_activities_manager(
    ActivitiesManager(
        WatchingAnimeJoyActivity(2),
        WatchingYoutubeActivity(3),
    ))

main.set_rpapps_controller(
    RPAppsController(config_apps)
)

if __name__ == '__main__':
    try:
        main.start_loop()
    except Exception as e:
        logging.critical(f"Error in file, script ended | Exception: {e}")
