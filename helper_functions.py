# Module with the helper functions

##########################################################################################
# Imports
##########################################################################################

from typing import List, Any, Tuple

import psynet
from psynet.utils import get_logger

from .helper_classes import (
    World,
    SliderValues
)

logger = get_logger()

###########################################
# Helper functions
###########################################

def get_world_wealth_slider_from_node(node: Any) -> Tuple[World, SliderValues, int]:
    # Extract world
    world = node.definition['world']
    # Extract wealth
    wealth = node.definition['wealth']
    # Extract slider values
    world_slider = SliderValues()
    world_slider.update_overhead(node.definition['overhead'])
    world_slider.update_wages_commission(node.definition['wages'])
    world_slider.update_coordinator_prerogative(node.definition['prerogative'])
    # Return values
    return world, world_slider, wealth

def get_list_participants_ids(
        experiment: psynet.experiment.Experiment, 
        participant: psynet.participant.Participant
    ) -> List[int]:
    
    # Get previous participant's ids
    participants_id = []
    for id in range(1, participant.id):
        try:
            p = experiment.get_participant_from_participant_id(id)
            if not p.failed:
                participants_id.append(id)
        except:
            pass
            logger.info(f"Id {id} is not valid!")

    logger.info(f"Participants: {participants_id}")

    return participants_id


# def test_check_bots(self, bots: List[Bot]):
#     time.sleep(2.0)

#     assert len([b for b in bots if b.var.participant_group == "A"]) == 3
#     assert len([b for b in bots if b.var.participant_group == "B"]) == 3

#     for b in bots:
#         assert len(b.alive_trials) == 7  # 4 normal trials + 3 repeat trials
#         assert all([t.finalized for t in b.alive_trials])

#     processes = AsyncProcess.query.all()
#     assert all([not p.failed for p in processes])

#     super().test_check_bots(bots)