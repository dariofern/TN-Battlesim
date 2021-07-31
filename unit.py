#!/usr/bin/env python3

from collections import namedtuple
import csv

Unit = namedtuple("Unit", ("unit_class", "name", "defense", "attack"))

def load_unit_data(unit_data_file):
    """
    Loads data from CSV into a list of unit types.

    The CSV is expected to have a header with the fields,
    Unit Class, Unit Name, Defense, and Attack (order does not matter).
    """
    units = []
    with open(unit_data_file) as f:
        for row in csv.DictReader(f):
            unit_class = row["Unit Class"]
            units.append(Unit(row["Unit Class"], row["Unit Name"],
                         float(row["Defense"]), float(row["Attack"])))

    return units

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: ./unit.py <path_to_unit_data>")
    else:
        print(load_unit_data(sys.argv[1]))