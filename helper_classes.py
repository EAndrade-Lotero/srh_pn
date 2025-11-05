# Helper classes to be used in the experiment
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from numpy.typing import NDArray
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from typing import List, Tuple, Optional, Iterable, Union, Any

import psynet.experiment
from .game_parameters import NUM_FORAGERS


class SliderValues:
    """Keeps track and updates the values of the three sliders"""
    coordinator_prerogative = 0.5
    wages_commission = 0.5
    overhead = 0.5
    rng = np.random.default_rng()

    def __init__(self, seed:Optional[Union[int, None]]=None) -> None:
        if seed is None:
            seed = 42
        self.rng = np.random.default_rng(seed)

    def get_coordinator_prerogative(self) -> float:
        return self.coordinator_prerogative

    def get_wages_commission(self) -> float:
        return self.wages_commission

    def get_overhead(self) -> float:
        return self.overhead

    def update_coordinator_prerogative(self, value: float) -> None:
        self.coordinator_prerogative = value

    def update_wages_commission(self, value: float) -> None:
        self.wages_commission = value

    def update_overhead(self, value: float) -> None:
        self.overhead = value

    def random_init(self) -> None:
        self.coordinator_prerogative = self.rng.random()
        self.wages_commission = self.rng.random()
        self.overhead = self.rng.random()

    def __str__(self) -> str:
        print_out = f"Coordinator prerogative: {self.coordinator_prerogative:.2f}"
        print_out += f"\nWages commission: {self.wages_commission:.2f}"
        print_out += f"\nOverhead: {self.overhead:.2f}"
        return print_out

    @staticmethod
    def dimension_explanation(dimension:str) -> str:
        assert(dimension in ["overhead", "wages-commission", "prerogative"]), f"Invalid dimension: {dimension}. Expected 'overhead', 'wages-commission' or 'prerogative'"
        if dimension == "overhead":
            explanation = "Overhead"
        elif dimension == "wages-commission":
            explanation = "Wages commission"
        elif dimension == "prerogative":
            explanation = "Prerogative"
        else:
            raise ValueError(f"Invalid dimension: {dimension}. Expected 'overhead', 'wages-commission' or 'prerogative'")
        return explanation


class World:
    """2D grid world with coins placed according to a distribution.

    Grid cells contain 1 if a coin is present, otherwise 0.
    """
    width: Optional[int] = 100
    height: Optional[int] = 100
    seed: Optional[int] = None
    coin_path: Path = Path('./static/assets/coin.png')
    map_path: Path = Path('./static/map.png')

    def __init__(
        self,
        num_coins: int,
        num_centroids: int,
        distribution: str,
        dispersion: float,
    ) -> None:
        self.num_coins = num_coins
        self.num_centroids = num_centroids
        assert(distribution in ["linear", "circular", "oval"]), f"Dispersion {distribution} not supported. Choose from ['linear', 'circular', 'oval']."
        self.distribution = distribution
        assert(dispersion > 0), f"Dispersion must be greater than 0 (but got {dispersion})."
        self.dispersion = dispersion
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive.")
        if self.num_coins < 0:
            raise ValueError("num_coins must be non-negative.")
        if self.num_coins > self.width * self.height / 10:
            raise ValueError(f"num_coins cannot exceed {int(self.width * self.height / 10)} (but got {self.num_coins})")
        self._rng = np.random.default_rng(self.seed if self.seed is not None else 42)
        self.grid = np.zeros((self.width, self.height))
        self._place_coins()

    def positions(self) -> List[Tuple[int, int]]:
        """List of (row, col) positions where coins are present."""
        coords_x, coords_y = np.where(self.grid == 1)
        coin_positions = list(zip(coords_x.tolist(), coords_y.tolist()))
        return coin_positions

    def count_coins(self) -> int:
        """Return the number of coins currently placed."""
        return self.grid.sum()

    def clear(self) -> None:
        """Remove all coins (set all cells to 0)."""
        self.grid = np.zeros((self.width, self.height))

    def _place_coins(self) -> None:
        """Dispatch to the chosen distribution strategy."""
        self.clear()
        if self.num_coins == 0:
            return

        coins_per_centroid = self.num_coins // self.num_centroids
        offset = self.count_coins() - coins_per_centroid * self.num_centroids
        coins_per_centroid = [coins_per_centroid for _ in range(self.num_centroids)]
        if offset > 0:
            coins_per_centroid[-1] += offset

        centroids = self.get_centroids()
        for i, (x, y) in enumerate(centroids):
            n_coins = coins_per_centroid[i]
            sample_coins = self.sample_bivariate_normal(
                mean=(x, y),
                cov=((self.dispersion, 0), (0, self.dispersion)),
                n=n_coins,
            )
            coords_x = [int(x) for x, y in sample_coins]
            coords_y = [int(y) for x, y in sample_coins]
            self.grid[coords_x, coords_y] = 1

    def get_centroids(self) -> List[Tuple[int, int]]:
        """Return the centroids of coins placed."""
        if self.num_centroids == 1:
            return [(int(self.width / 2), int(self.height / 2))]

        if self.distribution == "linear":
            sample = np.linspace(0, 1, self.num_centroids + 2)[1:-1]
            sample = [(int(x * self.width), int(x * self.height)) for x in sample]
            return sample

        elif self.distribution == "circular":
            sample = np.linspace(0, 1, self.num_centroids + 1)[:-1]
            theta = (2.0 * np.pi) * sample
            x = np.cos(theta).tolist()
            y = np.sin(theta).tolist()
            sample = list(zip(x, y))

            x_scale = 0.25 * self.width
            y_scale = 0.25 * self.height
            sample = [(x * x_scale, y * y_scale) for x, y in sample]
            sample = [(x + 0.5 * self.width, y + 0.5 * self.height) for x, y in sample]
            sample = [(int(x), int(y)) for x, y in sample]
            return sample

        elif self.distribution == "oval":
            raise NotImplementedError("oval dispersion is not yet implemented.")

        else:
            raise NotImplementedError(f"Dispersion {self.distribution} not supported. Choose from ['linear', 'circular', 'oval'].")

    def __str__(self) -> str:
        """ASCII representation: '1' for coin, '.' for empty."""
        lines = []
        for r in range(self.height):
            line = "".join("1" if self.grid[r][c] else "." for c in range(self.width))
            lines.append(line)
        return "\n".join(lines)

    def render(
        self,
        show: bool = False,
        coin_zoom: float = 0.1,
        coin_percentage: Optional[float] = 1,
    ) -> None:
        """Render the world by drawing coin images at coin positions.

        Args:
            show: If True, also display the figure.
            coin_zoom: Relative size of the coin inside a cell (0<zoom<=1).
        """
        if not (0 < coin_zoom <= 1.0):
            raise ValueError("coin_zoom must be in (0, 1].")

        # Canvas sized roughly to grid, independent of DPI
        fig, ax = plt.subplots(
            figsize=(self.width / 10, self.height / 10),
            dpi=300
        )

        # Light cell grid
        ax.set_xticks(np.arange(-.5, self.width, 1), minor=True)
        ax.set_yticks(np.arange(-.5, self.height, 1), minor=True)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal")
        ax.set_title("World", pad=8)
        ax.set_axis_off()

        # Load coin image (RGBA supported)
        raw_coin_img = plt.imread(self.coin_path)
        coin_img = OffsetImage(raw_coin_img, zoom=coin_zoom)

        # Place the coin image centered in each occupied cell
        half = 0.5 * coin_zoom
        coins = self.positions()
        for (r, c) in coins:
            if self._rng.random() < coin_percentage:
                coin_img.image.axes = ax
                ab = AnnotationBbox(
                    coin_img,
                    (c + half, r + half),
                    frameon=False
                )
                ax.add_artist(ab)

        fig.savefig(self.map_path, dpi=300, bbox_inches="tight")
        if show:
            plt.show()
        plt.close(fig)

    def sample_bivariate_normal(
        self,
        mean: Iterable[float],
        cov: Iterable[Iterable[float]],
        n: int,
    ) -> List[Tuple[float, float]] | NDArray[np.float64]:
        """
        Sample n points from a 2D (bivariate) normal distribution.

        Parameters
        ----------
        n : int
            Number of samples.
        mean : Iterable[float]
            Length-2 mean vector [mu_x, mu_y].
        cov : Iterable[Iterable[float]]
            2x2 covariance matrix [[var_x, cov_xy], [cov_yx, var_y]].

        Returns
        -------
        List[Tuple[float, float]] | NDArray[np.float_]
            The sampled coordinates.
        """
        mean_arr = np.asarray(mean, dtype=float)
        cov_arr = np.asarray(cov, dtype=float)

        samples: NDArray[np.float64] = self._rng.multivariate_normal(
            mean=mean_arr,
            cov=cov_arr,
            size=n
        )

        return [tuple(row) for row in samples]


class WealthTracker:
    """Keeps track of the coins throughout iterations"""

    def __init__(self) -> None:
        self.n_coins: int = 0
        self.num_foragers: int = NUM_FORAGERS
        self.coordinator_wealth: Union[float, None] = None
        self.foragers_wealth: Union[List[float], None] = None

    def update(self, trials: List[Any], slider: SliderValues) -> None:
        assert len(trials) == self.num_foragers
        pass

    def initialize(self, slider: SliderValues) -> None:
        self.coordinator_wealth = 0
        self.foragers_wealth = [0] * self.num_foragers

    def get_coordinator_wealth(self) -> float:
        assert(self.coordinator_wealth is not None), "Coordinator wealth is not set yet. Run update() first."
        return self.coordinator_wealth

    def get_forager_wealth(self, forager_id: int) -> float:
        assert(self.foragers_wealth is not None), "Forager wealth is not set yet. Run update() first."
        return self.foragers_wealth[forager_id]


class RewardProcessing:
    """Processes rewards and gives feedback"""

    @staticmethod
    def get_reward_text(
        experiment: psynet.experiment.Experiment,
        trial_type: str
    ) -> str:
        trial_types = ["coordinator"] + [f"forager-{i+1}" for i in range(NUM_FORAGERS)]
        assert(trial_type in trial_types), f"Invalid trial type: {trial_type}. Expected one of {trial_types}."

        wealth_tracker = experiment.var.accumulated_wealth
        n_coins = wealth_tracker.n_coins

        if trial_type == "coordinator":
            wealth = wealth_tracker.get_coordinator_wealth()
        elif trial_type.startswith("forager"):
            forager_id = trial_type.split("-")[1]
            wealth = wealth_tracker.get_forager_wealth(forager_id)
        else:
            raise ValueError(f"Invalid trial type: {trial_type}. Expected one of {trial_types}.")

        reward_text = f"The total number of coins collected on the previous iteration is {n_coins}."
        reward_text += f"Based on the existing contract, you received {wealth} coins."
        reward_text += f"Bear in mind that your performance in this turn will influence the rewards"
        reward_text += f"of future iterations, including your own."
        return reward_text

