#!/usr/bin/env python3

# Script to log user interaction with the battlesim and generate a log
# of the input and expected output.

from generate_expected_output import generate_expected_output

import pexpect

import pathlib
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        test_name = input("Name of the test: ")
    else:
        test_name = sys.argv[1]
    # In case user entered spaces in the name, replace with underscores.
    test_name.replace(" ", "_")

    base_path = f"{pathlib.Path(__file__).parent}/sample_inputs"
    battlesim_path = f"{pathlib.Path(__file__).parent}/battlesim1.py"
    input_file = f"{base_path}/{test_name}.txt"
    expected_output_file = f"{base_path}/expected_{test_name}.txt"

    child = pexpect.spawn(f"{battlesim_path}", encoding="utf-8")
    with open(input_file, "w") as f:
        child.logfile_send = f.buffer
        child.interact()

    generate_expected_output(input_file, expected_output_file)
    