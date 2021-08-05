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

    def casu(self, is_conscripts, i,s,tr,scatW,scatL,scdefW,scdefL,scatWair,scatLair,scdefWair,scdefLair,typ,pop):
        """
        Compute three new armies of alive, damaged, and dead units.
        """

        alive = {}
        wounded = {}
        dead = {}

        for unit in self.units:
            # Name of global containing name of global.
            g_name_name = globals()[global_names[f"{unit.name}"]]

            if is_conscripts:
                g_name = globals()[f"C{g_name_name}"]
                casualty_factor = unit.conscript_casualty_factor
            else:
                g_name = globals()[g_name_name]
                casualty_factor = unit.casualty_factor

            # Troopship crew is the base number plus however many troops
            # it is carrying.
            if unit.name == "troopship" and tr != 0:
                crew = unit.crew + globals()[tr]
            else:
                crew = unit.crew

            if unit.unit_class != "air":
                alive, wounded, dead = Army.casualties(g_name,scatW,scatL,scdefW,scdefL,s,casualties1,sidenat1,casualty_factor,crew,typ,0)
            # Air troops get away free under these obscure, unreadable conditions.
            elif unit.unit_class == "air" and (s=='winner' and scdefWair!=0 and scatLair==0) or (s=='loser' and scdefLair!=0 and scatWair==0):
                alive, wounded, dead = globals()[g_name], 0, 0
            elif unit.unit_class == "air" and (s=='winner' and scdefWair!=0 and scatLair!=0) or (s=='loser' and scdefLair!=0 and scatWair!=0) :
                alive, wounded, dead = Army.casualties(g_name,scatWair,scatLair,scdefWair,scdefLair,s,casualties1,sidenat1,1,crew,1,1)
            else:
                # Unit type not handled?
                continue

            alive[unit] = alive
            wounded[unit] = wounded
            dead[unit] = dead

        return alive, wounded, dead

    # Staticmethod until we can refactor this so it uses its own unit stats.
    @staticmethod
    def casualties(unit,scatW,scatL,scdefW,scdefL,status,casu,sn,mult,cons,typ,air):
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

def TEAM(n,sidesat,sidesdef,nsid,li,typ):
    teamname='Team'+str(n)
    print()
    globals()[teamname]= input("Name of the country : ")

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

    cons='cons'+str(n)
    globals()[cons]=int(input("Conscripts ? [1]:yes [0]:no"))

    for unit in UNIT_TYPES:
        if unit.unit_class not in allowed_classes:
            continue
        professionals[unit] = input_positive_integer(f"{unit.name} : ")
        if globals()[cons] == 1:
            conscripts[unit] = input_positive_integer(
                f"conscript {unit.name} : ")

    prof_army = Army(filter_units(professionals, {"land", "naval"}))
    conscript_army = Army(filter_units(conscripts, {"land", "naval"}))
    prof_army_air = Army(filter_units(professionals, {"air"}))
    conscript_army_air = Army(filter_units(conscripts, {"air"}))

    for unit, qty in professionals.items():
        globals()[f"{global_names[unit.name]}{n}"] = qty
    for unit, qty in conscripts.items():
        globals()[f"C{global_names[unit.name]}{n}"] = qty

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
        trench = 'trench'+str(n)
        globals()[trench] = (int(input("Entrenchement? [0] : no [1]: yes : ")))
        if globals()[trench]==1:
            Entrench='Entrench'+str(n)
            globals()[Entrench] = 1+((int(input("Entrenchement level : ")))**2)/30
        if globals()[trench]==0:
            Entrench='Entrench'+str(n)
            globals()[Entrench] = 1
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
        Terrain='Terrain'+str(n)
        globals()[Terrain] = 1
        Climate='Climate'+str(n)
        globals()[Climate] = 1
        Entrench = 'Entrench'+str(n)
        globals()[Entrench] = 1
        Tadv = 'Tadv'+str(n)
        globals()[Tadv] = 1
        Supply='Supply'+str(n)
        globals()[Supply] = 1
                                   
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

    prof_off, prof_def = prof_army.strength(
        wage_factor=wage_factor,
        entrenchment_factor=globals()[Entrench],
        terrain_factor=terrain_factor,
        **factors)

    conscript_off, conscript_def = conscript_army.strength(
        wage_factor=conscript_wage_factor,
        entrenchment_factor=globals()[Entrench],
        terrain_factor=terrain_factor,
        conscript_factor=0.3,
        **factors)

    air_prof_off, air_prof_def = prof_army_air.strength(
        wage_factor=wage_factor,
        terrain_factor=1,
        entrenchment_factor=1,
        **factors)

    air_conscript_off, air_conscript_def = conscript_army_air.strength(
        wage_factor=conscript_wage_factor,
        terrain_factor=1,
        entrenchment_factor=1,
        conscript_factor=0.3,
        **factors)

    li.append([nsid,n])
    return (prof_off + conscript_off + air_prof_off + air_conscript_off,
            prof_def + conscript_def, + air_prof_def, + air_conscript_def,
            air_prof_off + air_conscript_off,
            air_prof_def + air_conscript_def)

def casucount(is_conscripts, i,s,tr,scatW,scatL,scdefW,scdefL,scatWair,scatLair,scdefWair,scdefLair,typ,pop):
    print("------------------------------------------------------------------------")
    casualties1=[0,0]
    teamname='Team'+str(Listside[i][1])

    print(f"Casualties for {globals()[teamname]}")
    print(f"|Unit Type\t\t|Remaining\t|Wounded\t|Dead")

    for unit in UNIT_TYPES:
        # Name of global containing name of global.
        g_name_name = globals()[global_names[f"{unit.name}"]]

        try:
            if is_conscripts:
                g_name = globals()[f"C{g_name_name}"]
                casualty_factor = unit.conscript_casualty_factor
            else:
                g_name = globals()[g_name_name]
                casualty_factor = unit.casualty_factor
        except KeyError:
            # Unit is not in use in this battle.
            continue

        # Troopship crew is the base number plus however many troops
        # it is carrying.
        if unit.name == "troopship" and tr != 0:
            crew = unit.crew + globals()[tr]
        else:
            crew = unit.crew

        try:
            if unit.unit_class != "air":
                alive, wounded, dead = Army.casualties(g_name,scatW,scatL,scdefW,scdefL,s,casualties1,sidenat1,casualty_factor,crew,typ,0)
            # Air troops get away free under these obscure, unreadable conditions.
            elif unit.unit_class == "air" and (s=='winner' and scdefWair!=0 and scatLair==0) or (s=='loser' and scdefLair!=0 and scatWair==0):
                alive, wounded, dead = globals()[g_name], 0, 0
            elif unit.unit_class == "air" and (s=='winner' and scdefWair!=0 and scatLair!=0) or (s=='loser' and scdefLair!=0 and scatWair!=0) :
                alive, wounded, dead = Army.casualties(g_name,scatWair,scatLair,scdefWair,scdefLair,s,casualties1,sidenat1,1,crew,1,1)
            else:
                # Unit type not handled?
                continue
        except KeyError:
            # Hopefully unit not handled.
            continue
        # 20 was chosen arbitrarily.
        conscript_str = ""
        if is_conscripts:
            conscript_str = "conscript "
        print_name = conscript_str + unit.name
        padding = ' ' * (20 - len(print_name))
        print(f" {print_name + padding}\t {alive}\t\t {wounded}\t\t {dead}")

    print("Casualties (wounded/dead):",casualties1)
    pop=round(pop*(((casualties1[0]+casualties1[1])/(pop+1))/10),0)
    print("------------------------------------------------------------------------")
    return (pop)
    
Listside=[]
typ=int(input("Type of battle : [1]:land, [2]:sea"))
Side1=input('Name of the first side :')
sidenat1=int(input('Nations fighting for this side :'))
number=1
Siden=1
sidescoreat1=0
sidescoreairat1=0
sidescoreDef1=0
sidescoreairDef1=0
for loop in range(sidenat1):
    teamfi=TEAM(number,sidescoreat1,sidescoreDef1,Siden,Listside,typ)
    number=number+1
    sidescoreat1=sidescoreat1+teamfi[0]
    sidescoreairat1=sidescoreairat1+teamfi[2]
    sidescoreDef1=sidescoreDef1+teamfi[1]
    sidescoreairDef1=sidescoreairDef1+teamfi[3]
print()
Side2=input('Name of the second side :')
sidenat2=int(input('Nations fighting for this side :'))
sidescoreat2=0
sidescoreairat2=0
sidescoreDef2=0
sidescoreairDef2=0
Siden=2
for loop in range(sidenat2):
    teamse=TEAM(number,sidescoreat2,sidescoreDef2,Siden,Listside,typ)
    number=number+1
    sidescoreat2=sidescoreat2+teamse[0]
    sidescoreairat2=sidescoreairat2+teamse[2]
    sidescoreDef2=sidescoreDef2+teamse[1]
    sidescoreairDef2=sidescoreairDef2+teamse[3]
populationcity=int(input('nearby population'))/6000
Scoreside1 = sidescoreDef2-sidescoreat1
Scoreside2 = sidescoreDef1-sidescoreat2

def who_knows_what_this_even_does(side, win, loss):
    global populationcity
    global Inf
    global CInf
    global Tanks
    global CTanks
    global AFV
    global CAFV
    global AAA
    global CAAA
    global FA
    global CFA
    global Fighter
    global CFighter
    global Bomber
    global CBomber
    global BattleS
    global CBattleS
    global Destroyer
    global CDestroyer
    global Cruisers
    global CCruisers
    global Uboat
    global CUboat
    global TroopS
    global CTroopS
    global tr
    print()
    print(str(side)," won the battle!")
    Listside.sort()
    for i in range (0,number-1):
        Inf='Inf'+str(Listside[i][1])
        Tanks='Tanks'+str(Listside[i][1])
        AFV='AFV'+str(Listside[i][1])
        AAA='AAA'+str(Listside[i][1])
        FA='FA'+str(Listside[i][1])
        Fighter='Fighter'+str(Listside[i][1])
        Bomber='Bomber'+str(Listside[i][1])
        CInf='CInf'+str(Listside[i][1])
        CTanks='CTanks'+str(Listside[i][1])
        CAFV='CAFV'+str(Listside[i][1])
        CAAA='CAAA'+str(Listside[i][1])
        CFA='CFA'+str(Listside[i][1])
        CFighter='CFighter'+str(Listside[i][1])
        CBomber='CBomber'+str(Listside[i][1])
        tr='tr'+str(Listside[i][1])
        BattleS='BattleS'+str(Listside[i][1])
        Destroyer='Destroyers'+str(Listside[i][1])
        Cruisers='Cruisers'+str(Listside[i][1])
        Uboat='Uboat'+str(Listside[i][1])
        TroopS='TroopS'+str(Listside[i][1])
        CBattleS='BattleS'+str(Listside[i][1])
        CDestroyer='Destroyers'+str(Listside[i][1])
        CCruisers='Cruisers'+str(Listside[i][1])
        CUboat='Uboat'+str(Listside[i][1])
        CTroopS='TroopS'+str(Listside[i][1])
        if Listside[i][0] == win:
            if typ==1:
                populationcity=populationcity+casucount(False, i,"winner",0,sidescoreat1,sidescoreat2,sidescoreDef1,sidescoreDef2,sidescoreairat1,sidescoreairat2,sidescoreairDef1,sidescoreairDef2,1,populationcity)
                cons='cons'+str(Listside[i][1])
                if globals()[cons]==1:
                    populationcity=populationcity+casucount(True, i,"winner",0,sidescoreat1,sidescoreat2,sidescoreDef1,sidescoreDef2,sidescoreairat1,sidescoreairat2,sidescoreairDef1,sidescoreairDef2,1,populationcity)
            if typ==2:
                populationcity=populationcity+casucount(False, i, "winner",tr,sidescoreat1,sidescoreat2,sidescoreDef1,sidescoreDef2,sidescoreairat1,sidescoreairat2,sidescoreairDef1,sidescoreairDef2,2,populationcity)
                cons='cons'+str(Listside[i][1])
                if globals()[cons]==1:
                    populationcity=populationcity+casucount(True, i,"winner",tr,sidescoreat1,sidescoreat2,sidescoreDef1,sidescoreDef2,sidescoreairat1,sidescoreairat2,sidescoreairDef1,sidescoreairDef2,2,populationcity)
        if Listside[i][0] == loss:
            if typ==1:
                populationcity=populationcity+casucount(False, i,"loser",0,sidescoreat1,sidescoreat2,sidescoreDef1,sidescoreDef2,sidescoreairat1,sidescoreairat2,sidescoreairDef1,sidescoreairDef2,1,populationcity)
                cons='cons'+str(Listside[i][1])
                if globals()[cons]==1:
                    populationcity=populationcity+casucount(True, i,"loser",0,sidescoreat1,sidescoreat2,sidescoreDef1,sidescoreDef2,sidescoreairat1,sidescoreairat2,sidescoreairDef1,sidescoreairDef2,1,populationcity)
            if typ==2:
                populationcity=populationcity+casucount(False, i,"loser",tr,sidescoreat1,sidescoreat2,sidescoreDef1,sidescoreDef2,sidescoreairat1,sidescoreairat2,sidescoreairDef1,sidescoreairDef2,2,populationcity)
                cons='cons'+str(Listside[i][1])
                if globals()[cons]==1:
                    populationcity=populationcity+casucount(True, i,"loser",tr,sidescoreat1,sidescoreat2,sidescoreDef1,sidescoreDef2,sidescoreairat1,sidescoreairat2,sidescoreairDef1,sidescoreairDef2,2,populationcity)
 
    populationcity=round(populationcity,0)
    print('Civil casualties:',populationcity)

    
if Scoreside1<Scoreside2 :
    who_knows_what_this_even_does(Side1, 1, 2)
elif Scoreside2>Scoreside1:
    who_knows_what_this_even_does(Side2, 2, 1)
else:
    print("Unhandled draw.")
