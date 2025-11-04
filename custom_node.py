# Module with the custom node

##########################################################################################
# Imports
##########################################################################################

from psynet.trial import ChainNode
from psynet.trial.create_and_rate import CreateAndRateNodeMixin

###########################################
# Custom node
###########################################

class CustomNode(CreateAndRateNodeMixin, ChainNode):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        working_slider = experiment.var.slider
        working_slider.update_overhead(1)
        experiment.var.set("slider", working_slider)

        #implement!!!
        # take debugger here, and write a list comprehension that gets the right data from the trials
        # note that trials maybe of different types so maybe you need to check the type before accessing the data to avoid error
