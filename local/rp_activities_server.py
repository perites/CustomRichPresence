# TODO add time support for Activities
# TODO add custom name from popup.html
#   TODO manual current episode
#   TODO button to clear status

# TODO support to youtube
# todo update readme
#      TODO Instalasion gude
# TODO extention for pycharm , using https://github.com/Almighty-Alpaca/JetBrains-Discord-Integration/tree/master ?

import sys

import queue

import logging

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] : %(message)s \/ [LOGGER:%(name)s] [FUNC:%(funcName)s] [FILE:%(filename)s]',
    datefmt='%H:%M:%S',
    filename="rp_activities_server.log",
    filemode='w', level=logging.DEBUG, encoding='utf-8')
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)

try:
    import config
    from Server import Server
    from RPActivitiesController import RichPresenceActivitiesController, RPAppsController, ActivitiesManager
    from CustomActivities import WatchingAnimeJoyActivity, WatchingYoutubeActivity, PyCharmActivity
except Exception as exception:
    logging.exception(f"Failed to load modules, exiting")
    sys.exit(1)

data_queue = queue.Queue()

server = Server(config.server['port'], config.server['server_ip'], data_queue)

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


def start_processing_data_from_queue():
    while True:
        try:
            json_data = data_queue.get()
            logging.debug(f"New data in queue, processing")
            rpac.process_raw_data(json_data)

        except Exception as exception:
            logging.exception(f"Failed to process data '{json_data}'")


if __name__ == '__main__':
    try:
        server.start_handling_clients()
        start_processing_data_from_queue()
    except Exception as e:
        logging.critical(f"Error in file, script ended")
        logging.exception(e)
