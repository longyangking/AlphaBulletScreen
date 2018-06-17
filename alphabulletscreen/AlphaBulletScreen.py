import numpy as np 
import argparse

__version__ = "0.0.1"
__author__ = "Yang Long"

if __name__=='__main__':
    info = """
            {name}
            [version:{version}, Author: {author}]
        """.format(
            name='AlphaBulletScreen',
            version=__version__,
            author=__author__
        )
    parser = argparse.ArgumentParser(description=info)

    parser.add_argument("--retrain", action='store_true', default=False, help="Re-Train AI")
    parser.add_argument("--train",  action='store_true', default=False, help="Train AI")
    parser.add_argument("--verbose", action='store_true', default=False, help="Verbose")
    parser.add_argument("--info", action='store_true', default=False, help="Show the process information")
    parser.add_argument("--playbyai", action='store_true', default=False, help="Play by AI")
    #parser.add_argument("--play-human", action='store_true', default=False, help="Play by human")

    args = parser.parse_args()
    verbose = args.verbose

    if args.train:
        print("Train AI")

    if args.retrain:
        print("Re-train AI")

    if args.playbyai:
        print("Play with AI!")