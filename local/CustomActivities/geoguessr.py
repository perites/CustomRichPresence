import sys

from .logger import logger

try:
    from rpac import Activity, UpdateInfo

except Exception as exception:
    logger.exception(f"Failed to load external modules, exiting")
    sys.exit(1)


class GeoguessrActivity(Activity):
    activity_name = "Geoguessr"
    main_rp_app_name = "Geoguessr"

    clear_delay_seconds = 20

    max_seconds_after = {"clear": 60 * 20,
                         "update": None}

    game_modes_names = {
        "duels": "Duels",
        "game": "Regular Game",
        "live-challenge": "In party"
    }

    def __init__(self, priority):
        super().__init__(priority)

    def _handle_update(self, page_info):
        if page_info['rounds_info'][1] < 1:
            party_size = None
            state = f"Round {page_info['rounds_info'][0]}"
        else:
            party_size = [int(page_info['rounds_info'][0]),
                          int(page_info['rounds_info'][1])]
            state = "Round"

        buttons = [{"label": "Profile", "url": "https://www.geoguessr.com/user/62e07a68cc4b4df67260f12c"}]
        # if page_info.get('additional_info') and page_info['additional_info'].get('share_link'):
        #     buttons.append({"label": "Join Lobby", "url": page_info['additional_info']['share_link']})

        return True, UpdateInfo(
            start=self.get_start_time(),

            details=f"{self.game_modes_names[page_info['game_mode']]} on map {page_info['map_name']}",
            state=state,
            party_size=party_size,

            large_image="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcShlh3CUppNuuv4Ggaec_Rvgh5s99dBf-SuGg&s",
            large_text="Geoguessr Logo",
            buttons=buttons
        )

    def _handle_clean(self, page_info):
        return True, None
