# CubeNet

Can we create a neural net architecture that solves a Rubik's Cube?

The current goal is to solve a 2x2x2, but with more complex networks or perhaps Deep Reinforcement Learning, we
may be able to scale to a 3x3x3.

For reference, a 2x2x2 has "only" **3.5 million** states. A 3x3x3 **43 quintillion (43E18)** states.

## State of this project

74% accuracy has been achieved by generating random scrambles and passing states/the reverse move into
the neural net. As a high level example:

`Scramble: R U R' U'` This scramble clearly generates 4 different cube states with
`Solutions: R' U' R U`. We generate a 4x6x2x2 array of the stickers, flatten it into 4x24,
and pass that into the architecture.

74% is not sufficient to solve a cube. Naively, if the predictions are uniformly accurate for all
states, a scramble of 4 moves only has a .74^4=28% chance of being solved perfectly. Of course,
this assumption breaks since there are many paths to a solved cube, but tests have shown
that the neural net is inconsistent in performance.

## Further approaches

1. Attempt to train on solutions that have **1 unique optimal solution**. A corpus of scrambles that have 
   this property has been developed. Perhaps this will help the network generalize.
2. Implement deep-Q learning
