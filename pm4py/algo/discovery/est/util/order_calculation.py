from pm4py.util import xes_constants as xes_util


class Order:

    def __init__(self, activities):
        self._smaller_than = {a: set() for a in activities}

    def add_relation(self, larger=None, smaller=None):
        if (larger is not None and smaller is not None):
            self._smaller_than[smaller].add(larger)

    def is_smaller_than(self, smaller=None, larger=None):
        is_comparable = smaller is not None and larger is not None and smaller in self._smaller_than
        return larger in self._smaller_than[smaller] if is_comparable else False


def lexicographic_ordering(log, activity_key=xes_util.DEFAULT_NAME_KEY):
    sorted_activities = sorted(all_activities(log))
    order = Order(sorted_activities)
    for i in range(0, len(sorted_activities)):
        for j in range(i, len(sorted_activities)):
            larger = sorted_activities[j]
            smaller = sorted_activities[i]
            if larger != smaller:
                order.add_relation(larger=larger, smaller=smaller)
    return order


def all_activities(log, activity_key=xes_util.DEFAULT_NAME_KEY):
    return list(set(event[activity_key] for trace in log for event in trace))
