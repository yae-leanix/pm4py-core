from enum import Enum

from pm4py.util import xes_constants as xes_util


class OrderType(Enum):
    ASC = 'ascending'
    DESC = 'descending'


class Order:

    def __init__(self, activities):
        self._smaller_than = {a: set() for a in activities}

    def add_relation(self, larger=None, smaller=None):
        if (larger is not None and smaller is not None):
            self._smaller_than[smaller].add(larger)

    def is_smaller_than(self, smaller=None, larger=None):
        is_comparable = smaller is not None and larger is not None and smaller in self._smaller_than
        return larger in self._smaller_than[smaller] if is_comparable else False


class SearchSpaceOrdering:

    def __init__(self, input_ordering, output_ordering):
        self.input_ordering = input_ordering
        self.output_ordering = output_ordering


def search_space_ordering_based_on_absolute_activity_frequency(log, activity_key=xes_util.DEFAULT_NAME_KEY):
    """
    If absAF(a) is high, we expect many tokens to be produced (consumed) for places that
    have a as an ingoing (outgoing) activity during replay of log, and thus such places
    are more likely to be underfed (overfed).
    This means we want that both intput and output ordering should sort the activities descending
    based on their absAF, because this would mean that we visit places that are more
    likely to get pruned early on in our search.
    """
    input_ordering = output_ordering = absolute_activity_frequency_ordering(
        log, activity_key=activity_key, order_type=OrderType.DESC)
    return SearchSpaceOrdering(input_ordering, output_ordering)


def search_space_ordering_based_on_absolute_trace_frequency(log, activity_key=xes_util.DEFAULT_NAME_KEY):
    """
    If absTF(a) is high, we expect many tokens to be produced (consumed) for places that
    have a as an ingoing (outgoing) activity during replay of log, and thus such places
    are more likely to be underfed (overfed).
    This means we want that both intput and output ordering should sort the activities descending
    based on their absTF, because this would mean that we visit places that are more
    likely to get pruned early on in our search.
    """
    input_ordering = output_ordering = absolute_trace_frequency_ordering(
        log, activity_key=activity_key, order_type=OrderType.DESC)
    return SearchSpaceOrdering(input_ordering, output_ordering)


def search_space_ordering_based_on_average_first_occurrence_index(log, activity_key=xes_util.DEFAULT_NAME_KEY):
    """
    If avgFOI(a) is low, we can expect the activity a to generate or consume tokens early
    on during the replay of a trace. Places which have outgoing activities
    with low average first occurrence index are more likely to be underfed, as their output
    activities may require tokens early on during replay, where none might be available.
    This means we want the input ordering to sort the activities descending based on their avgFOI, while
    the output ordering should sort the activities ascending based on their avgFOI.
    This way we visit places early on, that have outgoing activities that require tokens early on during
    replay, while the outgoing activities only produce tokens late during replay.
    """
    input_ordering = average_first_occurrence_index_ordering(
        log, activity_key=activity_key, order_type=OrderType.DESC)
    output_ordering = average_first_occurrence_index_ordering(
        log, activity_key=activity_key, order_type=OrderType.ASC)
    return SearchSpaceOrdering(input_ordering, output_ordering)


def absolute_activity_frequency_ordering(log, activity_key=xes_util.DEFAULT_NAME_KEY, order_type=OrderType.ASC):
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
    return ordering_from_sorted_activities(sorted_activities(abs_activity_frequency, order_type=order_type))


def absolute_trace_frequency_ordering(log, activity_key=xes_util.DEFAULT_NAME_KEY, order_type=OrderType.ASC):
    """
    The absolute trace frequency is defined as
        absTF: A -> N, absTF(a) = size({ sigma in L | a in sigma})
    That is the absolute number of traces where a occurrs.
    If absTF(a) is high, we expect many tokens to be produced (consumed) for places that have a as an
    ingoing (outgoing) activity during replay of the log, and thus such places are more likely to be
    underfed (overfed).
    """
    abs_trace_frequency = absolute_trace_frequency(
        log, activity_key=activity_key)
    return ordering_from_sorted_activities(sorted_activities(abs_trace_frequency, order_type=order_type))


def absolute_trace_frequency(log, activity_key=xes_util.DEFAULT_NAME_KEY):
    activities = all_activities(log)
    abs_trace_frequency = {a: 0 for a in activities}
    for a in activities:
        for trace in log:
            contained_activities = set()
            for event in trace:
                contained_activities.add(event[activity_key])
            abs_trace_frequency[a] = abs_trace_frequency[a] + \
                (1 if a in contained_activities else 0)
    return abs_trace_frequency


def average_first_occurrence_index_ordering(log, activity_key=xes_util.DEFAULT_NAME_KEY, order_type=OrderType.ASC):
    """
    The average first occurrence index is defined as:
        avgFOI: A -> Q, avgFOI(a) = sum_{sigam in L} min({i in {1, 2, ..., len(sigma)} | sigma[i] = a}) / absTF(a)
    That is the first index in a trace where a is present, averaged over the number of traces where a occurrs.
    If avgFOI(a) is low, we can expect the activity a to generate or consume a token early on
    during replay of the trace. Places which have outgoing activities with low average first occurrence index
    are more likely to be underfed, as their output activities may require tokens early on during replay, where
    none might be available.
    """
    activities = all_activities(log)
    abs_trace_frequency = absolute_trace_frequency(
        log, activity_key=activity_key)
    avg_first_occurrence_index = {a: 0 for a in activities}
    for a in activities:
        for trace in log:
            for index, event in enumerate(trace, start=1):
                if event[activity_key] == a:
                    avg_first_occurrence_index[a] = avg_first_occurrence_index[a] + \
                        index / abs_trace_frequency[a]
                    break
    return ordering_from_sorted_activities(sorted_activities(avg_first_occurrence_index, order_type=order_type))


def sorted_activities(activity_metric, order_type=OrderType.ASC):
    reverse = order_type == OrderType.DESC
    return list({a: freq for (a, freq) in sorted(
        activity_metric.items(), key=lambda item: item[1], reverse=reverse)}.keys())


def lexicographic_ordering(log, activity_key=xes_util.DEFAULT_NAME_KEY, order_type=OrderType.ASC):
    reverse = order_type == order_type.DESC
    return ordering_from_sorted_activities(sorted(all_activities(log), reverse=reverse))


def ordering_from_sorted_activities(sorted_activities):
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
