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


def absolute_activity_frequency_ordering(log, activity_key=xes_util.DEFAULT_NAME_KEY):
    """
    The absolute activity frequency is defined as
        absAF: A -> N, absAF(a) = sum_{sigma in L} size({i in {1, ..., len(sigma)} | sigma(i) = a })
    That is the absolute number of occurrences of the activity a in all traces sigma in the log.
    If absAF(a) is high, we expect many tokens to be produced (consumed) for places that have a as an
    ingoing (outgoing) activity during replay of the log, and thus such places are more likely to be
    underfed (overfed).
    """
    activities = all_activities(log)
    abs_activity_frequency = {a: 0 for a in activities}
    for a in activities:
        for trace in log:
            for event in trace:
                if event[activity_key] == a:
                    abs_activity_frequency[a] = abs_activity_frequency[a] + 1
    asc_sorted_activities = list({a: freq for (a, freq) in sorted(
        abs_activity_frequency.items(), key=lambda item: item[1])}.keys())
    return ordering_from_asc_sorted_activities(asc_sorted_activities)


def lexicographic_ordering(log, activity_key=xes_util.DEFAULT_NAME_KEY):
    asc_sorted_activities = sorted(all_activities(log))
    return ordering_from_asc_sorted_activities(asc_sorted_activities)


def ordering_from_asc_sorted_activities(sorted_activities):
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
