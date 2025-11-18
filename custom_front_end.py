# Module with custom prompts and controls

##########################################################################################
# Imports
##########################################################################################
from typing import Union
from markupsafe import Markup

from psynet.modular_page import (
    Prompt, 
    ImagePrompt,
    Control,
)
from psynet.utils import get_logger

from .helper_classes import World
from .game_parameters import NUM_COINS

logger = get_logger()

###########################################
# Custom prompts
###########################################

def positioning_prompt(text, img_url) -> Prompt:
    return ImagePrompt(
        url=img_url,
        text=Markup(text),
        width="475px",
        height="300px",
    )

class HelloPrompt(Prompt):
    macro = "with_hello"
    external_template = "custom-prompts.html"

    def __init__(
            self,
            username: str,
            text: Union[None, str, Markup] = None,
            text_align: str = "left",
    ) -> None:
        super().__init__(text=text, text_align=text_align)
        self.username = username


###########################################
# Custom controls
###########################################

class PositioningControl(Control):
    macro = "positioning_area"
    external_template = "custom-controls.html"

    def __init__(
        self,
        world:World,
        investment:int,
    ) -> None:
        super().__init__()
        map_numpy = world.render(
            show=False,
            coin_percentage=investment,
            coin_zoom=1 / NUM_COINS
        )
        self.map = map_numpy.tolist()
        self.forager_url = world.forager_path
        self.num_foragers = world.num_foragers

    def format_answer(self, raw_answer, **kwargs):
        logger.info(f"Foragers positions: {raw_answer}")
        return raw_answer

###########################################
