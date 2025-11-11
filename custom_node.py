# Module with the custom node
##########################################################################################
# Imports
##########################################################################################

from psynet.trial import ChainNode
from psynet.trial.create_and_rate import CreateAndRateNodeMixin
from psynet.utils import get_logger

logger = get_logger()

###########################################
# Custom node
###########################################

class CustomNode(CreateAndRateNodeMixin, ChainNode):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_seed(self) -> str:
        return self.seed

    def create_definition_from_seed(self, seed, experiment, participant):
        return seed

    def summarize_trials(self, trials: list, experiment, participant):
        # import pydevd_pycharm
        # pydevd_pycharm.settrace('localhost', port=12345, stdout_to_server=True, stderr_to_server=True)

        # trial_maker = self.trial_maker
        # all_rate_trials = trial_maker.rater_class.query.filter_by(
        #     node_id=self.id, failed=False, finalized=True
        # ).all()
        # logger.info(f"All rate trials: {all_rate_trials}")
        #
        # rate_mode = trial_maker.rate_mode
        # logger.info(f"Rate mode: {rate_mode}")
        #
        # logger.info("")
        # logger.info("="*60)
        # trials_by_type = [type(trial) for trial in trials]
        # logger.info(f"trials: {trials_by_type}")
        # logger.info("")

        slider = experiment.var.slider
        accumulated_wealth = experiment.var.accumulated_wealth
        accumulated_wealth.update(trials, slider)
        experiment.var.set("accumulated_wealth", accumulated_wealth)

