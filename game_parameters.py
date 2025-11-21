# Module with the game parameters
import numpy as np

POWER_ROLE = "coordinator"
NUM_FORAGERS = 2
NUM_CENTROIDS = 2
NUM_COINS = 100
LIST_OF_DISTRIBUTIONS = ["linear"]
DISPERSION = 10
STARTING_OVERHEAD = 0.5
STARTING_PREROGATIVE = 0.5
STARTING_WAGES = 0.5
INITIAL_WEALTH = 100

MAX_NODES_PER_CHAIN = 10

IMAGE_PATHS = {
    "img_url": "static/positioning.png",
    "map_url": "static/map.png",
    "coin_url": "static/coin.png",
    "forager_url": "static/forager.png",
}

RNG = np.random.default_rng(42)