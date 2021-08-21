#!/usr/bin/env python3

import contextlib
import io
import pathlib
import random
import sys

SAMPLES_PATH = f"{pathlib.Path(__file__).parent}/sample_inputs"
SEED = 7192875936957918

def matches_expected(input_file):
    """
    Test whether an input file produces the expected output.

    The test will be looked for in the sample_inputs/ directory in
    the project workspace. If the input file is named test.txt, the file with
    expected values must be named expected_test.txt

    :param input_file: Name of the input file.
    :return: Whether the files match (True or False)
    """

    with open(f"{SAMPLES_PATH}/{input_file}", "r") as f:
        sys.stdin = f
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            import battlesim1
    sys.stdin = sys.__stdin__

    # Output was just written, so we need to seek back to the beginning.
    output.seek(0)
    with open(f"{SAMPLES_PATH}/expected_{input_file}", "r") as f:
        expected = f.read()
    return output.read() == expected

class TestRegressions:
    """
    Regression tests to ensure that certain inputs match the previously
    computed outputs.
    """

    def setup(self):
        """
        Seeds the random number generator so results are always consistent.
        """
        random.seed(SEED)

    def test_seed(self):
        """
        Make sure that the random seed is correct and working as expected.
        """
        assert random.random() == 0.38180022096866606

    def test_land_battle(self):
        assert matches_expected("one_v_one_land_conscripts.txt")