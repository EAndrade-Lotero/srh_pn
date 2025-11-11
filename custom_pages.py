# Module with the custom pages
##########################################################################################
# Imports
##########################################################################################
from typing import Union

import psynet.experiment
from psynet.utils import get_logger
from psynet.timeline import FailedValidation

from psynet.modular_page import (
    ModularPage,
    Prompt,
    SliderControl,
)

from .helper_classes import SliderValues

logger = get_logger()

###########################################
# Custom pages
###########################################

class WellBeingReportPage(ModularPage):
    def __init__(
            self,
            time_estimate: float,
    ) -> None:

        information_text = '''
        Please move the slider below to match your level of satisfaction with your reward.
        '''
        super().__init__(
            "Well-being_report",
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

        except (ValueError, AssertionError) as e:
            logger.info(f"Oooops: {e}")
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
            experiment: psynet.experiment.Experiment,
            time_estimate: float,
    ) -> None:
        assert(dimension in ["overhead", "wages-commission", "prerogative"]), f"Invalid dimension: {dimension}. Expected 'overhead', 'wages-commission' or 'prerogative'"

        information_text = f'''
        You can modify the parameters of the social contract established so far.
        This is the place to modify the {dimension} parameter.
        {SliderValues.dimension_explanation(dimension)}.
        The slider below displays the current level of {dimension}. Please move it to match your desired level of {dimension}.
        '''
        self.dimension = dimension
        self.experiment = experiment
        slider = experiment.var.slider

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
            logger.info(f"------> The {self.dimension} has been set to {new_value}%.")
            slider = self.experiment.var.slider
            if self.dimension == "overhead":
                slider.update_overhead(new_value)
            elif self.dimension == "wages-commission":
                slider.update_wages_commission(new_value)
            elif self.dimension == "prerogative":
                slider.update_coordinator_prerogative(new_value)
            else:
                raise ValueError(
                    f"Invalid dimension: {self.dimension}. Expected 'overhead', 'wages-commission', 'prerogative'.")

            self.experiment.var.set("slider", slider)
            return new_value

        except (ValueError, AssertionError) as e:
            logger.info(f"Oooops: {e}")
            return f"INVALID_RESPONSE"

    def validate(self, response, **kwargs) -> Union[FailedValidation, None]:
        logger.info(f"Validating...")
        if response.answer == "INVALID_RESPONSE":
            logger.info(f"Invalid response!")
            return FailedValidation(f"This failed for some reason.")
        logger.info(f"Validated!")
        return None