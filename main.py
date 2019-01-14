from pyTwistyScrambler import scrambler222

def get_scramble(n=2):
    if n == 2:
        return scrambler222.get_optimal_scramble().split(' ' )
    raise ValueError("Unsupported cube size")

