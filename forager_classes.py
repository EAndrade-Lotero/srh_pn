# Module with the coordinator classes

##########################################################################################
# Imports
##########################################################################################

from typing import Any, List

from psynet.modular_page import (
    ModularPage,
    Prompt,
    PushButtonControl,
    SliderControl,
)
from psynet.trial.create_and_rate import (
    CreateAndRateNode,
    SelectTrialMixin,
)
from psynet.trial.imitation_chain import ImitationChainTrial
from psynet.utils import get_logger

from .helper_functions import get_list_participants_ids
from .custom_front_end import positioning_prompt
from .coordinator_classes import CoordinatorTrial
from .game_parameters import NUM_FORAGERS

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

        # There should be only one target
        targets = [target for target in self.targets if isinstance(target, CoordinatorTrial)]
        assert (len(targets) == 1), f"Error: Num. targets should be 1 but got {len(targets)}!"

        # Get target from coordinator
        target = targets[0]
        if isinstance(target, CreateAndRateNode):
            target = self.get_target_answer(target)
        assert isinstance(target, CoordinatorTrial)

        # Get list of positions from target
        positions = self.get_target_answer(target)
        logger.info(f"positions: {positions}")

        # Get participant info
        logger.info(f"My id is: {participant.id}")

        # Get list of previous participants
        participants_ids = get_list_participants_ids(experiment, participant)
        # Calculate id based on number of previous non-failed participants
        forager_id = (len(participants_ids) % (NUM_FORAGERS + 1)) - 1

        logger.info(f"forager id: {forager_id}")

        # Extract forager position
        location = positions[str(forager_id)]

        list_of_pages = [
            # InfoPage(
            #     "This is going to be the Instructions page for a FORAGER",
            #     time_estimate=5
            # ),
            ModularPage(
                "forager_wages_parameter_modification",
                Prompt(
                    text=f"Move the slider to set a new value for the wages parameter:",
                ),
                SliderControl(
                    start_value=wages_parameter,
                    min_value=max(wages_parameter - 0.2, 0),
                    max_value=min(wages_parameter + 0.2, 1),
                    n_steps=10000,
                ),
                time_estimate=self.time_estimate
            ),
            ModularPage(
                "forager_turn",
                positioning_prompt(
                    text=f"You have been located here:<br><strong>{location}</strong>",
                    img_url=self.context["img_url"],
                ),
                PushButtonControl(
                    choices=[f"{target}" for target in targets],
                    labels=["Continue"],
                    arrange_vertically=False,
                ),
                time_estimate=self.time_estimate
            ),
        ]
        return list_of_pages
###########################################