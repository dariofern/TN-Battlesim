#!/usr/bin/env python3

#LAND BATTLE SIMULATOR

from unit import load_unit_data

from collections import defaultdict, namedtuple
import pathlib
import random

UNIT_DATA_FILE = f"{pathlib.Path(__file__).parent}/units.csv"

# Load at global scope to avoid loading more than once.
# Tuple ensures immutability.
with open(UNIT_DATA_FILE) as f:
    UNIT_TYPES = tuple(load_unit_data(f))

# Need to be able to map names of globals to names of units during refactoring.
global_names = {
    "infantry" : "Inf",
    "tank" : "Tanks",
    "AFV" : "AFV",
    "AAA" : "AAA",
    "FA" : "FA",
    "fighter" : "Fighter",
    "bomber" : "Bomber",
    "battleship" : "BattleS",
    "destroyer" : "Destroyer",
    "cruiser" : "Cruisers",
    "uboat" : "Uboat",
    "troopship" : "TroopS"
}

class Army:
    """ Represents a group of units and their corresponding numbers. """

    both_factors = frozenset([
        "budget_factor",
        "climate_factor",
        "conscript_factor",
        "luck_factor",
        "morale_factor",
        "supply_cut_factor",
        "tired_factor",
        "terrain_factor",
        "wage_factor"
    ])

    offense_factors = frozenset([
        "offense_tactic_factor"
    ])

    defense_factors = frozenset([
        "defense_tactic_factor",
        "entrenchment_factor"
    ])

    def __init__(self, units):
        self.units = units

    def base_strength(self):
        """
        Compute the base offensive and defensive score of an army.

        No factors besides the units are taken into account.
        """
        offense = 0
        defense = 0
        # Sum up base unit stats.
        for unit, qty in self.units.items():
            offense += unit.attack * qty
            defense += unit.defense * qty
        return offense, defense

    def strength(self, **kwargs):
        """
        Compute the offensive and defensive score of an army.

        Wage, terrain advantage, entrenchment, a luck factor and a
        conscription factor (default 1 ) are all taken into account.
        Factors may not be 0, but resulting army strength may be.
        """

        offense, defense = self.base_strength()

        # Apply modifiers.
        for factor, value in kwargs.items():
            if value <= 0:
                raise ValueError(f"{factor} has value {value}, but must be "
                                 "greater than 0.")

            if factor in self.both_factors:
                offense *= value
                defense *= value
            elif factor in self.offense_factors:
                offense *= value
            elif factor in self.defense_factors:
                defense *= value
            else:
                raise ValueError(f"{factor} is not a valid factor.")

        return offense, defense

    def casu(self, is_conscripts, s,tr,scatW,scatL,scdefW,scdefL,scatWair,scatLair,scdefWair,scdefLair,typ,pop):
        """
        Compute three new armies of alive, damaged, and dead units.
        """

        casualties1 = [0, 0]

        alive = {}
        wounded = {}
        dead = {}

        for unit, qty in self.units.items():

            if is_conscripts:
                casualty_factor = unit.conscript_casualty_factor
            else:
                casualty_factor = unit.casualty_factor

            # Troopship crew is the base number plus however many troops
            # it is carrying.
            if unit.name == "troopship" and tr != 0:
                #crew = unit.crew + globals()[tr]
                print("Troopship needs to be fixed still.")
            else:
                crew = unit.crew

            alive[unit], wounded[unit], dead[unit] = Army.casualties(qty,scatW,scatL,scdefW,scdefL,s,casualties1,casualty_factor,crew,typ,nearby_pop)

        print(casualties1)

        return alive, wounded, dead

    # Staticmethod until we can refactor this so it uses its own unit stats.
    @staticmethod
    def casualties(unit,scatW,scatL,scdefW,scdefL,status,casu,mult,cons,typ,air):
        typm=typ-(typ/2)+air/2
        if air==1:
            if ((-scatL)+scdefW)<((-scatW)+scdefL):
                if status=='loser':
                    status='winner'
                if status=='winner':
                    status='loser'
                scat=[scatL,scatW]
                scdef=[scdefL,scdefW]
                scatL=scat[1]
                scatW=scat[0]
                scdefL=scdef[1]
                scdefW=scdef[0]
        w=(((scatL+scdefL)/(scatW+scdefW))*(1+((scatL+scdefL)/(scatW+scdefW))))/4
        d=(((scatL+scdefL)/(scatW+scdefW))*(1+((scatL+scdefL)/(scatW+scdefW))))/10
        if status=='winner':
            deaths=round(unit*d*typm,0)
            wounded=round((unit-deaths)*w*typm,0)
            remaining=unit-wounded-deaths
        elif status=='loser':
            # Magic numbers, magic numbers everywhere.
            p=(((scatW+scdefW)/(scatL+scdefL))**2)/1.35
            ld=d*(1+(p/2))
            if ld>=0.95:
                ld=0.95
            lw=w*(1+(p/2))
            if lw>=1:
                lw=1
            deaths=round(unit*ld*typm,0)
            wounded=round((unit-deaths)*lw*typm,0)
            remaining=unit-wounded-deaths

        # Land battle
        if typ == 1:
            casu[0] = casu[0] + wounded * mult
            casu[1] = casu[1] + deaths * mult
        # Naval battle
        if typ == 2:
            woundedDeath = random.randint(0, 10)
            deathDeath = random.randint(50, 100)
            woundedWounded = woundedDeath+15
            woundedWounded = random.randint(0,woundedWounded)
            deathWounded = 100 - deathDeath
            deathWounded = random.randint(0,deathWounded)
            casu[0]=casu[0]+round(wounded*mult*woundedWounded/100+deaths*mult*deathWounded/100,0)
            casu[1]=casu[1]+round(deaths*mult*(deathDeath/100)+wounded*mult*(woundedDeath/100),0)

        return int(remaining), int(wounded), int(deaths)

class Nation():
    """ Represents a nation and their armies. """

    def __init__(self, name, prof_army, conscript_army,
                 prof_air_army, conscript_air_army):
        self.name = name
        self.prof_army = prof_army
        self.conscript_army = conscript_army
        self.prof_air_army = prof_air_army
        self.conscript_air_army = conscript_air_army

    def strength(self, wage_factor, conscript_wage_factor,
                 entrenchment_factor, terrain_factor, factors):
        """ Get the combined strength of all the nation's armies. """

        prof_off, prof_def = self.prof_army.strength(
            wage_factor=wage_factor,
            entrenchment_factor=entrenchment_factor,
            terrain_factor=terrain_factor,
            **factors)

        conscript_off, conscript_def = self.conscript_army.strength(
            wage_factor=conscript_wage_factor,
            entrenchment_factor=entrenchment_factor,
            terrain_factor=terrain_factor,
            conscript_factor=0.3,
            **factors)

        air_prof_off, air_prof_def = self.prof_air_army.strength(
            wage_factor=wage_factor,
            terrain_factor=1,
            entrenchment_factor=1,
            **factors)

        air_conscript_off, air_conscript_def = \
                self.conscript_air_army.strength(
            wage_factor=conscript_wage_factor,
            terrain_factor=1,
            entrenchment_factor=1,
            conscript_factor=0.3,
            **factors)

        return (prof_off + conscript_off + air_prof_off + air_conscript_off,
                prof_def + conscript_def + air_prof_def + air_conscript_def,
                air_prof_off + air_conscript_off,
                air_prof_def + air_conscript_def)

    # scatW,scatL,scdefW,scdefL,scatWair,scatLair,scdefWair,scdefLair
    def casu(self,
             status,
             tr,
             off_first_side,
             off_second_side,
             def_first_side,
             def_second_side,
             air_off_first_side,
             air_off_second_side,
             air_def_first_side,
             air_def_second_side,
             battle_type,
             nearby_pop):
        """ Get casualties of each army. """
        #casualties1 = [0,0]
        prof_casualties = self.prof_army.casu(
            False,
            status,
            tr,
            off_first_side,
            off_second_side,
            def_first_side,
            def_second_side,
            air_off_first_side,
            air_off_second_side,
            air_def_first_side,
            air_def_second_side,
            battle_type,
            nearby_pop)
        conscript_casualties = self.conscript_army.casu(
            True,
            status,
            tr,
            off_first_side,
            off_second_side,
            def_first_side,
            def_second_side,
            air_off_first_side,
            air_off_second_side,
            air_def_first_side,
            air_def_second_side,
            battle_type,
            nearby_pop)
        # Air troops get away free under these obscure, unreadable conditions.
        if (status == "winner" and air_off_first_side != 0 and 
                air_off_second_side == 0) or (status == "loser" and 
                air_def_second_side != 0 and air_off_first_side == 0):
            prof_air_casualties = (
                dict(self.prof_air_army.units),
                defaultdict(int),
                defaultdict(int))
            conscript_air_casualties = (
                dict(self.conscript_air_army.units),
                defaultdict(int),
                defaultdict(int))
        elif (status == "winner" and air_off_first_side !=0 and
                air_off_second_side != 0) or (status == "loser" and
                air_def_second_side != 0 and air_off_first_side != 0):
            prof_air_casualties = self.prof_air_army.casu(
                False,
                status,
                tr,
                off_first_side,
                off_second_side,
                def_first_side,
                def_second_side,
                air_off_first_side,
                air_off_second_side,
                1,
                1,
                1,
                nearby_pop)
            conscript_air_casualties = self.conscript_air_army.casu(
                True,
                status,
                tr,
                off_first_side,
                off_second_side,
                def_first_side,
                def_second_side,
                air_off_first_side,
                air_off_second_side,
                1,
                1,
                1,
                nearby_pop)

        return (prof_casualties, conscript_casualties,
                prof_air_casualties, conscript_air_casualties)

def filter_units(units, classes):
    """
    Filter units returning those in the specified classes.
    """
    filtered_units = {}
    for unit, qty in units.items():
        if unit.unit_class in classes:
            filtered_units[unit] = qty

    return filtered_units

#DATA INPUT

def input_positive_integer(prompt):
    """
    Get a positive integer from the input.
    
    Will retry until a valid input is entered.
    """
    while True:
        try:
            n = int(input(prompt))
            if n < 0:
                raise ValueError()
            return n
        except ValueError:
            print("Value must be a positive integer.")

def input_armies(typ):
    print()
    name = input("Name of the country : ")

    professionals = defaultdict(int)
    conscripts = defaultdict(int)
    allowed_classes = set()

    # Land battle
    if typ == 1:
        allowed_classes |= {"land", "air"}
    # Naval battle
    elif typ == 2:
        allowed_classes |= {"naval"}
        coas=int(input("Coastal battle ? [1]:yes [0]:no"))
        if coas == 1:
            allowed_classes |= {"air"}
    else:
        raise ValueError(f"Battle type must be 1 or 2, not {typ}.")

    have_conscripts = int(input("Conscripts ? [1]:yes [0]:no"))

    for unit in UNIT_TYPES:
        if unit.unit_class not in allowed_classes:
            continue
        professionals[unit] = input_positive_integer(f"{unit.name} : ")
        if have_conscripts == 1:
            conscripts[unit] = input_positive_integer(
                f"conscript {unit.name} : ")

    prof_army = Army(filter_units(professionals, {"land", "naval"}))
    conscript_army = Army(filter_units(conscripts, {"land", "naval"}))
    prof_army_air = Army(filter_units(professionals, {"air"}))
    conscript_army_air = Army(filter_units(conscripts, {"air"}))

    return name, prof_army, conscript_army, prof_army_air, conscript_army_air

def input_factors(typ, n):

    # If we're having a naval battle.
    tr='tr'+str(n)
    globals()[tr] = 0
    if typ == 2:
        if (globals()[f"TroopS{n}"]+globals()[f"CTroopS{n}"])!=0:
            globals()[tr]=round(int(input("Number of soldiers transported by troopships"))/(globals()[TroopS]+globals()[CTroopS]),0)

    print("Country stats :")

    military_budget = ((int(input("Military budget (without the $ and no commas) : ")))/100000000000)+1
    research_budget = ((int(input("Research budget (without the $ and no commas) : ")))/100000000000)+1
    wage_factor = (((int(input("Wage level (1-4) : ")))-1)/10)+1
    conscript_wage_factor = (((int(input("Conscript Wage level (1-4) : ")))-1)/4)+1
    tired_factor = (1-(int(input("Recent Battles (one year) : "))/20))
    morale = (10 - (int(input("Recent Battles lost (one year) : "))))+(int(input("Recent Battles won (one year) : ")))
    # Morale should be between 1 and 10, inclusive.
    morale = min(10, morale)
    morale = max(1, morale)
    morale_factor = 1 + (morale - 5) / 20
    
    if typ==1:
        terrain_knowledge = 1+((int(input("Terrain Knowledge (out of 5) : "))-3)/20)
        climate_factor = 0.25+(float(input("Climate malus : ")))
        trench = (int(input("Entrenchement? [0] : no [1]: yes : ")))
        if trench == 1:
            entrenchment_factor = 1+((int(input("Entrenchement level : ")))**2)/30
        elif trench == 0:
            entrenchment_factor = 1
        hill=int(input("Elevation advantage? [0] : no [1]: yes : "))
        river=int(input("Defending a river? [0] : no [1]: yes : "))
        city=int(input("Defending a city? [0] : no [1]: yes : "))
        landing=int(input("Disembarkment ? [0] : no [1]: yes : "))
        Tadv = 'Tadv'+str(n)
        terrain_advantage = 1 + (hill + river + city - landing) / 2
        terrain_factor = terrain_knowledge + terrain_advantage
        supply_cut_factor = 1 - (
            int(input("Supply line cut ? [0]:no [1]:yes")) / 3)

    else :
        terrain_factor = 1
        climate_factor = 1
        entrenchment_factor = 1
        supply_cut_factor = 1
                                   
    GenDef = 'GenDef'+str(n)
    globals()[GenDef] = int(input("General's defense skills : "))
    GenOff = 'GenOff'+str(n)
    globals()[GenOff] = int(input("General's attack skills : "))
    offense_tactic_factor = float(input("Offensive Tactic bonus : "))*(1+(globals()[GenOff])/20)
    defense_tactic_factor = float(input("Defensive Tactic bonus : "))*(1+(globals()[GenDef])/20)

    factors = {
        "budget_factor" : military_budget + research_budget,
        "climate_factor" : climate_factor,
        "defense_tactic_factor" : defense_tactic_factor,
        "luck_factor" : random.randint(85, 112) / 100,
        "morale_factor" : morale_factor,
        "offense_tactic_factor" : offense_tactic_factor,
        "supply_cut_factor" : supply_cut_factor,
        "tired_factor" : tired_factor,
    }

    return (wage_factor, conscript_wage_factor, entrenchment_factor,
            terrain_factor, factors)

def print_casualties(nation, description, units):
    print("------------------------------------------------------------------------")
    casualties1=[0,0]

    print(f"Casualties for {nation.name}")
    print(f"|Unit Type\t\t|Remaining\t|Wounded\t|Dead")

    alive, wounded, dead = units
    # Just to get the name of every unit to be considered.
    for unit in alive:
        print_name = f"{description} {unit.name}"
        # 20 was chosen arbitrarily.
        padding = ' ' * (20 - len(print_name))
        print(f" {print_name + padding}\t {alive[unit]}"
              f"\t\t {wounded[unit]}\t\t {dead[unit]}")

    print("Casualties (wounded/dead):",casualties1)

first_side_nations = []
second_side_nations = []
typ=int(input("Type of battle : [1]:land, [2]:sea"))

# Input nations for the first side.
first_side_name = input('Name of the first side :')
n = int(input('Nations fighting for this side :'))
off_first_side = 0
def_first_side = 0
air_off_first_side = 0
air_def_first_side = 0
for i in range(n):
    nation = Nation(*input_armies(typ))
    first_side_nations.append(nation)
    factors = input_factors(typ, i)
    (off_strength, def_strength,
     air_off_strength, air_def_strength) = nation.strength(*factors)
    off_first_side += off_strength
    def_first_side += def_strength
    air_off_first_side += air_off_strength
    air_def_first_side += air_def_strength

# Input nations for the second side.
print()
second_side_name = input('Name of the second side :')
n = int(input('Nations fighting for this side :'))
off_second_side = 0
def_second_side = 0
air_off_second_side = 0
air_def_second_side = 0
for i in range(n):
    nation = Nation(*input_armies(typ))
    second_side_nations.append(nation)
    factors = input_factors(typ, i)
    (off_strength, def_strength,
     air_off_strength, air_def_strength) = nation.strength(*factors)
    off_second_side += off_strength
    def_second_side += def_strength
    air_off_second_side += air_off_strength
    air_def_second_side += air_def_strength

nearby_pop = int(input('nearby population')) / 6000
first_side_score = def_second_side - off_first_side
second_side_score = def_first_side - off_second_side

print("\n")
if first_side_score > second_side_score:
    print(f"{first_side_name} won the battle!")
    winning_nations, losing_nations = first_side_nations, second_side_nations
elif second_side_score > first_side_score:
    print(f"{second_side_name} won the battle!")
    winning_nations, losing_nations = second_side_nations, first_side_nations
else:
    raise RuntimeError("Unhandled draw!")

tr = 0

for nation in winning_nations:
    (prof_casualties, conscript_casualties,
                     prof_air_casualties, conscript_air_casualties) = nation.casu("winner",tr,off_first_side,off_second_side,def_first_side,def_second_side,air_off_first_side,air_off_second_side,air_def_first_side,air_def_second_side,typ,nearby_pop)
    print_casualties(nation, "", prof_casualties)
    print_casualties(nation, "conscript", conscript_casualties)
    print_casualties(nation, "", prof_air_casualties)
    print_casualties(nation, "conscript", conscript_air_casualties)

for nation in losing_nations:
    (prof_casualties, conscript_casualties,
                     prof_air_casualties, conscript_air_casualties) = nation.casu("winner",tr,off_first_side,off_second_side,def_first_side,def_second_side,air_off_first_side,air_off_second_side,air_def_first_side,air_def_second_side,typ,nearby_pop)
    print_casualties(nation, "", prof_casualties)
    print_casualties(nation, "conscript", conscript_casualties)
    print_casualties(nation, "", prof_air_casualties)
    print_casualties(nation, "conscript", conscript_air_casualties)

# Population has been broken.
nearby_pop = round(nearby_pop / 6000, 0)
print('Civil casualties:', nearby_pop)