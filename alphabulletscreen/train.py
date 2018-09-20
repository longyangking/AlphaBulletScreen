import numpy as np 
import time
from bulletscreen import GameEngine
from ai import AI

class SelfplayEngine:
    def __init__(self, ai, verbose):
        self.ai = ai
        self.state_shape = ai.get_state_shape()
        self.verbose = verbose

        # Train data
        self.areas = list()
        self.states = list()
        self.actions = list()
        self.values = list()

    def get_state(self):
        return self.states[-1]

    def update_states(self):
        '''
        Update stored states
        '''
        Nx, Ny, channel = self.state_shape
        state = np.zeros((Nx,Ny,channel))
        n_areas = len(self.areas)
        for i in range(channel):
            if i+1 <= n_areas:
                state[:,:,-(i+1)] = self.areas[-(i+1)]

        self.states.append(state)
        
    def start(self):
        '''
        Main process for self-play engine
        '''
        n_grid = self.state_shape[0]

        n_points=10
        bounds = [-5, 5, -5, 5] # bounds: [x_min, x_max, y_min, y_max]
        velocity_max = 2.0
        velocity_min = 1.0
        dt = 0.1
        target_position = np.array([0,0]) 
        target_speed = 2.0
        n_crowds=3
        timestep_intervals=10

        gameengine = GameEngine(
            n_points=n_points, 
            bounds=bounds, 
            velocity_max=velocity_max, 
            velocity_min=velocity_min,
            dt=dt, 
            target_position=target_position, 
            target_speed=target_speed,
            n_crowds=n_crowds, 
            timestep_intervals=timestep_intervals,
            n_grid=n_grid,
            verbose=False   # Inner process, not shown
        )

        gameengine.init()
        # area = gameengine.get_area(n_grid)
        # self.areas.append(area)

        while not gameengine.update():
            area = gameengine.get_area()
            self.areas.append(area)
            self.update_states()

            action, action_values = self.ai.evaluate_function(self.get_state())

            control_code = np.zeros(5)
            control_code[action] = 1
            gameengine.play(control_code=control_code)

            self.actions.append(action)
            score = gameengine.get_score()
            self.values.append(score)

        GAMMA = 0.9
        action_values = list()
        for i in range(len(self.actions)-1):
            action_value = np.zeros(5)
            _, action_values_pred = self.ai.evaluate_function(self.states[i+1])
            action_value[self.actions[i]] = self.values[i] + GAMMA*np.max(action_values_pred)
            action_values.append(action_value)

        # Terminal action, which would not gain the incomings in the future
        action_value = np.zeros(5)
        action_value[self.actions[-1]] = self.values[-1]
        action_values.append(action_value)

        return self.states, action_values

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
        action_values = list()

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

            _states, _action_values = engine.start()
            for i in range(len(_action_values)):
                states.append(_states[i])
                action_values.append(_action_values[i])
        
        if self.verbose:
            endtime = time.time()
            print("End of self-play process with data size [{0}] and cost time [{1:.1f}s].".format(
                len(action_values),  (endtime - starttime)))

        states = np.array(states)
        action_values = np.array(action_values)

        return states, action_values

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
        n_rounds = 30
        n_checkpoints = 10

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