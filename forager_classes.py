# Module with the coordinator classes

##########################################################################################
# Imports
##########################################################################################

import numpy as np

from typing import List, Tuple, Dict, Any, Union

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

from .game_parameters import NUM_FORAGERS
from .helper_classes import RewardProcessing
from .custom_pages import WellBeingReportPage
from .coordinator_classes import CoordinatorTrial
from .helper_functions import get_list_participants_ids

logger = get_logger()

###########################################
# Forager classes
###########################################


class ForagerTrial(SelectTrialMixin, ImitationChainTrial):
    time_estimate = 5

    def show_trial(self, experiment, participant) -> List[Any]:
        assert self.trial_maker.target_selection_method == "all"

        # Get wages_parameter from previous generation
        wages_parameter = experiment.var.slider.get_wages_commission()

        # Get list of positions from target
        positions = self.get_positions_from_target()
        logger.info(f"positions: {positions}")
        # Get participant info
        logger.info(f"My id is: {participant.id}")
        # Get list of previous participants
        participants_ids = get_list_participants_ids(experiment, participant)
        # Calculate id based on number of previous non-failed participants
        forager_id = (len(participants_ids) % (NUM_FORAGERS + 1)) - 1
        forager_id = int(forager_id)
        logger.info(f"forager id: {forager_id}")
        # Extract forager position
        location = positions[str(forager_id)]

        # Create target_strs
        rated_target_strs = [f"{target}" for target in self.targets if isinstance(target, CoordinatorTrial)]
        assert(np.all([isinstance(target, str) for target in rated_target_strs])), f"{[type(target) for target in rated_target_strs]}"
        logger.info(f"rated_target_strs: {rated_target_strs}")

        list_of_pages = [
            InfoPage(
                "This is going to be the Instructions page for a FORAGER",
                time_estimate=5
            ),
            ModularPage(
                "forager_turn",
                Prompt(
                    text=f"You have been located here:<br><strong>{location}</strong>",
                ),
                PushButtonControl(
                    choices=rated_target_strs[:1],
                    labels=["Continue"],
                    arrange_vertically=False,
                ),
                time_estimate=self.time_estimate
            ),
            InfoPage(
                RewardProcessing.get_reward_text(experiment, f"forager-{forager_id}"),
                time_estimate=5
            ),
            WellBeingReportPage(
                time_estimate=self.time_estimate,
            ),
        ]
        return list_of_pages

    def get_positions_from_target(self) -> Dict[str, Tuple[int, int]]:
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