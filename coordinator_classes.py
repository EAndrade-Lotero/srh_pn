# Module with the coordinator classes

##########################################################################################
# Imports
##########################################################################################
from pathlib import Path
from typing import Any, Union, List

from psynet.modular_page import (
    ModularPage,
    Prompt,
    SliderControl,
)
from psynet.trial.imitation_chain import ImitationChainTrial
from psynet.trial.create_and_rate import CreateTrialMixin
from psynet.timeline import FailedValidation
from psynet.utils import get_logger
from psynet.page import  InfoPage

from .custom_front_end import (
    HelloPrompt,
    PositioningControl,
)
from .game_parameters import (
    NUM_FORAGERS,
    NUM_COINS,
    DISTRIBUTION,
    DISPERSION,
    IMAGE_PATHS,
)
from .helper_classes import (
    World,
    RewardProcessing,
    SliderValues,
)

logger = get_logger()

###########################################
# Coordinator classes
###########################################

class InvestingPage(ModularPage):
    def __init__(
            self,
            time_estimate: float,
    ) -> None:

        information_text = '''
        You have to invest a percentage of your endowment to obtain information about the location of the resources.
        The percentage you invest corresponds to the probability that each coin is shown in your map.
        Move the slider to determine the percentage of your endowment that you want to invest.
        '''
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
        )

    def format_answer(self, raw_answer, **kwargs) -> str:
        try:
            # numbers = re.findall(r"-?\d+", raw_answer)
            # assert len(numbers) == self.num_foragers
            # numbers = [int(n) for n in numbers]
            # logger.info(f"------> numbers input: {numbers}")
            # return numbers
            investment = float(raw_answer)
            logger.info(f"------> The coordinator invests: {investment*100}%")

            # Create the world visualizing the chosen percentage of coins
            world = World(
                num_coins=NUM_COINS,
                num_centroids=NUM_FORAGERS,
                distribution=DISTRIBUTION,
                dispersion=DISPERSION,
            )
            world.map_path = Path(IMAGE_PATHS["map_url"])
            world.coin_path = Path(IMAGE_PATHS["coin_url"])
            world.render(
                show=False,
                coin_percentage=investment,
                coin_zoom=1 / NUM_COINS
            )

            return "OK"

        except (ValueError, AssertionError):
            return f"INVALID_RESPONSE"

    def validate(self, response, **kwargs) -> Union[FailedValidation, None]:
        logger.info(f"Validating...")
        if response.answer == "INVALID_RESPONSE":
            logger.info(f"Invalid response!")
            return FailedValidation(f"This failed for some reason.")
        logger.info(f"Validated!")
        return None


class WellBeingReportPage(ModularPage):
    def __init__(
            self,
            time_estimate: float,
    ) -> None:

        information_text = '''
        Please move the slider below to match your level of satisfaction with the result
        '''
        super().__init__(
            "Coordinator_well-being_report",
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
        )

    def format_answer(self, raw_answer, **kwargs) -> Union[float, str]:
        try:
            coordinator_well_being = float(raw_answer)
            logger.info(f"------> The coordinator reports a {coordinator_well_being*100}% well-being")
            return coordinator_well_being

        except (ValueError, AssertionError):
            return f"INVALID_RESPONSE"

    def validate(self, response, **kwargs) -> Union[FailedValidation, None]:
        logger.info(f"Validating...")
        if response.answer == "INVALID_RESPONSE":
            logger.info(f"Invalid response!")
            return FailedValidation(f"This failed for some reason.")
        logger.info(f"Validated!")
        return None


class SliderSettingPage(ModularPage):
    def __init__(
            self,
            dimension: str,
            slider: SliderValues,
            time_estimate: float,
    ) -> None:
        assert(dimension in ["overhead", "wages-commission", "prerogative"]), f"Invalid dimension: {dimension}. Expected 'overhead', 'wages-commission' or 'prerogative'"

        information_text = f'''
        You can modify the parameters of the social contract established so far.
        This is the place to modify the {dimension} parameter.
        {SliderValues.dimension_explanation(dimension)}.
        Please move the slider below to match the new level of {dimension}.
        '''
        self.dimension = dimension

        if dimension == "overhead":
            start_value = slider.overhead
        elif dimension == "wages-commission":
            start_value = slider.wages_commission
        elif dimension == "prerogative":
            start_value = slider.coordinator_prerogative
        else:
            raise ValueError(f"Invalid dimension: {dimension}. Expected 'overhead', 'wages-commission', 'prerogative'.")

        super().__init__(
            "parameter_modification",
            Prompt(
                text=information_text,
            ),
            SliderControl(
                start_value=start_value,
                min_value=0,
                max_value=1,
                n_steps=100,
            ),
            time_estimate=time_estimate,
        )

    def format_answer(self, raw_answer, **kwargs) -> Union[float, str]:
        try:
            new_value = float(raw_answer)
            logger.info(f"------> The coordinator sets {self.dimension} to {new_value}%.")
            return new_value

        except (ValueError, AssertionError):
            return f"INVALID_RESPONSE"

    def validate(self, response, **kwargs) -> Union[FailedValidation, None]:
        logger.info(f"Validating...")
        if response.answer == "INVALID_RESPONSE":
            logger.info(f"Invalid response!")
            return FailedValidation(f"This failed for some reason.")
        logger.info(f"Validated!")
        return None



class CoordinatorTrial(CreateTrialMixin, ImitationChainTrial):
    time_estimate = 5
    accumulate_answers = True

    def show_trial(self, experiment, participant) -> List[Any]:
        # import pydevd_pycharm
        # pydevd_pycharm.settrace('localhost', port=12345, stdout_to_server=True, stderr_to_server=True)

        logger.info("Entering the coordinator trial...")

        slider = experiment.var.slider
        logger.info(f"===>{slider}")

        list_of_pages = [
            InfoPage(
                "This is going to be the Instructions page for the COORDINATOR",
                time_estimate=5
            ),
            InfoPage(
                RewardProcessing.get_reward_text(experiment, "coordinator"),
                time_estimate=5
            ),
            WellBeingReportPage(
                time_estimate=self.time_estimate,
            ),
            InvestingPage(
                time_estimate=self.time_estimate,
            ),
            ModularPage(
                "custom_front_end_to_position_foragers",
                HelloPrompt(
                    username="Coordinator",
                    text="Please position all the foragers on the map below."
                ),
                PositioningControl(
                    map_url=self.context["map_url"],
                    forager_url=self.context["forager_url"],
                    num_foragers=NUM_FORAGERS,
                ),
                time_estimate=self.time_estimate
            ),
            SliderSettingPage(
                dimension="overhead",
                slider=slider,
                time_estimate=self.time_estimate,
            )
        ]
        return list_of_pages

###########################################