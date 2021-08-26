# TN-Battlesim

## Test Cases
The test cases are designed for use with the nose test framework.

To install nose on Windows:
 - `py -m pip install nose`

After installing nose, to run the tests:
 - `py -m nose -v`

If any of the test cases do not pass, it indicates that the behavior of the
script has changed. If the behavior was supposed to change, the test can be
updated by running:
 - `./generate_expected_output.py <input_file>`
