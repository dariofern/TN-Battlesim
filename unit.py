#!/usr/bin/env python3

import csv

class Unit:
    _type = "unassigned"

    def __init__(self, name, def_power, atck_power):
        self.name = name
        self.defense = def_power
        self.attack = atck_power

    def __str__(self):
        return f"<{self.name}, {self.defense}, {self.attack}>"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.name + self._type)

class LandUnit(Unit):
    _type = "land"

class NavalUnit(Unit):
    _type = "naval"

class AirUnit(Unit):
    _type = "air"

unit_classes = {
    "land" : LandUnit,
    "naval" : NavalUnit,
    "air" : AirUnit,
}

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
            units.append(unit_classes[unit_class](
                row["Unit Name"], float(row["Defense"]), float(row["Attack"])))

    return units

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: ./unit.py <path_to_unit_data>")
    else:
        print(load_unit_data(sys.argv[1]))