#!/usr/bin/env python3

from collections import namedtuple
import csv

Unit = namedtuple("Unit", (
    "unit_class",
    "name",
    "defense",
    "attack",
    "crew",
    "causualty_factor",
    "conscript_casualty_factor"))

def load_unit_data(handle):
    """
    Loads data from CSV into a list of unit types.

    The CSV is expected to have a header with the fields,
    Unit Class, Unit Name, Defense, and Attack (order does not matter).
    """
    units = []
    for row in csv.DictReader(handle):
        unit_class = row["Unit Class"]
        units.append(Unit(
            row["Unit Class"],
            row["Unit Name"],
            float(row["Defense"]),
            float(row["Attack"]),
            float(row["Personnel"]),
            float(row["Casualty Factor"]),
            float(row["Conscript Casualty Factor"])))

    return units

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: ./unit.py <path_to_unit_data>")
    else:
        with open(sys.argv[1]) as f:
            print(load_unit_data(f))