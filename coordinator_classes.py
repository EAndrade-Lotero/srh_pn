# Module with the coordinator classes

##########################################################################################
# Imports
##########################################################################################
from pathlib import Path
from markupsafe import Markup
from typing import (
    Any, Union, List,
)

from psynet.page import  InfoPage
from psynet.utils import get_logger
from psynet.modular_page import (
    ModularPage,
    Prompt,
    SliderControl,
)
from psynet.timeline import (
    PageMaker,
    FailedValidation,
)
from psynet.trial.create_and_rate import CreateTrialMixin
from psynet.trial.imitation_chain import ImitationChainTrial

from .custom_front_end import (
    HelloPrompt,
    PositioningControl,
)
from .helper_classes import RewardProcessing
from .custom_pages import (
    WellBeingReportPage,
    SliderSettingPage,
)
from .helper_functions import get_world_wealth_slider_from_node

logger = get_logger()

###########################################
# Coordinator classes
###########################################


########################
# Pages

class InvestingPage(ModularPage):
    def __init__(
            self,
            time_estimate: float,
    ) -> None:

        information_text = Markup("""
        <h3>Page (2/6)</h3>
        <p>You have to invest a percentage of your endowment to obtain information about the location of the resources.
        The percentage you invest corresponds to the probability that each coin is shown in your map.
        Move the slider to determine the percentage of your endowment that you want to invest.</p>
        """)
        super().__init__(
            "Coordinator_information_gathering",
            Prompt(
                text=information_text,
            ),
            SliderControl(
                start_value=0.5,
                min_value=0,
                max_value=1,
                n_steps=100,
            ),
            time_estimate=time_estimate,
            save_answer="investment"
        )

    def format_answer(self, raw_answer, **kwargs) -> str:
        try:
            investment = float(raw_answer)
            logger.info(f"------> The coordinator invests: {investment*100}%")
            return raw_answer
        except (ValueError, AssertionError) as e:
            logger.info(f"Error: {e}")
            return f"INVALID_RESPONSE"

    def validate(self, response, **kwargs) -> Union[FailedValidation, None]:
        logger.info(f"Validating...")
        if response.answer == "INVALID_RESPONSE":
            logger.info(f"Invalid response!")
            return FailedValidation(f"This failed for some reason.")
        logger.info(f"Validated!")
        return None


########################
# Trial

class CoordinatorTrial(CreateTrialMixin, ImitationChainTrial):
    time_estimate = 5
    accumulate_answers = True

    def show_trial(self, experiment, participant) -> List[Any]:
        # import pydevd_pycharm
        # pydevd_pycharm.settrace('localhost', port=12345, stdout_to_server=True, stderr_to_server=True)

        logger.info("Entering the coordinator trial...")

        # Extract variables from node
        if hasattr(self, "origin"):
            # Extract world, wealth, slider values
            world, world_slider, wealth = get_world_wealth_slider_from_node(self.origin)
            world.map_path = Path(self.context["map_url"])
            world.coin_path = Path(self.context["coin_url"])
            world.forager_path = Path(self.context["forager_url"])
            logger.info(f"Overhead: {world_slider.get_overhead()}")
        else:
            raise Exception("Error: No world created for this trial.")

        list_of_pages = [
            InfoPage(
                Markup("""
                <h3>Page (1/6)</h3>
                <p>This is going to be the Instructions page for the COORDINATOR</p>
                """),
                time_estimate=5
            ),
            InvestingPage(
                time_estimate=self.time_estimate,
            ),
            PageMaker(
                lambda participant: ModularPage(
                    "custom_front_end_to_position_foragers",
                    HelloPrompt(
                        username="Coordinator",
                        text=Markup(
                            """
                            <h3>Page (3/6)</h3>
                            <p>Please position all the foragers on the map below.</p>
                            """
                        )
                    ),
                    PositioningControl(
                        world=world,
                        investment=participant.vars['investment'],
                    ),
                    time_estimate=self.time_estimate,
                    save_answer="forager_positions"
                ),
                time_estimate=self.time_estimate,
            ),
            InfoPage(
                RewardProcessing.get_reward_text(
                    n_coins=wealth,
                    slider=world_slider,
                    trial_type="coordinator"
                ),
                time_estimate=5
            ),
            # WellBeingReportPage(
            #     time_estimate=self.time_estimate,
            # ),
            SliderSettingPage(
                dimension="overhead",
                start_value=world_slider.get_overhead(),
                time_estimate=self.time_estimate,
            ),
            # SliderSettingPage(
            #     dimension="wages-commission",
            #     start_value=world_slider.get_wages_commission(),
            #     time_estimate=self.time_estimate,
            # ),
            # SliderSettingPage(
            #     dimension="prerogative",
            #     start_value=world_slider.get_coordinator_prerogative(),
            #     time_estimate=self.time_estimate,
            # ),
        ]
        return list_of_pages

###########################################