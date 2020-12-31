from enum import Enum


from pm4py.util import xes_constants as xes_util


class Place:
    def __init__(self, input_activities=set(), output_activities=set()):
        self.input_activities = input_activities
        self.output_activities = output_activities


class Fitness(Enum):
    FITTING = 'fitting'
    OVERFED = 'overfed'
    UNDERFED = 'underfed'


class FitnessState:
    def __init__(self, fitness_properties=set()):
        self.fitness_properties = fitness_properties


def place_fitness_state(place, log, tau, activitiy_key=xes_util.DEFAULT_NAME_KEY):
    """
    Returns wether the place is overfed, underfed or fitting w.r.t.
    the log and tau.

    A place is underfed w.r.t. log L and 0 <= tau <= 1,
    if and only if size({sigma in L | underfed(p, sigma)}) / size(L) > 1 - tau

    A place is overfed w.r.t. log L and 0 <= tau <= 1,
    if and only if size({sigma in L | overfed(p, sigma)}) / size(L) > 1 - tau

    A place is fitting w.r.t. log L and 0 <= tau <= 1,
    if and only if size({sigma in L | fitting(p, sigma)}) / size(L) >= tau
    """
    num_underfed = 0
    num_overfed = 0
    num_fitting = 0
    for trace in log:
        is_underfed = underfed(place, trace, activitiy_key)
        is_overfed = overfed(place, trace, activitiy_key)
        is_fitting = not is_underfed and not is_overfed
        num_underfed += 1 if is_underfed else 0
        num_overfed += 1 if is_overfed else 0
        num_fitting += 1 if is_fitting else 0

    fitness_properties = set()
    if num_underfed / len(log) > 1 - tau:
        fitness_properties.add(Fitness.UNDERFED)
    if num_overfed / len(log) > 1 - tau:
        fitness_properties.add(Fitness.OVERFED)
    if num_fitting / len(log) >= tau:
        fitness_properties.add(Fitness.FITTING)
    return FitnessState(fitness_properties=fitness_properties)


def underfed(place, trace, activity_key):
    """
    Returns wether the place is underfed w.r.t. the given trace
    """
    tokens = 0
    for event in trace:
        activity = event[activity_key]
        if activity in place.output_activities:
            tokens -= 1
        if tokens < 0:  # turning negative: place is underfed w.r.t. trace
            return True
        if activity in place.input_activities:
            tokens += 1
    return False


def overfed(place, trace, activity_key):
    """
    Returns wether the place is overfed w.r.t. the given trace
    """
    tokens = 0
    for event in trace:
        activity = event[activity_key]
        if activity in place.output_activities:
            tokens -= 1
        if activity in place.input_activities:
            tokens += 1
    return tokens > 0  # tokens remaining: place is overfed w.r.t. trace
