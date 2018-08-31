import numpy as np 
from bulletscreen import Point, PointCrowd
from ai import AI

class SelfplayEngine:
    def __init__(self, ai, verbose):
        self.ai = ai
        self.state_shape = state_shape
        self.verbose = verbose

        # Train data
        self.boards = list()
        self.states = list()
        self.actions = list()
        self.values = list()

    def get_state(self):
        return self.states[-1]

    def update_states(self):

    def start(self):

        return dataset

class TrainAI:
    def __init__(self, state_shape, ai=None, verbose=False):
        self.state_shape = state_shape
        self.verbose = verbose
        
        if ai is not None:
            self.ai = ai
        else:
            self.ai = AI(
                state_shape=state_shape,
                action_dim=5,
                verbose=self.verbose
            )

    def get_selfplay_data(self, n_round):

    def update_ai(self, dataset):

    def start(self, filename):
