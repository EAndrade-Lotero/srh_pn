# pylint: disable=unused-import,abstract-method,unused-argument
##########################################################################################
# Imports
##########################################################################################
import psynet.experiment
from psynet.utils import get_logger
from psynet.timeline import Timeline
from psynet.trial.create_and_rate import CreateAndRateTrialMakerMixin
from psynet.trial.imitation_chain import ImitationChainTrialMaker


from .coordinator_classes import CoordinatorTrial
from .forager_classes import ForagerTrial
from .custom_node import CustomNode
from .game_parameters import (
    NUM_FORAGERS,
    NUM_CENTROIDS,
    NUM_COINS,
    LIST_OF_DISTRIBUTIONS,
    DISPERSION,
    STARTING_OVERHEAD,
    STARTING_PREROGATIVE,
    STARTING_WAGES,
    INITIAL_WEALTH,
    MAX_NODES_PER_CHAIN,
    IMAGE_PATHS,
)
from .helper_classes import World

###########################################
# Variables
###########################################

# logger
logger = get_logger()

# Create list of initial nodes
start_nodes = [
    CustomNode(
        context=IMAGE_PATHS,
        seed={
            'world':World(
                num_coins=NUM_COINS,
                num_centroids=NUM_CENTROIDS,
                distribution=distribution,
                dispersion=DISPERSION,
            ),
            'overhead':STARTING_OVERHEAD,
            'prerogative':STARTING_PREROGATIVE,
            'wages':STARTING_WAGES,
            'wealth':INITIAL_WEALTH
        }
    )
    for distribution in LIST_OF_DISTRIBUTIONS
]

###########################################
# Experiment
###########################################

class CreateAndRateTrialMaker(CreateAndRateTrialMakerMixin, ImitationChainTrialMaker):
    pass

trial_maker = CreateAndRateTrialMaker(
    n_creators=1,
    n_raters=NUM_FORAGERS,
    node_class=CustomNode,
    creator_class=CoordinatorTrial,
    rater_class=ForagerTrial,
    # mixin params
    include_previous_iteration=True,
    rate_mode="select",
    target_selection_method="all",
    verbose=True,  # for the demo
    # trial_maker params
    id_="create_and_rate_basic",
    chain_type="across",
    expected_trials_per_participant=len(start_nodes),
    max_trials_per_participant=len(start_nodes),
    start_nodes=start_nodes,
    chains_per_experiment=len(start_nodes),
    balance_across_chains=False,
    check_performance_at_end=True,
    check_performance_every_trial=False,
    propagate_failure=False,
    recruit_mode="n_trials",
    target_n_participants=None,
    wait_for_networks=False,
    max_nodes_per_chain=MAX_NODES_PER_CHAIN,
)

class Exp(psynet.experiment.Experiment):
    label = "Social roles and hierarchies skeleton experiment"
    initial_recruitment_size = 1

    timeline = Timeline(
        trial_maker,
    )

    # test_n_bots = 6

###########################################