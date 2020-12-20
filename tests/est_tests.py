import os
import unittest

import pandas as pd

from pm4py.algo.discovery.est import algorithm as est_miner
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.log.importer.xes import importer as xes_importer
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


if __name__ == "__main__":
    unittest.main()
