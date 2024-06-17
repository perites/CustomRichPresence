import sys
import struct

import json
import logging
import urllib.parse

from pypresence import Presence
from mal import Anime


# TODO add time support

# TODO manual current episode
# TODO application ID setting
# TODO button to clear status

# TODO support to youtube

# pyinstaller --onefile --distpath local\build --workpath local\build\other --specpath local\build\other local\native_messaging_host.py

class Title:
    def __init__(self, mal_title_id=None, title_name=None, current_episode=-1):
        self.mal_title = Anime(mal_title_id)

        self.title_name = self.mal_title.title_english or self.mal_title.title

        self.current_episode = current_episode
        self.episodes_amount = self.mal_title.episodes

        self.mal_title_id = mal_title_id
        self.poster_url = self.mal_title.image_url
        self.media_type = self.mal_title.type

        self.url_to_mal = self.mal_title.url
        self.url_to_progress = f"https://myanimelist.net/animelist/perite?s={urllib.parse.quote(self.title_name or title_name)}"

    def update_rich_presence(self):
        rps.update(
            details=self.title_name,

            state=f"{self.media_type}, episode",
            party_size=[self.current_episode, self.episodes_amount],

            large_image=self.poster_url,
            large_text="Poster",

            buttons=[{"label": "Page on MAL", "url": self.url_to_mal},
                     {"label": "Progress",
                      "url": self.url_to_progress}
                     ]
        )
        logging.info(
            f"RPS updated | MAl title id : {self.mal_title_id} | Current episode : {self.current_episode}")


def update(page_info):
    global THE_TITLE

    if (THE_TITLE is None) or (THE_TITLE.mal_title_id != page_info["mal_title_id"]):

        THE_TITLE = Title(mal_title_id=page_info["mal_title_id"],
                          title_name=page_info['title_name'],
                          current_episode=page_info["current_episode"])
        logging.debug(
            f"Created new Title | MAl title id : {THE_TITLE.mal_title_id} | Current episode : {THE_TITLE.current_episode}")

    elif THE_TITLE.current_episode != page_info["current_episode"]:
        THE_TITLE.current_episode = page_info["current_episode"]
        logging.debug(
            f"Updated Title current episode | MAl title id : {THE_TITLE.mal_title_id} | Current episode : {THE_TITLE.current_episode} ")

    else:
        logging.debug("No action on Title, returning")
        return

    THE_TITLE.update_rich_presence()


def clear_rich_presence():
    global THE_TITLE
    if not THE_TITLE:
        logging.debug("Was not cleaned, already None")
        return
    rps.clear()
    logging.info(
        f"RPS cleared | MAl title id : {THE_TITLE.mal_title_id} | Current episode : {THE_TITLE.current_episode}")
    THE_TITLE = None


logging.basicConfig(format='%(levelname)s: %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    filename="C:\\Users\\nikit\PycharmProjects\\CustomRichPresence\\local\\native_messaging_host.log",
                    filemode='w', level=logging.DEBUG, encoding='utf-8')

logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)
CLIENT_ID = '1250924979776786514'
rps = Presence(CLIENT_ID)
rps.connect()

THE_TITLE = None


def main():
    logger.info('Starting native_messaging_host')
    while True:
        try:
            text_length_bytes = sys.stdin.buffer.read(4)
            logging.debug(f"Data received")
            if len(text_length_bytes) == 0:
                sys.exit(0)
            text_length = struct.unpack('i', text_length_bytes)[0]
            data_raw = sys.stdin.buffer.read(text_length).decode('utf-8')
            data = json.loads(data_raw)
            logging.debug(f"Data parsed: {data}")
            match data["method"]:
                case "update":
                    update(page_info=data['data'])
                case "clear":
                    clear_rich_presence()

        except Exception as e:
            logging.error(e)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.critical(e)
