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


def place_fitness_state(place, log, activitiy_key=xes_util.DEFAULT_NAME_KEY):
    tokens = 0
    fitness_properties = set()
    for trace in log:
        for event in trace:
            activity = event[activitiy_key]
            if activity in place.output_activities:
                tokens -= 1
            if tokens < 0:
                fitness_properties.add(Fitness.UNDERFED)
            if activity in place.input_activities:
                tokens += 1
    if tokens > 0:
        fitness_properties.add(Fitness.OVERFED)
    elif tokens == 0 and Fitness.UNDERFED not in fitness_properties:
        fitness_properties.add(Fitness.FITTING)
    return FitnessState(fitness_properties=fitness_properties)
