from enum import Enum

from pm4py.algo.discovery.est import variants
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.util import exec_utils

class Variants(Enum):
    EST_CLASSIC = variants.classic
    EST_INTERESTING_PLACES = variants.interesting_places

EST_VERSION_CLASSIC = Variants.EST_CLASSIC
EST_VERSION_INTERESTING_PLACES = Variants.EST_INTERESTING_PLACES
DEFAULT_VARIANT = EST_VERSION_CLASSIC
VERSIONS = {EST_VERSION_CLASSIC, EST_VERSION_INTERESTING_PLACES}

def apply(log, parameters=None, variant=EST_VERSION_CLASSIC):
    """
    Apply the eST-Miner on top of a log
    
        Parameters
    -----------
    log
        Log
    variant
        Variant of the algorithm to use:
            - Variants.EST_CLASSIC
            - Variants.EST_VERSION_INTERESTING_PLACES
    parameters
        Possible parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Name of the attribute that contains the activity

    Returns
    -----------
    net
        Petri net
    marking
        Initial marking
    final_marking
        Final marking
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG)) 
