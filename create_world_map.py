# Script to create world according to game parameters

from pathlib import Path
from helper_classes import World

from game_parameters import (
    NUM_COINS,
    NUM_FORAGERS,
    DISTRIBUTION,
    DISPERSION,
    IMAGE_PATHS,
)

world = World(
    num_coins=NUM_COINS,
    num_centroids=NUM_FORAGERS,
    distribution=DISTRIBUTION,
    dispersion=DISPERSION,
)
world.map_path = Path(IMAGE_PATHS["map_url"])
world.coin_path = Path(IMAGE_PATHS["coin_url"])
world.render(show=False, coin_zoom=1/NUM_COINS)
