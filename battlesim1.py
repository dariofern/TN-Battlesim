#!/usr/bin/env python3

#LAND BATTLE SIMULATOR

from unit import load_unit_data

from collections import namedtuple
import pathlib
import random

UNIT_DATA_FILE = f"{pathlib.Path(__file__).parent}/units.csv"

# Load at global scope to avoid loading more than once.
# Tuple ensures immutability.
with open(UNIT_DATA_FILE) as f:
    UNIT_TYPES = tuple(load_unit_data(f))

UnitQuantity = namedtuple("UnitQuantity", ["qty", "qty_conscript"])

def score(t,tadv,tren,wag,wagc,mult,a,b,c,d,e,f,g,h,i,j,k,l,m,n):
    if t==1:
        scoreat=(mult*tadv*(wag*(a*5+b*15+c*8+e*25+f*12+g*20)+wagc*0.3*(h*5+i*15+j*8+l*25+m*12+n*20)))
        scoredef=(mult*tadv*tren*(wag*(a*2+b*15+c*10+d*6+e*6)+wagc*0.3*(h*2+i*15+j*10+k*6+l*6)))
        scoreairat=(mult*(wag*(d*15+f*12)+wagc*0.3*(k*15+m*12)))
        scoreairdef=(mult*(wag*(f*8+g*10)+wagc*0.3*(m*8+n*10)))
    if t==2:
        scoreat=(mult*(wag*(a*60+b*40+c*45+d*50+e*10+f*0.5+g*20*1.5)+wagc*0.3*(h*60+i*40+j*45+k*50+l*10+m*0.5+n*20*1.5)))
        scoredef=(mult*(wag*(a*60+b*30+c*45+d*30+e*30)+wagc*0.3*(h*60+i*30+j*45+k*30+l*30)))
        scoreairat=(mult*(wag*(b*40*0.25+c*45*0.25+e*10*0.5+f*12)+wagc*0.3*(i*40*0.25+j*45*0.25+l*10*0.5+m*12)))
        scoreairdef=(mult*(wag*(f*8+g*10)+wagc*0.3*(m*8+n*10)))
    return[scoreat,scoredef,scoreairat,scoreairdef]
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

    national_units = {}
    national_units.setdefault(UnitQuantity(0, 0))
    allowed_classes = set()

    # Land battle
    if typ == 1:
        allowed_classes |= {"land", "air"}
    # Naval battle
    elif typ == 2:
        # TODO needs to allow fighters for coastal battles.
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
        qty = input_positive_integer(f"{unit.name} : ")
        qty_conscripts = 0
        if globals()[cons] == 1:
            qty_conscript = input_positive_integer(f"conscript {unit.name} : ")
        national_units[unit.name] = UnitQuantity(qty, qty_conscript)

    # Set all global variables for troop types. *insert woozy face emoji*
    Inf='Inf'+str(n)
    globals()[Inf] = national_units.get("infantry").qty
    CInf='CInf'+str(n)
    globals()[CInf] = national_units.get("infantry").qty_conscript
    Tanks='Tanks'+str(n)
    globals()[Tanks] = national_units.get("tank").qty
    CTanks='CTanks'+str(n)
    globals()[CTanks] = national_units.get("tank").qty_conscript
    AFV='AFV'+str(n)
    globals()[AFV] = national_units.get("AFV").qty
    CAFV='CAFV'+str(n)
    globals()[CAFV] = national_units.get("AFV").qty_conscript
    AAA='AAA'+str(n)
    globals()[AAA] = national_units.get("AAA").qty
    CAAA='CAAA'+str(n)
    globals()[CAAA] = national_units.get("AAA").qty_conscript
    FA='FA'+str(n)
    globals()[FA] = national_units.get("FA").qty
    CFA='CFA'+str(n)
    globals()[CFA] = national_units.get("FA").qty_conscript
    Fighter='Fighter'+str(n)
    globals()[Fighter] = national_units.get("fighter").qty
    CFighter='CFighter'+str(n)
    globals()[CFighter] = national_units.get("fighter").qty_conscript
    Bomber='Bomber'+str(n)
    globals()[Bomber] = national_units.get("bomber").qty
    CBomber='CBomber'+str(n)
    globals()[CBomber] = national_units.get("bomber").qty_conscript
    BattleS='BattleS'+str(n)
    globals()[BattleS] = national_units.get("battleship").qty
    CBattleS='CBattleS'+str(n)
    globals()[CBattleS] =national_units.get("battleship").qty_conscript
    Destroyer='Destroyers'+str(n)
    globals()[Destroyer] = national_units.get("destroyer").qty
    CDestroyer='CDestroyers'+str(n)
    globals()[CDestroyer] = national_units.get("destroyer").qty_conscript
    Cruisers='Cruisers'+str(n)
    globals()[Cruisers] = national_units.get("cruiser").qty
    CCruisers = 'CCruisers'+str(n)
    globals()[CCruisers] = national_units.get("cruiser.").qty_conscript
    Uboat='Uboat'+str(n)
    globals()[Uboat] = national_units.get("uboat").qty
    CUboat='CUboat'+str(n)
    globals()[CUboat] = national_units.get("uboat").qty_conscript
    TroopS='TroopS'+str(n)
    globals()[TroopS] = national_units.get("troopship").qty
    CTroopS='CTroopS'+str(n)
    globals()[CTroopS] = national_units.get("troopship").qty_conscript

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
    scoreteam=0
    if typ==1:
        scoreteam= score(1,globals()[Tadv],globals()[Entrench],globals()[Wage],globals()[CWage],globals()[Multi],globals()[Inf],globals()[Tanks],globals()[AFV],globals()[AAA],globals()[FA],globals()[Fighter],globals()[Bomber],globals()[CInf],globals()[CTanks],globals()[CAFV],globals()[CAAA],globals()[CFA],globals()[CFighter],globals()[CBomber])
    if typ==2:
        scoreteam= score(2,1,1,globals()[Wage],globals()[CWage],globals()[Multi],globals()[BattleS],globals()[Destroyer],globals()[Cruisers],globals()[Uboat],globals()[TroopS],globals()[Fighter],globals()[Bomber],globals()[CBattleS],globals()[CDestroyer],globals()[CCruisers],globals()[CUboat],globals()[CTroopS],globals()[CFighter],globals()[CBomber])
    scoreat = scoreteam[0]+scoreteam[2]
    scoredef = scoreteam[1]+scoreteam[3]
    scoreairat = scoreteam[2]
    scoreairdef = scoreteam[3]
    li.append([nsid,n])
    return [scoreat,scoredef,scoreairat,scoreairdef]

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
            
