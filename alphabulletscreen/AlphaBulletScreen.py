import numpy as np 
import argparse

__version__ = "0.0.1"
__author__ = "Yang Long"
__info__ = "Play BulletScreen Game with AI"


__default_board_shape__ = 10, 10
__default_n_grid__ = 31
__default_state_shape__ = __default_n_grid__, __default_n_grid__, 3
__filename__ = "model.h5"

if __name__=='__main__':

    parser = argparse.ArgumentParser(description=__info__)

    parser.add_argument("--retrain", action='store_true', default=False, help="Re-Train AI")
    parser.add_argument("--train",  action='store_true', default=False, help="Train AI")
    parser.add_argument("--verbose", action='store_true', default=False, help="Verbose")
    parser.add_argument("--playbyai", action='store_true', default=False, help="Play by AI")
    parser.add_argument("--play", action='store_true', default=False, help="Play by human")

    args = parser.parse_args()
    verbose = args.verbose

    if args.train:
        if verbose:
            print("Continue to train AI model with game board size: [{0}] and state vector: [{1}].".format(
                __default_board_shape__,
                __default_state_shape__
            ))

        from ai import AI
        from train import TrainAI

        ai = AI(state_shape=__default_state_shape__, action_dim=5, verbose=verbose)
        if verbose:
            print("loading latest model: [{0}] ...".format(__filename__),end="")
        ai.load_nnet(__filename__)
        if verbose:
            print("load OK!")

        trainai = TrainAI(
            state_shape=__default_state_shape__,
            ai=ai,
            verbose=verbose
        )
        trainai.start(filename=__filename__)

        if verbose:
            print("The latest AI model is saved as [{0}]".format(__filename__))

    if args.retrain:
        if verbose:
            print("Start to retrain AI model with game board size: [{0}] and state vector: [{1}].".format(
                __default_board_shape__,
                __default_state_shape__
            ))

        from train import TrainAI

        trainai = TrainAI(
            state_shape=__default_state_shape__,
            verbose=verbose
        )
        trainai.start(filename=__filename__)

        if verbose:
            print("The latest AI model is saved as [{0}]".format(__filename__))

    if args.playbyai:
        if verbose:
            print("Start to play the game by the AI model...")

        from ai import AI
        from bulletscreen import BulletScreen

        ai = AI(state_shape=__default_state_shape__, action_dim=5, verbose=verbose)
        if verbose:
            print("loading latest model: [{0}] ...".format(__filename__),end="")

        ai.load_nnet(__filename__)

        if verbose:
            print("load OK!")

        print("Play BulletScreen game. Please close game in terminal after closing window (i.e, Press Ctrl+C).")
        bulletscreen = BulletScreen(state_shape=__default_state_shape__, ai=ai, verbose=verbose)
        bulletscreen.start_ai()

    if args.play:
        print("Play BulletScreen game. Please close game in terminal after closing window (i.e, Press Ctrl+C).")
        from bulletscreen import BulletScreen

        bulletscreen = BulletScreen(state_shape=__default_state_shape__, verbose=verbose)
        bulletscreen.start()