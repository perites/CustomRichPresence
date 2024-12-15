# TODO extension for pycharm , using https://github.com/Almighty-Alpaca/JetBrains-Discord-Integration/tree/master ?
# TODO add custom name from popup.html
#   TODO manual current episode
#   TODO button to clear status

# TODO support to youtube
# TODO Instalasion gude to RPAC

import sys

import queue

import logging
import time

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] : %(message)s  ||[LOGGER:%(name)s] [FUNC:%(funcName)s] [FILE:%(filename)s]',
    datefmt='%H:%M:%S',
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("main.log", mode='w', encoding='utf-8', )
    ]
)

logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)

try:
    import config
    from Server import Server
    from rpac import RichPresenceActivitiesController
    from CustomActivities import WatchingAnimeJoyActivity, WatchingYoutubeActivity, PyCharmActivity, GeoguessrActivity
except Exception as exception:
    logging.exception(f"Failed to load modules, exiting")
    sys.exit(1)

data_queue = queue.Queue()

server = Server(config.server['port'], config.server['server_ip'], data_queue)

rpac = RichPresenceActivitiesController(data_queue)
rpac.set_activities(
    WatchingAnimeJoyActivity(2),
    WatchingYoutubeActivity(2),
    GeoguessrActivity(2),
    PyCharmActivity(1),
)
rpac.set_rich_presence_apps(config.rich_presence_apps)

if __name__ == '__main__':
    try:
        server.start_handling_clients(daemon=True)
        rpac.start_processing_data_from_queue(daemon=True)
        while True:
            time.sleep(60)
    except Exception as e:
        logging.critical(f"Error in file, script ended")
        logging.exception(e)
