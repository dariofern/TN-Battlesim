#!/usr/bin/env python3

# Generate the expected output for a given input file; useful for making
# test cases.

import tests

import contextlib
import pathlib
import random
import sys

def generate_expected_output(input_file, expected_output_file):
    random.seed(tests.SEED)
    with open(input_file, "r") as f:
        sys.stdin = f
        with open(expected_output_file, "w") as out:
            with contextlib.redirect_stdout(out):
                import battlesim1
    sys.stdin = sys.__stdin__

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Correct usage is './generate_expected_output.py <input_file>'")
        sys.exit()

    input_file = pathlib.Path(sys.argv[1])
    expected_output_file = pathlib.Path(
        f"{input_file.parent}/expected_{input_file.name}")

    print(f"Generating expected output for {input_file}")
    print("-" * 40)

    if expected_output_file.exists():
        overwrite = input(
            f"Expected output for {input_file.name} already exists, " \
            "are you sure you want to overwrite it? (Y\\N) ")
        if not overwrite.lower().startswith("y"):
            print("Cancelled.")
            sys.exit()
        print("-" * 40)

    generate_expected_output(input_file, expected_output_file)

    print(f"Wrote expected output to {expected_output_file}")