"""
This module implements the \"interesting-places\" eST-Miner [1]_.
It takes the input event log, which should be a log and starts with a Petri net without any places.
In contrast to the classic eST-Miner, the interesting places extension does not find all
fitting places with respect to the given, but decides based on an heuristic dervied from the
eventually-follows relations if a fraction of the search space is actually interesting or not.
Doing so allows the algorithm to significantly reduce the time spend on traversing the search
space, while still deriving complex model structures that other algorithms fail to discover.

References
    ----------
    .. [1] Lisa L. Mannel, Yannick Epstein, and Wil M. P. van der Aalst, "Improving the State-Space Traversal of the eST-Miner by Exploiting Underlying Log Structures",
      18TH INT. CONFERENCE ON BUSINESS PROCESS MANAGEMENT (BPM 2020). `<https://feb.kuleuven.be/drc/LIRIS/misc/bpiworkshop/papers/paper_210.pdf>`_.
"""


def apply(log, parameters=None):
    return None, None, None
