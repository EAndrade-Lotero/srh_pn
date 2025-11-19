# Module with the custom node
##########################################################################################
# Imports
##########################################################################################

from psynet.trial import ChainNode
from psynet.utils import get_logger
from psynet.trial.create_and_rate import CreateAndRateNodeMixin

from .helper_classes import (
    SliderValues,
    WealthTracker,
)
from .game_parameters import (
    POWER_ROLE,
    NUM_FORAGERS,
)

logger = get_logger()

###########################################
# Custom node
###########################################

class CustomNode(CreateAndRateNodeMixin, ChainNode):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_definition_from_seed(self, seed, experiment, participant):
        return seed

    def summarize_trials(self, trials: list, experiment, participant) -> None:
        # import pydevd_pycharm
        # pydevd_pycharm.settrace('localhost', port=12345, stdout_to_server=True, stderr_to_server=True)

        # Update slider values
        sliders = SliderValues()
        sliders.update_from_trials(trials)

        # Update wealth using results from players
        accumulated_wealth = WealthTracker()
        accumulated_wealth.update_from_trials(trials, sliders)

        # Update records
        seed = self.seed.copy()
        seed['overhead'] = sliders.get_overhead()
        seed['prerogative'] = sliders.get_coordinator_prerogative()
        seed['wages'] = sliders.get_wages_commission()
        seed['wealth'] = accumulated_wealth.n_coins

        return seed
