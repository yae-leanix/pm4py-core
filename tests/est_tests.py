import os
import unittest

import pandas as pd

from pm4py.algo.discovery.est import algorithm as est_miner
from pm4py.algo.discovery.est.util import log_transformation as log_transformer
from pm4py.algo.discovery.est.util import order_calculation as order_calculator
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.util import xes_constants as xes_util
from tests.constants import INPUT_DATA_DIR


class EstMinerTest(unittest.TestCase):
    def obtain_petri_net_through_est(self, log_name, variant):
        if ".xes" in log_name:
            log = xes_importer.apply(log_name)
        else:
            df = pd.read_csv(log_name)
            df = dataframe_utils.convert_timestamp_columns_in_df(df)
            log = log_conversion.apply(df)
        net, marking, fmarking = est_miner.apply(
            log, parameters=None, variant=variant)

        return log, net, marking, fmarking

    def test_applyClassicEstMinerToXES(self):
        log, net, marking, fmarking = self.obtain_petri_net_through_est(
            os.path.join(INPUT_DATA_DIR, "running-example.xes"), est_miner.EST_VERSION_CLASSIC)

        self.assertIsNotNone(net)
        self.assertIsNotNone(marking)
        self.assertIsNotNone(fmarking)

    def test_applyInterestingPlacesEstMinerToXES(self):
        log, net, marking, fmarking = self.obtain_petri_net_through_est(
            os.path.join(INPUT_DATA_DIR, "running-example.xes"),
            est_miner.EST_VERSION_INTERESTING_PLACES)

        self.assertIsNotNone(net)
        self.assertIsNotNone(marking)
        self.assertIsNotNone(fmarking)


class EstMinerUtilTest(unittest.TestCase):
    def test_addsUniqueStartAndEndActivityToLog(self):
        log = xes_importer.apply(os.path.join(
            INPUT_DATA_DIR, "running-example.xes"))
        start_activity = "[start>"
        end_activity = "[end]"
        activity_key = xes_util.DEFAULT_NAME_KEY

        result = log_transformer.add_unique_start_and_end_activity(
            log, start_activity=start_activity, end_activity=end_activity, activity_key=activity_key)

        for trace in result:
            self.assertEqual(trace[0], {activity_key: start_activity})
            self.assertEqual(trace[len(trace) - 1],
                             {activity_key: end_activity})

    def test_returnsAbsoluteActivityFrequencyOrdering(self):
        pass

    def test_returnsAbsoluteTraceFrequencyOrdering(self):
        pass

    def test_returnsAbsoluteTraceOccurrenceOrdering(self):
        pass

    def test_returnsAverageFirstOccurrenceIndexOrdering(self):
        pass

    def test_returnsLexicographicOrdering(self):
        log = xes_importer.apply(os.path.join(
            INPUT_DATA_DIR, "long_term_dependencies_xor.xes"))

        result = order_calculator.lexicographic_ordering(log)

        for larger in ['b', 'c', 'd', 'e', 'f']:
            self.assertTrue(result.is_smaller_than(
                smaller='a', larger=larger))
            self.assertFalse(result.is_smaller_than(
                smaller=larger, larger='a'))
        for larger in ['c', 'd', 'e', 'f']:
            self.assertTrue(result.is_smaller_than(smaller='b', larger=larger))
            self.assertFalse(result.is_smaller_than(
                smaller=larger, larger='b'))
        for larger in ['d', 'e', 'f']:
            self.assertTrue(result.is_smaller_than(smaller='c', larger=larger))
            self.assertFalse(result.is_smaller_than(
                smaller=larger, larger='c'))
        for larger in ['e', 'f']:
            self.assertTrue(result.is_smaller_than(smaller='d', larger=larger))
            self.assertFalse(result.is_smaller_than(
                smaller=larger, larger='d'))
        for larger in ['f']:
            self.assertTrue(result.is_smaller_than(smaller='e', larger=larger))
            self.assertFalse(result.is_smaller_than(
                smaller=larger, larger='e'))
        for activity in ['a', 'b', 'c', 'd', 'e', 'f']:
            self.assertFalse(result.is_smaller_than(
                smaller=activity, larger=activity))


if __name__ == "__main__":
    unittest.main()
