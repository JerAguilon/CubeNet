from MagicCube.cube import Cube
from pyTwistyScrambler import scrambler222
from enum import Enum

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import normalize

import numpy as np
import pandas as pd

c = Cube(2)

front_left_top =   [ [2, 0, 1], [5, 1, 1], [0, 0, 0] ]
front_right_top =  [ [2, 1, 1], [4, 0, 1], [0, 1, 0] ]
front_left_down =  [ [2, 0, 0], [5, 1, 0], [1, 0, 1] ]
front_right_down = [ [2, 1, 0], [4, 0, 0], [1, 1, 1] ]
back_left_top =    [ [3, 1, 1], [5, 0, 1], [0, 0, 1] ]
back_right_top =   [ [3, 0, 1], [4, 1, 1], [0, 1, 1] ]
back_left_down =   [ [3, 1, 0], [5, 0, 0], [1, 0, 0] ]
back_right_down =  [ [3, 0, 0], [4, 1, 0], [1, 1, 0] ]

all_pieces = [
    front_left_top,
    front_right_top,
    front_left_down,
    front_right_down,
    back_left_top,
    back_right_top,
    back_left_down,
    back_right_down,
]

class PieceColors(Enum):
    WHITE_BLUE_RED=0
    WHITE_BLUE_ORANGE=1
    WHITE_GREEN_RED=2
    WHITE_GREEN_ORANGE=3
    YELLOW_BLUE_RED=4
    YELLOW_BLUE_ORANGE=5
    YELLOW_GREEN_RED=6
    YELLOW_GREEN_ORANGE=7

piece_color_mapping = {
    (0, 2, 5): PieceColors.WHITE_BLUE_RED,
    (0, 2, 4): PieceColors.WHITE_BLUE_ORANGE,
    (0, 3, 5): PieceColors.WHITE_GREEN_RED,
    (0, 3, 4): PieceColors.WHITE_GREEN_ORANGE,
    (1, 2, 5): PieceColors.YELLOW_BLUE_RED,
    (1, 2, 4): PieceColors.YELLOW_BLUE_ORANGE,
    (1, 3, 5): PieceColors.YELLOW_GREEN_RED,
    (1, 3, 4): PieceColors.YELLOW_GREEN_ORANGE
}

def get_scramble(n=2):
    if n == 2:
        return scrambler222.get_optimal_scramble().split(' ')
    raise ValueError("Unsupported cube size")


def get_block_colors(colors):
    colors = tuple(sorted(list(colors)))
    return piece_color_mapping[colors]


num_classes = 9
one_hot = np.identity(9)
possible_moves = ['F', "F'", 'F2', 'R', "R'", 'R2', 'U', "U'", 'U2']
move_mapping = dict(
    [(move, i) for i, move in enumerate(
        possible_moves
    )]
)

def convert_move(m):
    return {
        "F" : ('F', 0, 1),
        "F'" : ('F', 0, -1),
        "F2": ('F', 0, 2),
        "B" : ('B', 0, 1),
        "B'": ('B', 0, -1),
        "B2": ('B', 0, 2),
        "L": ('L', 0, 1),
        "L'": ('L', 0, -1),
        "L2": ('L', 0, 2),
        "R": ('R', 0, 1),
        "R'": ('R', 0, -1),
        "R2": ('R', 0, 2),
        "U": ('U', 0, 1),
        "U'": ('U', 0, -1),
        "U2": ('U', 0, 2),
        "D": ('D', 0, 1),
        "D'": ('D', 0, -1),
        "D2": ('D', 0, 2),
    }[m]

def counter_move(m):
    return {
        "F": "F'",
        "F'": "F",
        "B'": "B'",
        "B": "B",
        "R": "R'",
        "R'": "R",
        "L": "L'",
        "L'": "L",
        "U": "U'",
        "U'": "U",
        "D": "D'",
        "D'": "D",
        "F2": "F2",
        "B2": "B2",
        "R2": "R2",
        "L2": "L2",
        "U2": "U2",
        "D2": "D2",
    }[m]

def generate_case(moves=10):
    if moves > 10:
        raise ValueError("Only up to 10 moves supported")
    scramble = get_scramble()[0:moves]
    undo_scramble = [counter_move(m) for m in reversed(scramble)]
    return scramble, undo_scramble

def unfold_case(scramble, undo_scramble):
    c = Cube(2)
    n = len(scramble)
    X_stickers = np.zeros( (n, 12, 2, 1) )
    X_pieces = np.zeros((n, 8))
    y = np.zeros(n)
    for i in range(n):
        c.move(*convert_move(scramble[n - i - 1]))
        solution = undo_scramble[i]
        stickers = c.stickers.copy()
        state = np.asarray(stickers).reshape(12, 2, 1)
        X_stickers[i] = state
        for j, piece in enumerate(all_pieces):
            piece_stickers = []
            for sticker_pos in piece:
                sticker_color = stickers[
                    sticker_pos[0], sticker_pos[1], sticker_pos[2]
                ]
                piece_stickers.append(sticker_color)
            X_pieces[i][j] = get_block_colors(piece_stickers).value
        y[i] = move_mapping[solution]
    return X_stickers, X_pieces, y


def data_generator(solves=5000):
    stickers = []
    pieces = []
    solutions = []
    for i in range(solves):
        if i % 100 == 0:
            print(f'{i}/{solves} completed')
        scramble, reverse = generate_case(moves=10)
        s, p, y = unfold_case(scramble, reverse)
        stickers.append(s)
        pieces.append(p)
        solutions.append(y)
    stickers = np.concatenate(stickers, axis=0)
    pieces = np.concatenate(pieces, axis=0)
    solutions = np.concatenate(solutions, axis=0)
    return stickers, pieces, solutions


SAVE_STICKERS = "data/train_stickers.npy"
SAVE_PIECES = "data/train_pieces.npy"
SAVE_SOLUTIONS = "data/train_solutions.npy"

if  __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(allow_abbrev=True)
    parser.add_argument(
        '--prefix',
        help="output data prefix",
        type=str,
    )

    parser.add_argument(
        '--suffix',
        help="output data suffix",
        type=str,
    )
    args = parser.parse_args()
    file_prefix = args.prefix if args.prefix else "data/train_"
    file_suffix = args.suffix if args.suffix else ""

    SAVE_STICKERS = "{}stickers{}.npy".format(file_prefix, file_suffix)
    SAVE_PIECES = "{}pieces{}.npy".format(file_prefix, file_suffix)
    SAVE_SOLUTIONS = "{}solutions{}.npy".format(file_prefix, file_suffix)


    print("Saving to: \n{}\n{}\n{}".format(
        SAVE_STICKERS, SAVE_PIECES, SAVE_SOLUTIONS))

    stickers, pieces, solutions = data_generator(solves=50000)

    np.save(SAVE_STICKERS, stickers)
    np.save(SAVE_PIECES, pieces)
    np.save(SAVE_SOLUTIONS, solutions)
