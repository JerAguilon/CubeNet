#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import numpy as np
import py222

from pyTwistyScrambler import scrambler222

hO = np.ones(2186, dtype=np.int) * 12
hP = np.ones(823543, dtype=np.int) * 12

moveStrs = {
    0: 'U',
    1: "U'",
    2: 'U2',
    3: 'R',
    4: "R'",
    5: 'R2',
    6: 'F',
    7: "F'",
    8: 'F2',
    }


# generate pruning table for the piece orientation states

def genOTable(s, d, lm=-3):
    index = py222.indexO(py222.getOP(s))
    if d < hO[index]:
        hO[index] = d
        for m in range(9):
            if int(m / 3) == int(lm / 3):
                continue
            genOTable(py222.doMove(s, m), d + 1, m)


# generate pruning table for the piece permutation states

def genPTable(s, d, lm=-3):
    index = py222.indexP(py222.getOP(s))
    if d < hP[index]:
        hP[index] = d
        for m in range(9):
            if int(m / 3) == int(lm / 3):
                continue
            genPTable(py222.doMove(s, m), d + 1, m)


# IDA* which prints all optimal solutions

def IDAStar(
    s,
    d,
    moves,
    lm=-3,
    ):
    if py222.isSolved(s):

    # printMoves(moves)

        return (True, 1)
    else:
        sOP = py222.getOP(s)
        total = 0

        if d > 0 and d >= hO[py222.indexO(sOP)] and d \
            >= hP[py222.indexP(sOP)]:
            dOptimal = False
            for m in range(9):
                if int(m / 3) == int(lm / 3):
                    continue
                newMoves = moves[:]
                newMoves.append(m)
                (solved, new_total) = IDAStar(py222.doMove(s, m), d
                        - 1, newMoves, m)
                total += new_total
                if solved and not dOptimal:
                    dOptimal = (True, total)
            if dOptimal:
                return (True, total)
    return (False, total)


# print a move sequence from an array of move indices

def printMoves(moves):
    moveStr = ''
    for m in moves:
        moveStr += moveStrs[m] + ' '
    print(moveStr)


# solve a cube state

def solveCube(s):

  # print cube state
  # py222.printCube(s)

  # FC-normalize stickers
  # print("normalizing stickers...")

    s = py222.normFC(s)

  # generate pruning tables
  # print("generating pruning tables...")

    genOTable(py222.initState(), 0)
    genPTable(py222.initState(), 0)

  # run IDA*
  # print("searching...")

    solved = False
    depth = 1
    total = 0
    while depth <= 11 and not solved:

    # print("depth {}".format(depth))

        (solved, new_total) = IDAStar(s, depth, [])
        total += new_total
        depth += 1
    return total


def get_scramble(n=2):
    if n == 2:
        return scrambler222.get_optimal_scramble().split(' ')
    raise ValueError('Unsupported cube size')


def generate_case(moves=10):
    if moves > 10:
        raise ValueError('Only up to 10 moves supported')
    scramble = get_scramble()[0:moves]
    return scramble


if __name__ == '__main__':

    import pickle
    scrambles = []
    for scramble_length in range(1, 10):
        print("Processing scrambles of length " + str(scramble_length))
        for i in range(50000):
            if i % 1000 == 0:
                print("{}/{}".format(i, 50000))
                print("Found {} scrambles".format(len(scrambles)))
            scramble = generate_case(scramble_length)
            s = py222.doAlgStr(py222.initState(), ' '.join(scramble))

            total = solveCube(s)
            if total == 1:
                scrambles.append(scramble)
    print("Found {} scrambles".format(len(scrambles)))
    with open('scrambles.pkl', 'wb') as fp:
        pickle.dump(scrambles, fp)
