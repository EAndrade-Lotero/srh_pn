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
        map_url:str,
        forager_url:str,
        num_foragers:int,
    ) -> None:
        super().__init__()
        self.map_url = map_url
        self.forager_url = forager_url
        self.num_foragers = num_foragers

    def format_answer(self, raw_answer, **kwargs):
        logger.info(f"Foragers positions: {raw_answer}")
        return raw_answer

###########################################
