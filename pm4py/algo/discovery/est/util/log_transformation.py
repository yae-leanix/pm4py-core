from pm4py.util import xes_constants as xes_util
from pm4py.objects.log.log import Event


def add_unique_start_and_end_activity(log, start_activity='[start>', end_activity='[end]', activity_key=xes_util.DEFAULT_NAME_KEY):
    for trace in log:
        trace.insert(0, Event({activity_key: start_activity}))
        trace.append(Event({activity_key: end_activity}))
    return log
