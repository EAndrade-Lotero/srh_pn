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
        # Update slider values
        sliders = SliderValues()
        sliders.update_from_trials(trials)

        # Update wealth using results from players
        accumulated_wealth = WealthTracker()
        accumulated_wealth.update_from_trials(trials, sliders)

        # Update records
        self.seed['overhead'] = sliders.get_overhead()
        self.seed['prerogative'] = sliders.get_coordinator_prerogative()
        self.seed['wages'] = sliders.get_wages_commission()
        self.seed['wealth'] = accumulated_wealth.n_coins

