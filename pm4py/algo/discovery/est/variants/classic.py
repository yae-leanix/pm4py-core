"""
This module implements the \"classic\" eST-Miner [1]_.
It takes the input event log, which should be a log and starts with a Petri net without any places.
The eST-Miner then continues to insert the maximal set of places considering fitting with respect
to the behavior described by the log. As traversing and evaluating the set of all possible places
is not feasible, the eST-Miner relies on a strategy to drastically prune the search space to a small
number of candidates, while still ensuring that all fitting places are found.
This allows the eST-Miner to derive complex model structures that other algorithms fail to discover.

References
    ----------
    .. [1] Lisa L. Mannel and Wil M. P. van der Aalst, "Finding Complex Process-Structures by Exploiting the Token-Game",
      Application and Theory of Petri Nets and Concurrency, 40th International Conference, 2019. `DOI <https://doi.org/10.1007/978-3-030-21571-2_15>`_.
"""


def apply(log, parameters=None):
    return None, None, None
