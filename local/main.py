from flask import Flask, request
from flask_cors import CORS

from pypresence import Presence
from mal import Anime

import urllib.parse

# TODO add time support
# TODO add logs
# TODO Add readme to git

# TODO manual current episode
# TODO application ID setting
# TODO button to clear status

# TODO Cmplitly invisible on startup
# TODO support to youtube


app = Flask(__name__)
CORS(app, resources={
    r"/receiveinfo": {"origins": ["https://animejoy.ru", "chrome-extension://dbcbbndaklflflpmibcinoffbegfaple"]}})

CLIENT_ID = '1250924979776786514'
rpc = Presence(CLIENT_ID)
rpc.connect()

THE_TITLE = None


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
        rpc.update(
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
        print(f"rpc updated: {self.mal_title_id} | {self.current_episode}")


def update(page_info):
    global THE_TITLE

    if (THE_TITLE is None) or (THE_TITLE.mal_title_id != page_info["mal_title_id"]):
        THE_TITLE = Title(mal_title_id=page_info["mal_title_id"],
                          title_name=page_info['title_name'],
                          current_episode=page_info["current_episode"])

    elif THE_TITLE.current_episode != page_info["current_episode"]:
        THE_TITLE.current_episode = page_info["current_episode"]

    else:
        return

    THE_TITLE.update_rich_presence()


def clear_rich_presence():
    global THE_TITLE
    if not THE_TITLE:
        return
    rpc.clear()
    print(
        f"rpc cleared : {THE_TITLE.mal_title_id} | {THE_TITLE.current_episode}")
    THE_TITLE = None


@app.route("/receiveinfo", methods=['POST'])
def receiveinfo():
    data = request.get_json()

    print(request.headers.get('Origin'), )
    # print(data['data'])

    match data["method"]:
        case "update":
            update(page_info=data['data'])
        case "clear":
            clear_rich_presence()

    return {'result': "OK"}, 200


if __name__ == '__main__':
    app.run(debug=True)
