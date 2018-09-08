import numpy as np 
import time
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

        return 

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

        self.losses = list()

    def get_selfplay_data(self, n_rounds):
        states = list()
        actions = list()
        values = list()

        if self.verbose:
            starttime = time.time()
            print("Start self-play process with rounds [{0}]:".format(n_rounds))

        for i in range(n_rounds):
            if self.verbose:
                print("{0}th self-play round...".format(i+1))

            engine = SelfplayEngine(
                ai=self.ai,
                verbose=self.verbose
            )

            _states, _actions, _values = engine.start()
            for i in range(_actions):
                states.append(_states[i])
                actions.append(_actions[i])
                values.append(_values[i])
        
        if self.verbose:
            endtime = time.time()
            print("End of self-play process with data size [{0}] and cost time [{1:.1f}s].".format(
                len(values),  (endtime - starttime)))

        return states, actions, values

    def update_ai(self, dataset):
        if self.verbose:
            print("Start to update the network of AI model...")

        history = self.ai.train(dataset, epochs=30, batch_size=32)

        if self.verbose:
            print("End of updating with final loss [{0:.4f}]".format(history.history['loss'][-1]))

        return history

    def start(self, filename):
        '''
        Main training process
        '''
        n_epochs = 1000
        n_rounds = 20
        n_checkpoints = 30

        if self.verbose:
            print("Train AI model with epochs: [{0}]".format(n_epochs))
        
        for i in range(n_epochs):
            if self.verbose:
                print("{0}th self-play training process ...".format(i+1))

            dataset = self.get_selfplay_data(n_rounds)

            history = self.update_ai(dataset)
            self.losses.extend(history.history['loss'])

            if self.verbose:
                print("End of training process.")

            if (i+1)%n_checkpoints == 0:
                if self.verbose:
                    print("Checkpoint: Saving AI model with filename [{0}] ...".format(filename),end="")

                self.ai.save_nnet(filename)

                if self.verbose:
                    print("OK!")