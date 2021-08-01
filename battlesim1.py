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

def army_strength(units, wage_factor, terrain_factor,
                  entrenchment_factor, luck_factor, conscript_factor=1):
    """
    Compute the offensive and defensive score of an army.

    Wage, terrain advantage, entrenchment, a luck factor and a
    conscription factor (default 1 ) are all taken into account.
    Factors may not be 0, but resulting army strength may be.
    """
    # These checks could be redundant, but good to have just in case.
    if wage_factor <= 0:
        raise ValueError("Wage factor must be greater than 0.")
    if terrain_factor <= 0:
        raise ValueError("Terrain factor must be greater than 0.")
    if entrenchment_factor <= 0:
        raise ValueError("Entrenchment factor must be greater than 0.")
    if luck_factor <= 0:
        raise ValueError("Luck factor must be greater than 0.")
    if conscript_factor <= 0:
        raise ValueError("Conscript factor must be greater than 0.")

    offense = 0
    defense = 0
    # Sum up base unit stats.
    for name, qty in units.items():
        # If we used the Unit as the key we wouldn't have to lookup.
        for unit in UNIT_TYPES:
            if unit.name == name:
                offense += unit.attack * qty
                defense += unit.defense * qty
                break
        else:
            raise ValueError(f"Unit {name} not recognized!")

    # Apply modifiers.
    offense *= wage_factor * terrain_factor * luck_factor * conscript_factor
    defense *= wage_factor * terrain_factor * entrenchment_factor * \
               luck_factor * conscript_factor
    return offense, defense

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
        if typ==1:
            casu[0]=casu[0]+wounded*mult
            casu[1]=casu[1]+deaths*mult
        if typ==2:
            woundedDeath=random.randint(0, 10)
            deathDeath=random.randint(50, 100)
            woundedWounded=woundedDeath+15
            woundedWounded=random.randint(0,woundedWounded)
            deathWounded=100-deathDeath
            deathWounded=random.randint(0,deathWounded)
            casu[0]=casu[0]+round(wounded*mult*woundedWounded/100+deaths*mult*deathWounded/100,0)
            casu[1]=casu[1]+round(deaths*mult*(deathDeath/100)+wounded*mult*(woundedDeath/100),0)
        print(remaining,'/',wounded,'/',deaths)
    if status=='loser':
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
        if typ==1:
            casu[0]=casu[0]+wounded*mult
            casu[1]=casu[1]+deaths*mult
        if typ==2:
            woundedDeath=random.randint(0, 10)
            deathDeath=random.randint(50, 100)
            woundedWounded=woundedDeath+15
            woundedWounded=random.randint(0,woundedWounded)
            deathWounded=100-deathDeath
            deathWounded=random.randint(0,deathWounded)
            casu[0]=casu[0]+round(wounded*mult*woundedWounded/100+deaths*mult*deathWounded/100,0)
            casu[1]=casu[1]+round(deaths*mult*(deathDeath/100)+wounded*mult*(woundedDeath/100),0)
        print(remaining,'/',wounded,'/',deaths)
    return()

def filter_units(units, classes):
    """
    Filter units returning those in the specified classes.
    """
    filtered_units = {}
    for name, qty in units.items():
        for unit in UNIT_TYPES:
            if unit.name == name:
                if unit.unit_class in classes:
                    filtered_units[name] = qty
                break
        else:
            raise ValueError(f"Unit {name} not recognized!")
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
        professionals[unit.name] = input_positive_integer(f"{unit.name} : ")
        if globals()[cons] == 1:
            conscripts[unit.name] = input_positive_integer(
                f"conscript {unit.name} : ")

    # Set all global variables for troop types. *insert woozy face emoji*
    Inf='Inf'+str(n)
    globals()[Inf] = professionals["infantry"]
    CInf='CInf'+str(n)
    globals()[CInf] = conscripts["infantry"]
    Tanks='Tanks'+str(n)
    globals()[Tanks] = professionals["tank"]
    CTanks='CTanks'+str(n)
    globals()[CTanks] = conscripts["tank"]
    AFV='AFV'+str(n)
    globals()[AFV] = professionals["AFV"]
    CAFV='CAFV'+str(n)
    globals()[CAFV] = conscripts["AFV"]
    AAA='AAA'+str(n)
    globals()[AAA] = professionals["AAA"]
    CAAA='CAAA'+str(n)
    globals()[CAAA] = conscripts["AAA"]
    FA='FA'+str(n)
    globals()[FA] = professionals["FA"]
    CFA='CFA'+str(n)
    globals()[CFA] = conscripts["FA"]
    Fighter='Fighter'+str(n)
    globals()[Fighter] = professionals["fighter"]
    CFighter='CFighter'+str(n)
    globals()[CFighter] = conscripts["fighter"]
    Bomber='Bomber'+str(n)
    globals()[Bomber] = professionals["bomber"]
    CBomber='CBomber'+str(n)
    globals()[CBomber] = conscripts["bomber"]
    BattleS='BattleS'+str(n)
    globals()[BattleS] = professionals["battleship"]
    CBattleS='CBattleS'+str(n)
    globals()[CBattleS] = conscripts["battleship"]
    Destroyer='Destroyer'+str(n)
    globals()[Destroyer] = professionals["destroyer"]
    CDestroyer='CDestroyer'+str(n)
    globals()[CDestroyer] = conscripts["destroyer"]
    Cruisers='Cruisers'+str(n)
    globals()[Cruisers] = professionals["cruiser"]
    CCruisers = 'CCruisers'+str(n)
    globals()[CCruisers] = conscripts["cruiser"]
    Uboat='Uboat'+str(n)
    globals()[Uboat] = professionals["uboat"]
    CUboat='CUboat'+str(n)
    globals()[CUboat] = conscripts["uboat"]
    TroopS='TroopS'+str(n)
    globals()[TroopS] = professionals["troopship"]
    CTroopS='CTroopS'+str(n)
    globals()[CTroopS] = conscripts["troopship"]

    tr='tr'+str(n)
    if (globals()[TroopS]+globals()[CTroopS])!=0:
        globals()[tr]=round(int(input("Number of soldiers transported by troopships"))/(globals()[TroopS]+globals()[CTroopS]),0)
    else:
        globals()[tr]=0

    print("Country stats :")

    Part='Part'+str(n)
    globals()[Part] = ((int(input("Military budget (without the $ and no commas) : ")))/100000000000)+1
    Rese='Rese'+str(n)
    globals()[Rese] = ((int(input("Research budget (without the $ and no commas) : ")))/100000000000)+1
    Wage='Wage'+str(n)
    globals()[Wage] = (((int(input("Wage level (1-4) : ")))-1)/10)+1
    CWage='CWage'+str(n)
    globals()[CWage] = (((int(input("Conscript Wage level (1-4) : ")))-1)/4)+1
    Tired='Tired'+str(n)
    globals()[Tired] = (1-(int(input("Recent Battles (one year) : "))/20))
    Morale='Morale'+str(n)
    Mor = (10 - (int(input("Recent Battles lost (one year) : "))))+(int(input("Recent Battles won (one year) : ")))
    if Mor > 10 :
        Mor = 10
    if Mor < 1 :
        Mor = 1
    else:
        Mor = Mor
    globals()[Morale] = 1+((-5+Mor)/20)
    
    if typ==1:

        Terrain='Terrain'+str(n)
        globals()[Terrain] = 1+((int(input("Terrain Knowledge (out of 5) : "))-3)/20)
        Climate='Climate'+str(n)
        globals()[Climate] = 0.25+(float(input("Climate malus : ")))
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
        globals()[Tadv]=1+(hill+river+city-landing)/2
        Supply='Supply'+str(n)
        globals()[Supply] = 1-(int(input("Supply line cut ? [0]:no [1]:yes"))/3)

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
                                   
    Luck = 'Luck'+str(n)
    globals()[Luck] = (random.randint(85, 112))/100
    GenDef = 'GenDef'+str(n)
    globals()[GenDef] = int(input("General's defense skills : "))
    GenOff = 'GenOff'+str(n)
    globals()[GenOff] = int(input("General's attack skills : "))
    TacticOff = 'TacticOff'+str(n)
    globals()[TacticOff] = float(input("Offensive Tactic bonus : "))*(1+(globals()[GenOff])/20)
    TacticDef = 'TacticDef'+str(n)
    globals()[TacticDef] = float(input("Defensive Tactic bonus : "))*(1+(globals()[GenDef])/20)
    Multi = 'Multi'+str(n)  
    globals()[Multi] = globals()[Supply]*globals()[Rese]*globals()[Luck]*globals()[Climate]*globals()[Terrain]*globals()[Morale]*globals()[Tired]*globals()[Part]*globals()[TacticOff]*globals()[TacticDef]

    prof_off, prof_def = army_strength(
        units=filter_units(professionals, {"land", "naval"}),
        wage_factor=globals()[Wage],
        terrain_factor=globals()[Tadv],
        entrenchment_factor=globals()[Entrench],
        luck_factor=globals()[Multi])

    conscript_off, conscript_def = army_strength(
        units=filter_units(conscripts, {"land", "naval"}),
        wage_factor=globals()[CWage],
        terrain_factor=globals()[Tadv],
        entrenchment_factor=globals()[Entrench],
        luck_factor=globals()[Multi],
        conscript_factor=0.3)

    air_prof_off, air_prof_def = army_strength(
        units=filter_units(professionals, {"air"}),
        wage_factor=globals()[Wage],
        terrain_factor=1,
        entrenchment_factor=1,
        luck_factor=globals()[Multi])

    air_conscript_off, air_conscript_def = army_strength(
        units=filter_units(conscripts, {"air"}),
        wage_factor=globals()[CWage],
        terrain_factor=1,
        entrenchment_factor=1,
        luck_factor=globals()[Multi],
        conscript_factor=0.3)

    li.append([nsid,n])
    return (prof_off + conscript_off + air_prof_off + air_conscript_off,
            prof_def + conscript_def, + air_prof_def, + air_conscript_def,
            air_prof_off + air_conscript_off,
            air_prof_def + air_conscript_def)

def casucount(a,b,c,d,e,f,g,i,s,tr,scatW,scatL,scdefW,scdefL,scatWair,scatLair,scdefWair,scdefLair,typ,pop):
    if a==Inf or a==CInf :
        am=1
        if a==CInf:
            namea="Conscripted Infantrymen"
            Consa=1.5
        if a==Inf :
            namea="Infantrymen"
            Consa=1
    else :
        am=850
        if a==CBattleS:
            namea="Conscript Battleships"
            Consa=1.5
        if a==BattleS:
            namea="Battleships"
            Consa=1
            
    if b==Tanks or b==CTanks :
        bm=5
        if b==CTanks :
            nameb="Conscript Tanks"
            Consb=1.5
        if b==Tanks :
            nameb="Tanks"
            Consb=1
    else :
        bm=450
        if b==CDestroyer:
            nameb="Conscript Destroyers"
            Consb=1.5
        if b==Destroyer :
            nameb="Destroyers"
            Consb=2
        
    if c==AFV or c==CAFV :
        cm=4
        if c==CAFV:
            namec="Conscript AFVs"
            Consc=1.5
        if c==AFV :
            namec="AFVs"
            Consc=1
    else :
        cm=600
        if c==CCruisers:
            namec="Conscript Cruisers"
            Consc=1.5
        if c==Cruisers:
            namec="Cruisers"
            Consc=1
        
    if d==AAA or d==CAAA:
        dm=3
        if d==CAAA:
            named="Conscript AAA cannons"
            Consd=1.5
        if d==AAA :
            named="AAA cannons"
            Consd=1
    else :
        dm=50
        if d==CUboat :
            named="Conscript Uboats"
            Consd=3
        if d==Uboat :
            named="Uboats"
            Consd=2
        
    if e==FA or e==CFA :
        em=3
        if e==CFA:
            namee="Conscript FA cannons"
            Conse=1.5
        if e==FA :
            namee="FA cannons"
            Conse=1
    else :
        em=6+(globals()[tr])
        if e==CTroopS:
            namee="Conscript Troopships"
            Conse=1.5
        if e==TroopS :
            namee="Troopships"
            Conse=1

    if f==CFighter:
        namef="Conscript Fighters"
        Consf=3
    if f==Fighter:
        namef="Fighters"
        Consf=2

    if g==CBomber:
        nameg="Conscript Bombers"
        Consg=3
    if g==Bomber:
        nameg="Bombers"
        Consg=2
        
        
    
    print("------------------------------------------------------------------------")
    casualties1=[0,0]
    teamname='Team'+str(Listside[i][1])
    
    print(str(globals()[teamname]),"'s",namea," remaining / wounded(damaged if battleship) / dead(destroyed if battleship):",end=' ')
    print(casualties(globals()[a],scatW,scatL,scdefW,scdefL,s,casualties1,sidenat1,am,Consa,typ,0))
    
    print(str(globals()[teamname]),"'s",nameb," remaining / damaged / destroyed:",end=' ')
    print(casualties(globals()[b],scatW,scatL,scdefW,scdefL,s,casualties1,sidenat1,bm,Consb,typ,0))
    
    print(str(globals()[teamname]),"'s",namec," remaining / damaged / destroyed:",end=' ')
    print(casualties(globals()[c],scatW,scatL,scdefW,scdefL,s,casualties1,sidenat1,cm,Consc,typ,0))
    
    print(str(globals()[teamname]),"'s",named," remaining / damaged / destroyed:",end=' ')
    print(casualties(globals()[d],scatW,scatL,scdefW,scdefL,s,casualties1,sidenat1,dm,Consd,typ,0))
    
    print(str(globals()[teamname]),"'s",namee," remaining / damaged / destroyed:",end=' ')
    print(casualties(globals()[e],scatW,scatL,scdefW,scdefL,s,casualties1,sidenat1,em,Conse,typ,0))

    if (s=='winner' and scdefWair!=0 and scatLair==0) or (s=='loser' and scdefLair!=0 and scatWair==0):
        
        print(str(globals()[teamname]),"'s",namef," remaining / damaged / destroyed:",end=' ')
        print(globals()[f],'/ 0 / 0')
        print()
        
        print(str(globals()[teamname]),"'s",nameg," remaining / damaged / destroyed:",end=' ')
        print(globals()[g],'/ 0 /0')
        print()
        
    if (s=='winner' and scdefWair!=0 and scatLair!=0) or (s=='loser' and scdefLair!=0 and scatWair!=0) :
            
        print(str(globals()[teamname]),"'s",namef," remaining / damaged / destroyed:",end=' ')
        print(casualties(globals()[f],scatWair,scatLair,scdefWair,scdefLair,s,casualties1,sidenat1,1,Consf,1,1))
    
        print(str(globals()[teamname]),"'s",nameg," remaining / damaged / destroyed:",end=' ')
        print(casualties(globals()[g],scatWair,scatLair,scdefWair,scdefLair,s,casualties1,sidenat1,3,Consg,1,1))
          
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
    print()
    print(str(side)," won the battle!")
    Listside.sort()
    for i in range (0,number-1):
        if Listside[i][0] == win:
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
            if typ==1:
                populationcity=populationcity+casucount(Inf,Tanks,AFV,AAA,FA,Fighter,Bomber,i,"winner",0,sidescoreat1,sidescoreat2,sidescoreDef1,sidescoreDef2,sidescoreairat1,sidescoreairat2,sidescoreairDef1,sidescoreairDef2,1,populationcity)
                cons='cons'+str(Listside[i][1])
                if globals()[cons]==1:
                    populationcity=populationcity+casucount(CInf,CTanks,CAFV,CAAA,CFA,CFighter,CBomber,i,"winner",0,sidescoreat1,sidescoreat2,sidescoreDef1,sidescoreDef2,sidescoreairat1,sidescoreairat2,sidescoreairDef1,sidescoreairDef2,1,populationcity)
            if typ==2:
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
                populationcity=populationcity+casucount(BattleS,Destroyer,Cruisers,Uboat,TroopS,Fighter,Bomber,i,"winner",tr,sidescoreat1,sidescoreat2,sidescoreDef1,sidescoreDef2,sidescoreairat1,sidescoreairat2,sidescoreairDef1,sidescoreairDef2,2,populationcity)
                cons='cons'+str(Listside[i][1])
                if globals()[cons]==1:
                    populationcity=populationcity+casucount(CBattleS,CDestroyer,CCruisers,CUboat,CTroopS,CFighter,CBomber,i,"winner",tr,sidescoreat1,sidescoreat2,sidescoreDef1,sidescoreDef2,sidescoreairat1,sidescoreairat2,sidescoreairDef1,sidescoreairDef2,2,populationcity)
        if Listside[i][0] == loss:
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
            if typ==1:
                populationcity=populationcity+casucount(Inf,Tanks,AFV,AAA,FA,Fighter,Bomber,i,"loser",0,sidescoreat1,sidescoreat2,sidescoreDef1,sidescoreDef2,sidescoreairat1,sidescoreairat2,sidescoreairDef1,sidescoreairDef2,1,populationcity)
                cons='cons'+str(Listside[i][1])
                if globals()[cons]==1:
                    populationcity=populationcity+casucount(CInf,CTanks,CAFV,CAAA,CFA,CFighter,CBomber,i,"loser",0,sidescoreat1,sidescoreat2,sidescoreDef1,sidescoreDef2,sidescoreairat1,sidescoreairat2,sidescoreairDef1,sidescoreairDef2,1,populationcity)
            if typ==2:
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
                populationcity=populationcity+casucount(BattleS,Destroyer,Cruisers,Uboat,TroopS,Fighter,Bomber,i,"loser",tr,sidescoreat1,sidescoreat2,sidescoreDef1,sidescoreDef2,sidescoreairat1,sidescoreairat2,sidescoreairDef1,sidescoreairDef2,2,populationcity)
                cons='cons'+str(Listside[i][1])
                if globals()[cons]==1:
                    populationcity=populationcity+casucount(CBattleS,CDestroyer,CCruisers,CUboat,CTroopS,CFighter,CBomber,i,"loser",tr,sidescoreat1,sidescoreat2,sidescoreDef1,sidescoreDef2,sidescoreairat1,sidescoreairat2,sidescoreairDef1,sidescoreairDef2,2,populationcity)
 
    populationcity=round(populationcity,0)
    print('Civil casualties:',populationcity)

    
if Scoreside1<Scoreside2 :
    who_knows_what_this_even_does(Side1, 1, 2)
else:
    who_knows_what_this_even_does(Side2, 2, 1)
            
