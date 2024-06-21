import logging
import sys

import urllib.parse

from dataclasses import dataclass

try:
    from RPActivityController import Activity, UpdateInfo
    from mal import Anime
except Exception as e:
    logging.exception(f"Failed to load external modules, exiting")
    sys.exit(1)


class WatchingAnimeJoyActivity(Activity):
    activity_name = "WatchingAnimeJoy"
    main_rp_app_name = "watching"
    clear_delay_seconds = 60

    def __init__(self, priority=0):
        super().__init__(priority)
        self.current_title = None

    def _handle_update(self, page_info):
        if (not isinstance(self.current_title, Title) or
                self.current_title.mal_title_id != page_info['mal_title_id']):
            self.current_title = Title(page_info['mal_title_id'], page_info['title_name'], page_info['current_episode'])
            logging.debug(f'Created new Title with page_info : {page_info}')

        elif self.current_title.current_episode != page_info['current_episode']:
            self.current_title.current_episode = page_info['current_episode']
            logging.debug(f'Updated Title current_episode: {page_info}')

        # else:
        #     logging.warning("No changes detected in page_info, returning False")
        #     return False

        return True, UpdateInfo(
            details=self.current_title.title_name,
            state=f"{self.current_title.media_type}, episode",
            party_size=[self.current_title.current_episode, self.current_title.episodes_amount],
            large_image=self.current_title.poster_url,
            large_text="Poster",
            buttons=[{"label": "Page on MAL", "url": self.current_title.url_to_mal},
                     {"label": "Progress", "url": self.current_title.url_to_progress},
                     ]
        )

    def _handle_clean(self, page_info):
        if not self.current_title or page_info['mal_title_id'] != self.current_title.mal_title_id:
            logging.warning("Was not cleaned, current_title and title to clean are not the same")
            return False, None

        self.current_title = None
        logging.debug(f"Clean method called on {self.main_rp_app_name}, current_title became None")
        return True, None


@dataclass
class Title:
    mal_title_id: int
    raw_title_name: str = ""
    current_episode: int = -1

    def __post_init__(self):
        self.mal_title = Anime(self.mal_title_id)
        self.title_name = self.mal_title.title_english or self.mal_title.title

        self.episodes_amount = self.mal_title.episodes

        self.poster_url = self.mal_title.image_url
        self.media_type = self.mal_title.type

        self.url_to_mal = self.mal_title.url
        self.url_to_progress = f"https://myanimelist.net/animelist/perite?s={urllib.parse.quote(self.title_name or self.raw_title_name)}"


class WatchingYoutubeActivity(Activity):
    activity_name = "WatchingYoutube"
    main_rp_app_name = "test"
    clear_delay_seconds = 60

    def __init__(self, priority=0):
        super().__init__(priority)

    def _handle_update(self, page_info):
        return True, UpdateInfo(
            details="watching_youtube",
            state=f"videos",
        )

    def _handle_clean(self, page_info):
        return True, None
