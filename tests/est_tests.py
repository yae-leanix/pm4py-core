import os
import unittest

import pandas as pd

from pm4py.algo.discovery.est import algorithm as est_miner
from pm4py.algo.discovery.est.util import log_transformation as log_transformer
from pm4py.algo.discovery.est.util import order_calculation as order_calculator
from pm4py.algo.discovery.est.util import place_fitness as place_fitness_calculator
from pm4py.algo.discovery.est.util.place_fitness import Place, Fitness
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


class EstMinerOrderingTest(unittest.TestCase):
    def test_returnsSameInputAndOutputOrderingForAbsoluteActivityFrequencyMetric(self):
        log = xes_importer.apply(os.path.join(
            INPUT_DATA_DIR, "running-example.xes"))

        result = order_calculator.search_space_ordering_based_on_absolute_activity_frequency(
            log)

        self.assertEqual(result.input_ordering._smaller_than,
                         result.output_ordering._smaller_than)

    def test_returnsSameInputAndOutputOrderingForAbsoluteTraceFrequencyMetric(self):
        log = xes_importer.apply(os.path.join(
            INPUT_DATA_DIR, "running-example.xes"))

        result = order_calculator.search_space_ordering_based_on_absolute_trace_frequency(
            log)

        self.assertEqual(result.input_ordering._smaller_than,
                         result.output_ordering._smaller_than)

    def test_returnsDifferentInputAndOutputOrderingForAverageFirstOccurrenceIndexMetric(self):
        log = xes_importer.apply(os.path.join(
            INPUT_DATA_DIR, "running-example.xes"))

        result = order_calculator.search_space_ordering_based_on_average_first_occurrence_index(
            log)

        self.assertNotEqual(result.input_ordering._smaller_than,
                            result.output_ordering._smaller_than)

    def test_returnsAscendingAbsoluteActivityFrequencyOrdering(self):
        log = xes_importer.apply(os.path.join(
            INPUT_DATA_DIR, "running-example.xes"))
        # absAF(register request) = 6
        # absAF(examine casually) = 6
        # absAF(check ticket) = 9
        # absAF(decide) = 9
        # absAF(reinitiate request) = 3
        # absAF(examine thoroughly) = 3
        # absAF(pay compensation) = 3
        # absAF(reject request) = 3

        result = order_calculator.absolute_activity_frequency_ordering(
            log, order_type=order_calculator.OrderType.ASC)

        self.assertSmallerAndLarger(result, smallerActivities=['reinitiate request', 'examine thoroughly', 'pay compensation', 'reject request'], largerActivities=[
                                    'register request', 'examine casually', 'check ticket', 'decide'])
        self.assertSmallerAndLarger(result,
                                    smallerActivities=['register request', 'examine casually'], largerActivities=['check ticket', 'decide'])
        for equallyRated in [['register request', 'examine casually'], ['check ticket', 'decide'], ['reinitiate request', 'examine thoroughly', 'pay compensation', 'reject request']]:
            self.assertEquallyRated(result, equallyRated)

    def test_returnsDescendingAbsoluteActivityFrequencyOrdering(self):
        log = xes_importer.apply(os.path.join(
            INPUT_DATA_DIR, "running-example.xes"))

        result = order_calculator.absolute_activity_frequency_ordering(
            log, order_type=order_calculator.OrderType.DESC)

        self.assertSmallerAndLarger(result, smallerActivities=[
                                    'register request', 'examine casually', 'check ticket', 'decide'], largerActivities=['reinitiate request', 'examine thoroughly', 'pay compensation', 'reject request'])
        self.assertSmallerAndLarger(result, smallerActivities=[
                                    'check ticket', 'decide'], largerActivities=['register request', 'examine casually'])
        for equallyRated in [['register request', 'examine casually'], ['check ticket', 'decide'], ['reinitiate request', 'examine thoroughly', 'pay compensation', 'reject request']]:
            self.assertEquallyRated(result, equallyRated)

    def test_returnsAscendingAbsoluteTraceFrequencyOrdering(self):
        log = xes_importer.apply(os.path.join(
            INPUT_DATA_DIR, "running-example.xes"))
        # absTF(register request) = 6
        # absTF(examine casually) = 4
        # absTF(check ticket) = 6
        # absTF(decide) = 6
        # absTF(reinitiate request) = 2
        # absTF(examine thoroughly) = 3
        # absTF(pay compensation) = 3
        # absTF(reject request) = 3

        result = order_calculator.absolute_trace_frequency_ordering(
            log, order_type=order_calculator.OrderType.ASC)

        self.assertSmallerAndLarger(result, smallerActivities=['reinitiate request'], largerActivities=[
                                    'register request', 'examine casually', 'check ticket', 'decide', 'examine thoroughly', 'pay compensation', 'reject request'])
        self.assertSmallerAndLarger(result, smallerActivities=['examine thoroughly', 'pay compensation', 'reject request'], largerActivities=[
                                    'register request', 'check ticket', 'decide', 'examine casually'])
        self.assertSmallerAndLarger(result, smallerActivities=['examine casually'], largerActivities=[
                                    'register request', 'check ticket', 'decide'])
        for equallyRated in [['register request', 'check ticket', 'decide'], ['examine casually'], ['examine thoroughly', 'pay compensation', 'reject request'], ['reinitiate request']]:
            self.assertEquallyRated(result, equallyRated)

    def test_returnsDescendingAbsoluteTraceFrequencyOrdering(self):
        log = xes_importer.apply(os.path.join(
            INPUT_DATA_DIR, "running-example.xes"))

        result = order_calculator.absolute_trace_frequency_ordering(
            log, order_type=order_calculator.OrderType.DESC)

        self.assertSmallerAndLarger(result, smallerActivities=[
                                    'register request', 'examine casually', 'check ticket', 'decide', 'examine thoroughly', 'pay compensation', 'reject request'], largerActivities=['reinitiate request'])
        self.assertSmallerAndLarger(result, smallerActivities=[
                                    'register request', 'check ticket', 'decide', 'examine casually'], largerActivities=['examine thoroughly', 'pay compensation', 'reject request'])
        self.assertSmallerAndLarger(result, smallerActivities=[
                                    'register request', 'check ticket', 'decide'], largerActivities=['examine casually'])
        for equallyRated in [['register request', 'check ticket', 'decide'], ['examine casually'], ['examine thoroughly', 'pay compensation', 'reject request'], ['reinitiate request']]:
            self.assertEquallyRated(result, equallyRated)

    def test_returnsAscendingAverageFirstOccurrenceIndexOrdering(self):
        log = xes_importer.apply(os.path.join(
            INPUT_DATA_DIR, "running-example.xes"))
        # avgFOI(register request) = 1
        # avgFOI(examine casually) = 2.25
        # absFOI(check ticket) = 2.67
        # absFOI(decide) = 4
        # absFOI(reinitiate request) = 5
        # absFOI(examine thoroughly) = 3.67
        # absFOI(pay compensation) = 6.33
        # absFOI(reject request) = 7.67

        result = order_calculator.average_first_occurrence_index_ordering(
            log, order_type=order_calculator.OrderType.ASC)

        self.assertSmallerAndLarger(result, smallerActivities=['register request'], largerActivities=[
                                    'examine casually', 'check ticket', 'decide', 'reinitiate request', 'examine thoroughly', 'pay compensation', 'reject request'])
        self.assertSmallerAndLarger(result, smallerActivities=['examine casually'], largerActivities=[
                                    'check ticket', 'decide', 'reinitiate request', 'examine thoroughly', 'pay compensation', 'reject request'])
        self.assertSmallerAndLarger(result, smallerActivities=['check ticket'], largerActivities=[
                                    'decide', 'reinitiate request', 'examine thoroughly', 'pay compensation', 'reject request'])
        self.assertSmallerAndLarger(result, smallerActivities=['decide'], largerActivities=[
                                    'reinitiate request', 'pay compensation', 'reject request'])
        self.assertSmallerAndLarger(result, smallerActivities=['reinitiate request'], largerActivities=[
                                    'pay compensation', 'reject request'])
        self.assertSmallerAndLarger(result, smallerActivities=[
                                    'examine thoroughly'], largerActivities=['decide', 'reinitiate request', 'pay compensation', 'reject request'])
        self.assertSmallerAndLarger(
            result, smallerActivities=['pay compensation'], largerActivities=['reject request'])

    def test_returnsDescendingAverageFirstOccurrenceIndexOrdering(self):
        log = xes_importer.apply(os.path.join(
            INPUT_DATA_DIR, "running-example.xes"))

        result = order_calculator.average_first_occurrence_index_ordering(
            log, order_type=order_calculator.OrderType.DESC)

        self.assertSmallerAndLarger(result, smallerActivities=[
                                    'examine casually', 'check ticket', 'decide', 'reinitiate request', 'examine thoroughly', 'pay compensation', 'reject request'], largerActivities=['register request'])
        self.assertSmallerAndLarger(result, smallerActivities=[
                                    'check ticket', 'decide', 'reinitiate request', 'examine thoroughly', 'pay compensation', 'reject request'], largerActivities=['examine casually'])
        self.assertSmallerAndLarger(result, smallerActivities=[
                                    'decide', 'reinitiate request', 'examine thoroughly', 'pay compensation', 'reject request'], largerActivities=['check ticket'])
        self.assertSmallerAndLarger(result, smallerActivities=[
                                    'reinitiate request', 'pay compensation', 'reject request'], largerActivities=['decide'])
        self.assertSmallerAndLarger(result, smallerActivities=[
                                    'pay compensation', 'reject request'], largerActivities=['reinitiate request'])
        self.assertSmallerAndLarger(result, smallerActivities=['decide', 'reinitiate request', 'pay compensation', 'reject request'], largerActivities=[
                                    'examine thoroughly'])
        self.assertSmallerAndLarger(
            result, smallerActivities=['reject request'], largerActivities=['pay compensation'])

    def test_returnsAscendingLexicographicOrdering(self):
        log = xes_importer.apply(os.path.join(
            INPUT_DATA_DIR, "long_term_dependencies_xor.xes"))

        result = order_calculator.lexicographic_ordering(
            log, order_type=order_calculator.OrderType.ASC)

        self.assertSmallerAndLarger(result, smallerActivities=[
                                    'a'], largerActivities=['b', 'c', 'd', 'e', 'f'])
        self.assertSmallerAndLarger(result, smallerActivities=[
                                    'b'], largerActivities=['c', 'd', 'e', 'f'])
        self.assertSmallerAndLarger(result, smallerActivities=[
                                    'c'], largerActivities=['d', 'e', 'f'])
        self.assertSmallerAndLarger(result, smallerActivities=[
                                    'd'], largerActivities=['e', 'f'])
        self.assertSmallerAndLarger(result, smallerActivities=[
                                    'e'], largerActivities=['f'])
        for activity in ['a', 'b', 'c', 'd', 'e', 'f']:
            self.assertFalse(result.is_smaller_than(
                smaller=activity, larger=activity))

    def assertSmallerAndLarger(self, result, smallerActivities=[], largerActivities=[]):
        for larger in largerActivities:
            for smaller in smallerActivities:
                self.assertTrue(result.is_smaller_than(
                    smaller=smaller, larger=larger))
                self.assertFalse(result.is_smaller_than(
                    smaller=larger, larger=smaller))

    def assertEquallyRated(self, result, equallyRated):
        for a in equallyRated:
            for b in equallyRated:
                if (a != b):
                    self.assertTrue((result.is_smaller_than(
                        smaller=a, larger=b) or result.is_smaller_than(smaller=b, larger=a)))
                    self.assertFalse(result.is_smaller_than(
                        smaller=a, larger=b) and result.is_smaller_than(smaller=b, larger=a))
                else:
                    self.assertFalse(result.is_smaller_than(
                        smaller=a, larger=b) or result.is_smaller_than(smaller=b, larger=a))


class EstMinerPlaceFitnessTest(unittest.TestCase):
    def test_recognizesFittingPlace(self):
        log = xes_importer.apply(os.path.join(
            INPUT_DATA_DIR, "long_term_dependencies_xor.xes"))
        place = Place(input_activities=['a', 'b'], output_activities=['c'])
        tau = 1.0

        result = place_fitness_calculator.place_fitness_state(place, log, tau)

        self.assertTrue(Fitness.FITTING in result.fitness_properties)
        self.assertFalse(Fitness.UNDERFED in result.fitness_properties)
        self.assertFalse(Fitness.OVERFED in result.fitness_properties)

    def test_recognizesOverfedPlace(self):
        log = xes_importer.apply(os.path.join(
            INPUT_DATA_DIR, "long_term_dependencies_xor.xes"))
        place = Place(input_activities=['a', 'c'], output_activities=['d'])
        tau = 1.0

        result = place_fitness_calculator.place_fitness_state(place, log, tau)

        self.assertTrue(Fitness.OVERFED in result.fitness_properties)
        self.assertFalse(Fitness.UNDERFED in result.fitness_properties)
        self.assertFalse(Fitness.FITTING in result.fitness_properties)

    def test_recognizesUnderfedPlace(self):
        log = xes_importer.apply(os.path.join(
            INPUT_DATA_DIR, "long_term_dependencies_xor.xes"))
        place = Place(input_activities=['d'], output_activities=['c'])
        tau = 1.0

        result = place_fitness_calculator.place_fitness_state(place, log, tau)

        self.assertTrue(Fitness.UNDERFED in result.fitness_properties)
        self.assertFalse(Fitness.OVERFED in result.fitness_properties)
        self.assertFalse(Fitness.FITTING in result.fitness_properties)

    def test_recognizesOverfedAndUnderfedPlace(self):
        log = xes_importer.apply(os.path.join(
            INPUT_DATA_DIR, "long_term_dependencies_xor.xes"))
        place = Place(input_activities=[
                      'e', 'f', 'd'], output_activities=['a'])
        tau = 1.0

        result = place_fitness_calculator.place_fitness_state(place, log, tau)

        self.assertTrue(Fitness.OVERFED in result.fitness_properties)
        self.assertTrue(Fitness.UNDERFED in result.fitness_properties)
        self.assertFalse(Fitness.FITTING in result.fitness_properties)


if __name__ == "__main__":
    unittest.main()
