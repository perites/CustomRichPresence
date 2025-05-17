import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .anime import WatchingAnimeActivity
from .youtube import WatchingYoutubeActivity
from .pycharm import PyCharmActivity
from .geoguessr import GeoguessrActivity
