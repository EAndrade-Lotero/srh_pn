# Module with the coordinator classes

##########################################################################################
# Imports
##########################################################################################

import numpy as np
from copy import deepcopy

from markupsafe import Markup
from typing import List, Tuple, Dict, Any

import psynet.experiment
from psynet.page import  InfoPage
from psynet.utils import get_logger
from psynet.modular_page import (
    ModularPage,
    Prompt,
    PushButtonControl,
)
from psynet.trial.create_and_rate import (
    CreateAndRateNode,
    SelectTrialMixin,
)
from psynet.trial.imitation_chain import ImitationChainTrial

from .helper_classes import (
    RewardProcessing,
    ForagerPositions,
)
# from .custom_pages import WellBeingReportPage
from .coordinator_classes import CoordinatorTrial
from .helper_functions import get_world_wealth_slider_from_node
from .game_parameters import NUM_FORAGERS

logger = get_logger()

###########################################
# Forager classes
###########################################

########################
# Pages

# NO PAGES

########################
# Trial

class ForagerTrial(SelectTrialMixin, ImitationChainTrial):
    time_estimate = 5

    def show_trial(self, experiment, participant) -> List[Any]:
        assert self.trial_maker.target_selection_method == "all"

        # Get participant info
        logger.info(f"My trial id is: {participant.id}")

        # Get list of positions from target
        positions = self.get_positions_from_target(experiment)
        assert (isinstance(positions, ForagerPositions))
        logger.info(f"positions: {positions}")

        # Extract forager position
        forager_id, location = positions.get_forager_position(participant.id)
        experiment.var.set("forager_positions", deepcopy(positions))
        assert(len(experiment.var.forager_positions) == NUM_FORAGERS)

        # Create target_strs
        rated_target_strs = [f"{target}" for target in self.targets if isinstance(target, CoordinatorTrial)]
        assert(np.all([isinstance(target, str) for target in rated_target_strs])), f"{[type(target) for target in rated_target_strs]}"
        logger.info(f"rated_target_strs: {rated_target_strs}")

        # Extract variables from node
        if hasattr(self, "origin"):
            # Extract world, wealth, slider values
            world, world_slider, wealth = get_world_wealth_slider_from_node(self.origin)
        else:
            raise Exception("Error: No world created for this trial.")

        list_of_pages = [
            InfoPage(
                "This is going to be the Instructions page for a FORAGER",
                time_estimate=5
            ),
            ModularPage(
                "forager_turn",
                Prompt(
                    text=Markup(f"""
                    <p>You have been located here:</p><br><p>{location}</p>
                    """)
                ),
                PushButtonControl(
                    choices=rated_target_strs[:1],
                    labels=["Continue"],
                    arrange_vertically=False,
                ),
                time_estimate=self.time_estimate
            ),
            InfoPage(
                RewardProcessing.get_reward_text(
                    n_coins=wealth,
                    slider=world_slider,
                    trial_type=f"forager-{forager_id}"
                ),
                time_estimate=5
            ),
            # WellBeingReportPage(
            #     time_estimate=self.time_estimate,
            # ),
        ]
        return list_of_pages

    def get_positions_from_target(
        self,
        experiment: psynet.experiment.Experiment
    ) -> Dict[str, Tuple[int, int]]:

        positions_ = deepcopy(experiment.var.forager_positions)

        if positions_ is None:
            # There should be only one target
            targets = [target for target in self.targets if isinstance(target, CoordinatorTrial)]
            assert (len(targets) == 1), f"Error: Num. targets should be 1 but got {len(targets)}!"

            # Get target from coordinator
            target = targets[0]
            if isinstance(target, CreateAndRateNode):
                target = self.get_target_answer(target)
            assert isinstance(target, CoordinatorTrial)

            answers = self.get_target_answer(target)
            positions = answers['custom_front_end_to_position_foragers']
        else:
            positions = positions_

        assert (len(positions) == NUM_FORAGERS)
        return positions

    def format_answer(self, raw_answer, **kwargs) -> str:
        try:
            if isinstance(raw_answer, dict):
                answer = raw_answer["forager_turn"]
            elif isinstance(raw_answer, str):
                answer = raw_answer
            else:
                logger.info(f"raw_answer does not have the right type or key: {raw_answer}")
                raise TypeError
            return answer
        except (ValueError, AssertionError):
            return f"INVALID_RESPONSE"

###########################################