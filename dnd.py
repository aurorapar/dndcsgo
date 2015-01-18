#########
#           DND:GO Alpha
#           Aurora Pariseau   ______   ____  _____  ______       ______      __    
#                             |_   _ `.|_   \|  _|  ||_   _ `.  _ .' ___   | .' `.  
#                             | | `. \ |   \   \    | | `. \(_)/ .'   \_| /  .-.  \ 
#                             | |  | | | |\ \   \   | |  | | _ | |   ____ | |   | | 
#                             |_| |_.' /_| |_\   \__| |_.' /(_)\ `.___]  |\  `-'  / 
#                             |______.'|_____|\____||______.'   `._____.'  `.___.'
# 
#
#########

# Need gamethread functions
#   1. Prune inactive players

import messages, os.path, time, pickle, random

from commands.client import ClientCommand
from commands.say import SayCommand

from entities import helpers
from entities.constants import damage_types

from events import Event

from menus import SimpleMenu
from menus import Option
from menus import Text

from paths import GAME_PATH

from players import PlayerGenerator
from players.entity import PlayerEntity
from players.helpers import *

from listeners.tick import TickRepeat
from listeners.tick import TickRepeatStatus

# Import pickle file at end of script

#After this amount of time inactivity, will delete inactive user. Time is in seconds
pruneTime = 1209600 #two weeks

classes = ['Fighter', 'Rogue', 'Cleric', 'Wizard', 'Paladin', 'Ranger', 'Monk', 'Bard', 'Necromancer']
races = ['Human', 'Dwarf', 'Elf', 'Orc', 'Halfling', 'Gray Elf', 'Kobold']
laracesList = ['Aasimar', 'Tiefling', 'Minotaur', 'Drow', 'Avariel', 'Doppleganger', 'Vampire', 'Troll']
weaponlist = [
            ['Fighter','All except autosnipers\nGains AWP at 10'],
            ['Rogue','All Pistols\nMP7 UMP TMP Mac10\nSSG 08'],
            ['Cleric','All Pistols\nFamas Galil\nM249 Negev'],
            ['Wizard', 'All Pistols except Deagle'],
            ['Paladin','All Weapons'],
            ['Ranger','Duals OR Scout'],
            ['Bard','All Pistols and SMGS\nScout Galil Famas'],
            ['Monk','Knife ONLY'],
            ['Necromancer','Glock USP P2000\nAt level 15, Elites and FiveSeveN']
        ]
            
prestiges = {
        'Grenadier':['Fighter', 5],
        'Kensai':['Fighter', 10],
        'Exotic Weapons Dancer':['Fighter', 15],
        'Acrobat':['Rogue', 5], 
        'Assassin':['Rogue', 10],
        'Shadow Dancer':['Rogue', 15],
        'War Mage':['Wizard', 5],
        'Mage of Arcane Order':['Wizard', 10], 
        'Arch Mage':['Wizard', 15], 
        'War Priest':['Cleric', 5],
        'Divine Oracle':['Cleric', 10], 
        'Hierophant':['Cleric', 15]
        }
        
laraces = { 'Aasimar':1,
            'Tiefling':1,
            'Minotaur':2,
            'Drow':2,
            'Avariel':3,
            'Doppleganger':4,
            'Vampire':8,
            'Troll':9
        }
        
xp = {  'killxp': 80,
        'suicidexp': 80,
        'headshotxp': 60,
        'knifexp': 150,
        'bombxp': 70,
        'bombexxp': 50,
        'defusexp':50,
        'hostagexp': 40,
        'hexp': 80,
        'tkpenxp': 300,
        'classlevel': 1000,
        'prestigelevel': 1250,
        'humbxp': 55,
        'zombiexp': 150,
        'ks_xp': 15,
        'bounty_xp': 30,
        'high_xp': 15,
        'rnd_xp': 35,
        'monster_levelxp': 30000
    }
        
infomenu = {
        'Fighter':' Class: Fighter\n Weapons: All except AWP and Autos (AWP gained at level 10)\n Overview: Gives bonus damage, takes less damage,\n along with drugging attacks',
        'Rogue':' Class: Rogue\n Weapons: All pistols, TMP, MP5, Mac10, Scout\n Overview: Gains stealth, and more stealth with levels,\n bonus damage when stealthed (sneak attack), slows, dodges, and steals cash',
        'Cleric':' Class: Cleric\n Weapons: All pistols, Famas, Galil, M249\n Overview: Has two sides, !good and !evil\n Can heal or deal damage, stun, resurrect,\n purge debuffs or give debuffs, uses !spells',
        'Wizard':' Class: Wizard\n Weapons: All pistols except Deagle\n Overview: Has damage !spells, sleep spell (stun + blind), can\n teleport and has an insta-kill spell and a god mode spell.',
        'Paladin':' Class: Paladin\n Weapons: All Weapons\n Overview: Paladins can heal, are immune to crits, burn enemies they shoot,\n and have bonus health and regen',
        'Ranger':' Class: Ranger\n Weapons: Elites OR Scout\n Overview: Rangers use one of two styles of combat:\n !dual Uses elites with bonus damage, speed, and drug attacks\n !archer Uses scout with bonus damage and stealth',
        'Monk':' Class: Monk\n Weapons: Knife only (no exceptions)\n Overview: Invisible knife class that has bonus damage and\n increased speed. It can use !escape and gets !teleport 1/round',
        'Bard':' Class: Bard\n Weapons: Pistols, SMGs, Scout, Galil, Famas\n Overview: Buffs their team with AOE abilities like\n speed abd damage, and some damaging songs',
        'Necromancer':' Class: Necromancer: \n Weapons: Pistols (except Deagle)\n Overview: Uses fire skills along with raising dead\n team mates as zombies and ghouls',
        'Grenadier':' Prestige: Grenadier\n Requires Fighter Level 5\n Overview: The Grendier has powerful and versatile different grenades\n along with free grenades',
        'Kensai':' Prestige: Kensai\n Requires Fighter Level 10\n Overview: The Kensai boosts their attacks with special abilities\n every round with points. Points are earned with levels',
        'Exotic Weapons Dancer':' Prestige: Exotic Weapons Dancer\n Requires Fighter Level 15\n Overview: Gains acess to Auto Snipers and deals extra\n damage with them and the AWP',
        'Acrobat':' Prestige: Acrobat\n Requires Rogue Level 5\n Overview: Has lowered gravity and much increased speed',
        'Assassin':' Prestige: Assassin\n Requires Rogue Level 10\n Overview: Gains a !deathattack, where you remain still and\n once ready, your next attack has the chance to instantly kill',
        'Shadow Dancer':' Prestige: Shadow Dancer\n Requres Rogue Level 15\n Overview: Only your knife is invisible, and you can only use the knife',
        'War Mage':' Prestige: War Mage\n Requires Wizard Level 5\n Overview: Allows the Wizard to use Mac10 and TMP\n and has unique spells',
        'Mage of Arcane Order':' Prestige: Mage of Arcane Order\n Requires Wizard Level 10\n Overview: Gains !meteor, a massive AOE damage spell',
        'Arch Mage':' Prestige: Arch Mage\n Requires Wizard Level 15\n Overview: Reduces the chance your spells are resisted',
        'War Priest':' Prestige: War Priest\n Requires Cleric Level 5\n Overview: Gains P90, AWP, M4A1 and AK47 and new spells',
        'Divine Oracle':' Prestige: Divine Oracle\n Requires Cleric Level 10\n Overview: Divine intervention has a chance to prevent damage\n (Subject to change)',
        'Hierophant':' Prestige: Hierophant\n Requires Cleric Level 15\n Overview: Increases healing or damage of existing spells,\n and makes them harder to resist',
        'Human':' Race: Human\n Passive Powers:\n %s bonus XP per kill'%xp['humbxp'],
        'Dwarf':' Race: Dwarf\n Passive Powers:\n +10 Health\n -10% Cash',
        'Elf':' Race: Elf\n Passive Powers:\n -10 if stealthed or +2% speed\n -10 Health\n Extra Weapons: Scout, M4A1, AK47',
        'Orc':' Race: Orc\n Passive Powers:\n 10% Damage\n -10% Cash\n -10 Mana',
        'Halfling':' Race: Halfling\n Passive Powers:\n -50 color if stealthed or +2% speed\n 70% gravity\n -20% speed\n -5% Damage',
        'Gray Elf':' Race: Gray Elf\n Passive Powers:\n +10 Mana\n -10 color if stealthed or +2% speed\n -10 Health\n -5% Damage\n Extra Weapons: UMP, P90',
        'Kobold':' Race: Kobold\n Passive Powers:\n Fire Grenades\n Free Grenade\n -10 Health\n -10% Damage\n Commands:\n !escape',
        'Aasimar':' Race: Aasimar\n Level Adjustment: 1\n Passive Powers:\n +5 Team Health\n 5% Damage Reduction\n +10% Cash\n Bonus Weapon: UMP',
        'Tiefling':' Race: Tiefling\n Level Adjustment: 1\n Passive Powers:\n -5 Enemy Team Health\n +10 Mana on spawn\n -10% Cash on spawn\n -10 color if stealthed or 2% speed\n Bonus Weapon',
        'Minotaur':' Race: Minotaur\n Level Adjustment: 2\n Passive Powers:\n +20% Damage\n -20 Mana\n -20% Cash\n +60 Color\n 20% Damage Reduction\n Bonus Weapon: M249',
        'Drow':' Race: Drow\n Level Adjustment: 2\n Passive Powers:\n 4 Doses of Poison\n +10 Mana\n +10% Cash\n -10 Health\n -10 color color if stealthed or 2% speed\n Commands:\n !lev0 !lev1',
        'Avariel':' Race: Avariel\n Level Adjustment: 3\n Passive Powers:\n +10 Mana\n -10 Health\n -20 if stealthed or +4% speed\n Bonus Weapon: Scount\n Commands:\n !lev0 !lev1 !lev2 !lev3',
        'Doppleganger':' Race: Doppleganger\n Level Adjustment: 4\n Passive Powers:\n 20% Damage Reduction\n +10 Mana\n +10 Health\n -10 if stealthed or +2% speed\n Camoflauged as enemy\n +10% Damage\n +10% Cash',
        'Vampire':' Race: Vampire\n Level Adjustment: 8\n Passive Powers:\n -90 Health\n 5hp/6s regen\n +15% Damage\n +10% Cash\n 40% Life Steal\n -20 if stealthed or +4% Speed\n Commands:\n !lev0 !lev1 !lev2 !lev3\n 2/round !stealth',
        'Troll':' Race: Troll\n Level Adjustment: 9\n Passive Powers:\n +60 Health\n +33% Damage\n -20% Cash\n -20 Mana\n +20 color if stealthed'
}
    
statusEffectsList = ['drug','regen','stun', 'freeze', 'slow', 'burn']
statusEffects = {}
for status in statusEffectsList:
    statusEffects[status] = []
    
timers = []

#Weapon Allowances here
weapons = {}
for x in classes:
    weapons[x] = []
for x in races:
    weapons[x] = []
weapons['Elf'] = ['m4a1','ak47','scout']
        
########################################################################
# EVENTS                                                               #
########################################################################
@Event
def item_pickup(game_event):
    player = dndPlayerDictionary[game_event.get_int('userid')]
    weapon_index = game_event.get_int('index')    
    #tell(playerinfo_from_userid(userid), dir(weapon))
    weapon = BaseEntity(weapon_index)
    #player.drop_weapon(weapon)
    '''
    if weapon.name not in weapons[player.getClass()] or weapons[player.getRace()]:
        player.drop_weapon(weapon.pointer, True, True)
        weapon.remove()
        tell(player.playerinfo, "Your class is not allowed to use that weapon")
    '''

@Event
def round_end(game_event):
    saveDatabase()
    for x,y in PlayerDataDictionary.items():
        if int(time.clock()) - int(PlayerDataDictionary[x]['last connected']) > int(pruneTime):
            msg('%s\'s XP and Levels were deleted for inactivity (2 weeks)'%PlayerDataDictionary[x].name)
            PlayerDataDictionary[x] = {}
    winners = game_event.get_int('winner')
    for players in PlayerGenerator():
        if players.get_team_index == winners:
            dndPlayerDictionary[userid_from_playerinfo(players)].giveXp(xp['rnd_xp'], 'for winning the round!')               
            
@Event
def round_start(game_event):
    msg('Welcome to D&D!')
        
@Event
def bomb_planted(game_event):
    userid = dndPlayerDictionary[game_event.get_int('userid')]
    userid.giveXp(xp['bombxp'], 'for planting the bomb!')
    
@Event
def bomb_exploded(game_event):
    userid = dndPlayerDictionary[game_event.get_int('userid')]
    userid.giveXp(xp['bombexxp'], 'for the bomb exploding!')
    
@Event
def bomb_defused(game_event):
    userid = dndPlayerDictionary[game_event.get_int('userid')]
    userid.giveXp(xp['defusexp'], 'for defusing the bomb!')
    
@Event
def hostage_rescued(game_event):
    userid = dndPlayerDictionary[game_event.get_int('userid')]
    userid.giveXp(xp['bombexxp'], 'for rescuing a hostage!')

@Event
def round_prestart(game_event):
    pass
    
@Event
def player_spawn(game_event):
    global timers
    spawnee_userid = game_event.get_int('userid')
    spawnee = dndPlayerDictionary[spawnee_userid]
    tell(spawnee.playerinfo, 'You are playing a %s %s %s'%(spawnee.getRace(), spawnee.getLevel(), spawnee.getClass()))    
    spawnee.reset()

    if spawnee.getRace() == 'Human':
        tell(spawnee.playerinfo, 'You are a fast-learning Human and level quicker')
    if spawnee.getRace() == 'Orc':
        spawnee.damagepercent += 10
        spawnee.set_property_int('m_iAccount', spawnee.get_property_int('m_iAccount') * .9)
        tell(spawnee.playerinfo, 'You are a strong but unfriendly and non-intelligent Orc')
    if spawnee.getRace() == 'Dwarf':
        spawnee.maxhp += 10
        tell(spawnee.playerinfo, spawnee.maxhp)
        spawnee.health = spawnee.maxhp
        spawnee.maxspeed -= .1
        spawnee.speed = spawnee.maxspeed
        spawnee.set_property_int('m_iAccount', spawnee.get_property_int('m_iAccount') * .9)
        tell(spawnee.playerinfo, 'You have an extra 10 HP for being a hardy Dwarf, but are slow and unfriendly')
    if spawnee.getRace() == 'Elf':
        if spawnee.stealth < 255:
            spawnee.addStealth(-10)
            tell(spawnee.playerinfo, 'You are a stealthy and martially-versed Elf')
        else:
            spawnee.maxspeed += .02
            tell(spawnee.playerinfo, 'You are a nimble and martially-versed Elf')
    if spawnee.getRace() == 'Halfling':
        spawnee.damagepercent -= 10
        if spawnee.stealth < 255:
            spawnee.addStealth(-50)
            tell(spawnee.playerinfo, 'You are an incredibly stealthy but weak and slow Halfling')
        else:
            spawnee.maxspeed += .02
            tell(spawnee.playerinfo, 'You are a nimble and acrobatic but weak and slow Halfling')
    if spawnee.getRace() == 'Kobold':
        spawnee.damagepercent -= 10
        spawnee.maxhp -= 10
        spawnee.health = spawnee.maxhp
        spawnee.statusEffects['regen'].append({'duration':3,'effect':1,'intervals':None})
        tell(spawnee.playerinfo, 'You are a Kobold that uses trickery, but are frail and weak')
    if spawnee.getRace() == 'Grey Elf':
        if spawnee.mana > 0:
            spawnee.mana += 10
        if spawnee.stealth < 255:
            spawnee.addStealth(-10)
            tell(spawnee.playerinfo, 'Grey Elves are a stealthy, martially-versed, and cunning but frail and weak')
        else:
            spawnee.maxspeed += .02
            tell(spawnee.playerinfo, 'Grey Elves are a nimble, martially-versed, and cunning but frail and weak')
        
        
@Event
def player_death(game_event):
    attacker_userid = game_event.get_int('attacker')
    
    victim_userid = game_event.get_int('userid')
    victim = dndPlayerDictionary[victim_userid]
    
    if attacker_userid > 1:

        attacker = dndPlayerDictionary[attacker_userid]
            
        killStreak = attacker.getKillSpree()
        victimStreak = victim.getKillSpree()

        if attacker.team != victim.team:
            attacker.giveXp(xp['killxp'], 'for getting a kill!')
            attacker.addKill()
            attacker.addKillingSpree()
            if attacker.getRace() == 'Human':
                attacker.giveXp(xp['humbxp'], 'for being Human')
            if game_event.get_bool('headshot'):
                attacker.giveXp(xp['headshotxp'], 'for getting a headshot!')
            if attacker.getECL() < victim.getECL():
                attacker.giveXp(xp['high_xp'] * (victim.getECL() - attacker.getECL()), 'for killing someone higher level than you!')
            if killStreak > 5:
                attacker.giveXp(xp['ks_xp'] * (killStreak - 5), 'for being on a Killing Streak!')
                msg('%s is on a Killing Streak! Kill them for bonus experience!')
            if victimStreak > 5:
                attacker.giveXp(xp['bounty_xp'] * (victimStreak - 5), 'shutting down %s\'s killing spree!'%attacker.name)
            PlayerDataDictionary[victim.steamid]['spree'] = 0
        else:
            if attacker.name != victim.name:
                attacker.giveXp(-xp['tkpenxp'], 'for killing a team mate')
                attacker.setKills(0)
            
    else:
        victim.giveXp(-xp['suicidexp'], 'for committing suicide')         
        victim.setKills(0)

@Event        
def player_hurt(game_event):
    attacker_userid = game_event.get_int('attacker')
    victim_userid = game_event.get_int('userid')
    damage = game_event.get_int('dmg_health')
    
    attacker = dndPlayerDictionary[attacker_userid]
    victim = dndPlayerDictionary[victim_userid]
    
    damage += damage * (float(100) / float(attacker.damagepercent))
    
    tell(playerinfo_from_userid(attacker_userid), 'victim hp: %s'%victim.health)
    tell(playerinfo_from_userid(attacker_userid), 'victim damage: %s'%damage)
    attacker.damage(victim.index, 1, DamageTypes.NERVEGAS)
    tell(playerinfo_from_userid(attacker_userid), 'victim hp: %s'%victim.health)
    
    if damage > 0:
        victim.removeStealth()
    '''
    if attacker.steamid == 'STEAM_1:1:45055382':
        angleOne = attacker.eye_angle_y
        angleTwo = victim.eye_angle_y
        if abs(angleOne - angleTwo) < 75:
            tell(playerinfo_from_userid(attacker_userid), 'Sneak Attack!')
    
    
    player = PlayerEntity(index_from_userid(victim_userid))
    player.damage(index_from_userid(victim_userid), 1, DamageTypes.NERVEGAS, weapon_index=player.get_primary())
    '''
########################################################################
# CUSTOM FUCTIONS                                                      #
########################################################################
def saveDatabase():
    databaseSaveTimer.stop()
    pickle.dump(PlayerDataDictionary, open(str_path,'wb'))
    msg('Levels saved')
    databaseSaveTimer.start(300,1)
    
databaseSaveTimer = TickRepeat(saveDatabase)
databaseSaveTimer.start(300,1)
    
@SayCommand('!test')
def test(player, teamonly, CCommand):
    print(PlayerEntity(index_from_playerinfo(player)).color)
        
@SayCommand(['!Menu','!menu'])    
def mainMenu(player, teamonly, CCommand):
    mainMenu.send(index_from_playerinfo(player))
    
def mainMenuCallBack(menu, playerIndex, option):
    player = dndPlayerDictionary[userid_from_index(playerIndex)]
    if option.value == 'race':
        #Make sure to do LA races here
        raceMenu.send(playerIndex)
    if option.value == 'class':
        classMenu.send(playerIndex)
    if option.value == 'prestige':
        tell(playerinfo_from_index(playerIndex), 'Prestige classes are not yet implemented')
        buildPrestigeMenu(playerIndex)
    if option.value == 'playerinfo':
        playerInfoMenu(playerIndex)
    if option.value == 'info':
        tell(playerinfo_from_index(playerIndex), 'All information can be found at http://http://dnd-css-mod.wikidot.com/')
        mainInfoMenu.send(playerIndex)
    if option.value == 'stats':
        sendStatsMenu(playerIndex, playerIndex)
        
def playerInfoMenu(playerIndex):
    playerInfo = SimpleMenu()
    playerInfo.append(Text('[D&D] Select a player to see their stats'))
    for player in PlayerGenerator():
        optionIndex = index_from_playerinfo(player)
        playerInfo.append(Option(PlayerEntity(optionIndex).name, optionIndex))
    playerInfo.append(Option('Exit','exit'))
    playerInfo.select_callback = playerInfoMenuCallBack
    playerInfo.send(playerIndex)
    
def playerInfoMenuCallBack(menu,playerIndex,option):
    players = []
    for player in PlayerGenerator():
        players.append(index_from_playerinfo(player))
    if option.value in players:
        sendStatsMenu(playerIndex,option.value)
        
def sendStatsMenu(source, target):
    #takes indexes as args
    myPlayer = dndPlayerDictionary[userid_from_index(target)]
    level, race, myClass, myXP = myPlayer.getLevel(), myPlayer.getRace(), myPlayer.getClass(), myPlayer.getXp()
    statsMenu = SimpleMenu()
    statsMenu.append(Text('[D&D] %s\'s Stats'%myPlayer.name))
    statsMenu.append(Text('  %s'%race))
    statsMenu.append(Text('  %s %s'%(myClass, level)))
    statsMenu.append(Text('  %s / %s'%(myXP, level * 1000)))
    statsMenu.append(Option('Exit', 'exit'))
    statsMenu.send(source)
    
def buildPrestigeMenu(playerIndex):
    myPlayer = dndPlayerDictionary[userid_from_index(playerIndex)]
    myClass = myPlayer.getClass()
    prestigeMenuOptions = []
    for prestige in prestiges:
        if myClass == prestiges[prestige][0]:
            prestigeMenuOptions.append(prestige)
    
    prestigeMenu = SimpleMenu()
    prestigeMenu.append(Text('[D&D] Prestiges'))
    if len(prestigeMenuOptions) > 0:
        for prestige in prestigeMenuOptions:
            prestigeMenu.append(Option(prestige, prestige))
    else:
        prestigeMenu.append(Text('%s has no prestige classes'%myClass))
    prestigeMenu.append(Option('Exit','exit'))
    prestigeMenu.select_callback = prestigeMenuCallBack
    prestigeMenu.send(playerIndex)
    
def prestigeMenuCallBack(menu, playerIndex, option):
    if option.value in prestiges:
        dndPlayerDictionary[userid_from_index(playerIndex)].changeClass(option.value)
        
def mainInfoMenuCallBack(menu, playerIndex, option):
    if option.value == 'races':
        raceInfoMenu.send(playerIndex)
    if option.value == 'classes':
        classInfoMenu.send(playerIndex)
    if option.value == 'commands':
        commandInfoMenu.send(playerIndex)
        
def raceInfoMenuCallBack(menu,playerIndex, option):
    if option.value == 'baseraces':
        baseRaceInfoMenu.send(playerIndex)
    if option.value == 'laraces':
        laRaceInfoMenu.send(playerIndex)

def baseRaceInfoMenuCallBack(menu,playerIndex,option):
    if option.value in infomenu:
        buildInfoMenu(playerIndex, option.value)
        
def laRaceInfoMenuCallBack(menu,playerIndex,option):
    if option.value in infomenu:
        buildInfoMenu(playerIndex, option.value)
        
def classInfoMenuCallBack(menu,playerIndex,option):
    if option.value == 'classes':
        baseClassInfoMenu.send(playerIndex)
    if option.value == 'prestiges':
        prestigeClassInfoMenu.send(playerIndex)
        
def baseClassInfoMenuCallBack(menu,playerIndex,option):
    if option.value in infomenu:
        buildInfoMenu(playerIndex, option.value)
        
def prestigeClassInfoMenuCallBack(menu,playerIndex,option):
    if option.value in infomenu:
        buildInfoMenu(playerIndex, option.value)
        
def buildInfoMenu(playerIndex,item):
    customInfoMenu = SimpleMenu()
    customInfoMenu.append(Text('[D&D] %s Info'%item))
    customInfoMenu.append(Text(infomenu[item]))
    customInfoMenu.append(Option('Exit','exit'))
    customInfoMenu.send(playerIndex)
        
@SayCommand(['!stats', '!stat', '!Stats', '!Stat'])
def sayStats(player, teamonly, CCommand):
    sendStatsMenu(index_from_playerinfo(player), index_from_playerinfo(player))
    
@SayCommand('!info')
def info(player, teamonly, CCommand):
    myItem = ''
    i = 1
    x = CCommand.get_arg_count()
    while i < x:
        myItem = CCommand.get_arg(i).replace('!info ', '')
        i+=1
    if myItem in infomenu:
        m = ShowMenu(slots=0b000011111, time=-1, message=infomenu[myItem])
        m.send(index_from_playerinfo(player))
    else:
        tell(player, 'unknown class or race: %s'%myItem)

def classMenuCallBack(menu, playerIndex, option):
    if option.value != 'exit':
        myPlayer = dndPlayerDictionary[userid_from_index(playerIndex)]
        myPlayer.changeClass(option.value)
        
@SayCommand('!class')
def switchClass(player, teamonly, CCommand):
    myPlayer = dndPlayerDictionary[userid_from_playerinfo(player)]
    newClass = ''
    i = 1
    x = CCommand.get_arg_count()
    while i < x:
        newClass = CCommand.get_arg(i).replace('!class ','')
        i+=1
    myPlayer.changeClass(newClass)        
    
def raceMenuCallBack(menu, playerIndex, option):
    if option.value != 'exit':
        myPlayer = dndPlayerDictionary[userid_from_index(playerIndex)]
        myPlayer.changeRace(option.value)
    
@SayCommand('!race')
def switchRace(player, teamonly, CCommand):
    myPlayer = dndPlayerDictionary[userid_from_playerinfo(player)]
    newRace = ''
    i = 1
    x = CCommand.get_arg_count()
    while i < x:
        newRace = CCommand.get_arg(i).replace('!race ','')
        i+=1        
    myPlayer.changeRace(newRace)        

def msg(the_message):
    formatted_message = '\x04[D&D] \x01%s'%the_message    
    for players in PlayerGenerator():
        i = index_from_playerinfo(players)
        m = messages.SayText2(index=i, chat=1, message=formatted_message)
        m.send(i)
    
def tell(player, myMessage=[]):
    myMessage = '\x04[D&D] \x01%s'%myMessage
    i = index_from_playerinfo(player)
    m = messages.SayText2(index=i, chat=1, message=myMessage)
    m.send(i)
    
def debug(myMessage=[]):
    print('\n[D&D Debug] %s\n'%myMessage)
    
        
def dndTick():
    for userid in PlayerIter('alive', return_types='userid'):
        myPlayer = dndPlayerDictionary[userid]
        for item in myPlayer.statusEffects:
            for instance in myPlayer.statusEffects[item]:
            
                if myPlayer.statusEffects[item][instance]['effect']:
                    if dndTimer.count >= myPlayer.statusEffects[item][instance]['duration'] and dndTimer.count % myPlayer.statusEffects[item][instance]['duration'] == 0:
                        
                        getattr(myPlayer, item)(instance)
                        if myPlayer.statusEffects[item][instance]['iteration'] != None:
                            if myPlayer.statusEffects[item][instance]['iteration'] > 0:
                                myPlayer.statusEffects[item][instance]['iteration'] -= 1
                            else:
                                myPlayer.statusEffects[item][instance].pop
                        
dndTimer = TickRepeat(dndTick)
dndTimer.start(1,0)
    
    # Drug brokez?
def drug(index):
    msg('Drug function')
    drugTimer = TickRepeat(changeAngle, index)
    drugTimer.start(1,4)
    
def changeAngle(index):
    msg('Drugging')
    myPlayer = PlayerEntity(index)
    myPlayer.eye_angle_x = float(random.randint(-180, 180))
    myPlayer.eye_angle_y = float(random.randint(-180, 180))
        
########################################################################
# CLASSES                                                              #
########################################################################

class _dndPlayerDictionary(dict):
    def __missing__(self, userid):
        value = self[userid] = dndPlayer(userid)
        return value
        
    def __delitem__(self, userid):
        if userid in self:
            super(_dndPlayerDictionary, self).__delitem__(userid)
            
dndPlayerDictionary = _dndPlayerDictionary()
            
class _PlayerDataDictionary(dict):
    def __missing__(self, steamid):
        value = self[steamid] = PlayerData()
        name = ''
        for players in PlayerGenerator():
            if PlayerEntity(index_from_playerinfo(players)).steamid == steamid:
                tell(players, 'Your class and race have been automatically reset to Human Fighter')
                name = PlayerEntity(index_from_playerinfo(players)).name
        msg('%s is new! Give them some help!'%name)
        return value

class PlayerData(dict):
    def __init__(self):
        self.kills = 0
        self.spree = 0
        self.gold = 0
        self.dndclass = 'Fighter'
        self.race = 'Human'
        self.la = 0
        self.prestige = 0
        self.points = 0
        self.ecl = 1
        self.Fighter = {
            'level' :1,
            'highest level':1,
            'xp'    :0
        }

    def __getattr__(self, attr):
        # Redirect to __getitem__
        # Can also use:
        #     return self[attr]
        try:
            return self[attr]
        except KeyError:
            raise AttributeError('Attribute "{0}" not found'.format(attr))

    def __setattr__(self, attr, value):
        # Redirect to __setitem__
        # Can also use:
        #     self[attr] = value
        self.__setitem__(attr, value)
    
class dndPlayer(PlayerEntity):

    def __new__(cls, userid):

        # Since PlayerEntity requires an index for instantiation, we need to get the index
        index = index_from_userid(userid)
        self = super(dndPlayer, cls).__new__(cls, index)
        return self
        
    def __init__(self, userid):
        PlayerDataDictionary[self.steamid]['last connected'] = int(time.clock())
        PlayerDataDictionary[self.steamid]['name'] = self.name
        PlayerDataDictionary[self.steamid]['spree'] = 0        
        self.maxhp = 100
        self.maxspeed = 1 # this is a fraction
        self.stealth = 255
        self.knifevisible = False 
        self.regen = []
        self.damageflat = 0 
        self.damagepercent = 0
        self.weaponlist = []
                
    def reset(self):
        self.maxhp = 100
        self.maxspeed = 1 # this is a fraction
        self.stealth = 255
        self.knifevisible = False 
        self.statusEffects = statusEffects
        self.damageflat = 0 
        self.damagepercent = 0
        self.get_input('IgniteLifetime', 0.0)
        self.weaponlist = []
        
    def regen(self, instance={}):
        self.heal(instance['effect'])
            
    def heal(self, amount):
        self.health += amount
        if self.health > self.maxhp:
            self.health = self.maxhp
            
    def stun(self, instance={}):
        raise NotImplementedError('Not yet included')
        
    def drug(self, instance={}):
        raise NotImplementedError('Not yet included')
        
    def freeze(self, instance={}):
        raise NotImplementedError('Not yet included')
        
    def slow(self, instance={}):
        raise NotImplementedError('Not yet included')

    def burn(self, instance={}):
        if instance['duration'] != None:
            self.get_input('IgniteLifetime')(float(instance['duration']))
        else:
            self.get_input('IgniteLifetime')(500.0)
        
    def addStealth(self, amount=0, duration=None):
        if amount:
            self.stealth += amount
        if self.stealth < 255:
            tell(self.playerinfo, 'You have gone into stealth')
        self.set_color(self.get_color().with_alpha(self.stealth))
        if duration:
            myTimer = TickRepeat(self.addStealth, -amount)
            myTimer.start(duration, 1)
            
    def removeStealth(self, amount=0, duration=None):
        if amount:
            self.stealth += amount
        self.set_color(self.get_color().with_alpha(255))
        if self.stealth < 255:
            tell(self.playerinfo, 'You have come out of stealth')
        if duration:
            myTimer = TickRepeat(self.addStealth, amount)
            myTimer.start(duration, 1)
        
    def changeMaxhp(self, amount, duration=None):
        self.maxhp += amount
        if duration:
            myTimer = TickRepeat(self.changeMaxhp, -amount)
            myTimer.start(duration, 1)
    
    def changeSpeed(self, amount, duration=None):
        self.speed += amount
        if duration:
            myTimer = TickRepeat(self.changeSpeed, -amount)
            myTimer.start(duration, 1)
        
    def addRegen(self, amount, time, duration=None):
        self.regen += amount
        self.regentime = time
        '''
        if duration:
            myTimer = TickRepeat(self.addRegen, -amount)
            myTimer.start(duration, 1)
        '''
        
    def addDamage(self, amount, duration=None):
        self.damageflat += amount
        if duration:
            myTimer = TickRepeat(self.addDamage, -amount)
            myTimer.start(duration, 1)
        
    def addDamagePercent(self, amount, duration=None):
        self.damagepercent += amount                        
        if duration:
            myTimer = TickRepeat(self.addDamagePercent, -amount)
            myTimer.start(duration, 1)
        
    def addKill(self, kills=1):
        PlayerDataDictionary[self.steamid].kills += kills
        
    def setKills(self, amount):
        PlayerDataDictionary[self.steamid].kills = amount
        
    def getKills(self):
        return PlayerDataDictionary[self.steamid].kills
        
    def getKillSpree(self):
        return PlayerDataDictionary[self.steamid]['spree']
        
    def addKillingSpree(self):
        PlayerDataDictionary[self.steamid]['spree'] += 1
       
    def changeRace(self, newRace):
        if not self.isdead:
            tell(self.playerinfo, 'You must be dead to change your race')
        else:
            if newRace not in races and newRace not in laraces:
                tell(self.playerinfo, '"%s" is not a valid race. The valid choices are: '%newRace)
                message = ''
                for x in races:
                    if x != races[0]:
                        message += ', "%s"'%x
                    else:
                        message += '"%s"'%x
                for x in laraces:
                    message += ', "%s"'%x                    
                tell(self.playerinfo, message)
            if newRace in races:
                debug('normal race')
                PlayerDataDictionary[self.steamid].race = newRace
                tell(self.playerinfo, 'You are now a %s'%newRace)
                if PlayerDataDictionary[self.steamid]['la'] > 0:
                    PlayerDataDictionary[self.steamid]['la'] = 0
                    PlayerDataDictionary[self.steamid]['ecl'] = self.getLevel()
            elif newRace in laraces:
                debug('La race')
                if (self.getLevel() > laraces[newRace]) and (self.getClass() not in prestiges):
                    PlayerDataDictionary[self.steamid]['race'] = newRace
                    PlayerDataDictionary[self.steamid]['la'] = laraces[newRace]
                    PlayerDataDictionary[self.steamid]['ecl'] = self.getLevel() - self.getLevelAdjustment()
                    tell(self.playerinfo, 'You are now a %s'%newRace)
                else:
                    tell(self.info, 'You are not a high-enough level %s for %s'%(self.getClass(), newRace))
                if self.getClass() in prestiges:
                    debug('prestiges')
                    prestigeLevel = 0
                    prestigeLevel = prestiges[self.getClass()][1]
                    if self.getLevel() - prestigeLevel < laraces[newRace]:
                        tell(self.playerinfo, 'You are not a high-enough level %s for %s'%(self.getClass(), newRace))                        
                    else:
                        PlayerDataDictionary[self.steamid]['race'] = newRace
                        PlayerDataDictionary[self.steamid]['la'] = laraces[newRace]
                        PlayerDataDictionary[self.steamid]['ecl'] = self.getLevel() - self.getLevelAdjustment()
                        tell(self.playerinfo, 'You are now a %s'%newRace)
            
    def changeClass(self, newClass):
        if self.isdead:
            if newClass in classes or prestiges:
                if newClass not in PlayerDataDictionary[self.steamid]:
                    PlayerDataDictionary[self.steamid][newClass] = {
                            'level' :1,
                            'highest level':1,
                            'xp'    :0
                        }
                    
                    if newClass in prestiges:
                        if self.getLevel(prestiges[newClass][0]) >= prestiges[newClass][1]:
                            if self.getLevel(newClass) == 1:
                                PlayerDataDictionary[self.steamid][newClass]['level'] = prestiges[newClass][1]
                            if self.getLevel(newClass) - prestiges[newClass][1] > self.getLevelAdjustment():
                                PlayerDataDictionary[self.steamid]['dndclass'] = newClass
                                tell(self.playerinfo, 'You are now a %s'%newClass)
                            else:
                                tell(self.playerinfo, 'Your level-adjustment is too great for %s'%newClass)
                        else:
                            tell(self.playerinfo, 'You must have a level %s %s to play a %s'%(prestiges[newClass][1], prestiges[newClass][0], newClass))
                if newClass in classes:
                    if self.getLevelAdjustment() < self.getLevel(newClass):
                        PlayerDataDictionary[self.steamid]['dndclass'] = newClass              
                        tell(self.playerinfo, 'You are now a %s'%newClass)
                    else:
                       tell(self.playerinfo, 'Your level-adjustment is too great for %s'%newClass)
            else:
                tell(self.playerinfo, '"%s" is not a valid class. The valid choices are: '%newClass)
                message = ''
                for x in classes:
                    if x != classes[0]:
                        message += ', "%s"'%x
                    else:
                        message += '"%s"'%x
                for x in prestiges:
                    message += ', "%s"'%x
                tell(self.playerinfo, message)
        else:
            tell(self.playerinfo, 'You can only change classes while dead!')
        
        
        
    
    def getRace(self):
        return PlayerDataDictionary[self.steamid].race
    
    def getClass(self):
        return PlayerDataDictionary[self.steamid]['dndclass']
        
    def getLevel(self, dndclass=None):
        if not dndclass:
            return PlayerDataDictionary[self.steamid][self.getClass()]['level']
        else:
            if dndclass not in PlayerDataDictionary[self.steamid]:
                PlayerDataDictionary[self.steamid][dndclass] = {
                                'level' :1,
                                'highest level':1,
                                'xp'    :0
                            }
            return PlayerDataDictionary[self.steamid][dndclass]['level']            
                
    def getECL(self):
        PlayerDataDictionary[self.steamid]['ecl'] = self.getLevel() - self.getLevelAdjustment()
        return PlayerDataDictionary[self.steamid]['ecl']
                
    def getLevelAdjustment(self):
        return PlayerDataDictionary[self.steamid]['la']
        
    def getXp(self):
        if PlayerDataDictionary[self.steamid][self.getClass()]['xp'] < 0:
            PlayerDataDictionary[self.steamid][self.getClass()]['xp']= 0
        return PlayerDataDictionary[self.steamid][self.getClass()]['xp']       
        
    def giveLevel(self, levels):
        PlayerDataDictionary[self.steamid][self.getClass()]['level'] += levels
        if PlayerDataDictionary[self.steamid][self.getClass()]['highest level'] < self.getECL():
            PlayerDataDictionary[self.steamid][self.getClass()]['highest level'] = self.getECL()
        msg('Congratulations, %s, for leveling up! %s is now Level %s!'%(self.name, self.name, self.getECL()))
        
    def giveXp(self, amount, reason=None):
        count = 0
        for players in PlayerGenerator():
            if players.get_team_index() > 1:
                count += 1
        if count > 1:
            PlayerDataDictionary[self.steamid][self.getClass()]['xp'] += amount
            if PlayerDataDictionary[self.steamid][self.getClass()]['xp'] < 0:
                PlayerDataDictionary[self.steamid][self.getClass()]['xp'] = 0
            if reason:
                
                tell(self.playerinfo, 'You have gained %s xp %s'%(amount, reason))
            else:
                tell(self.playerinfo, 'You have gained %s xp'%amount)
            if self.getECL() < 20:
                if self.getXp() / self.getECL() >= 1000:
                    PlayerDataDictionary[self.steamid][self.getClass()]['xp'] -= self.getECL() * 1000
                    self.giveLevel(1)
        else:
            tell(self.playerinfo, 'Not enough players for XP')                    
            
PlayerDataDictionary = _PlayerDataDictionary()
str_path = GAME_PATH + '/addons/source-python/plugins/dnd/player_database.db'
if os.path.isfile(str_path):
    if not os.stat(str_path).st_size == 0:
        PlayerDataDictionary = pickle.load(open(str_path, 'rb'))
    

########################################################################
# MENUS                                                                #
########################################################################

# Create a new menu
mainMenu = SimpleMenu()

# Add a simple line
mainMenu.append(Text('[D&D] Main Menu'))

# Add two answer options. The first argument is the text that is displayed
# in the menu. The second argument is a value that you can access later in
# your select callback
mainMenu.append(Option('Race', 'race'))
mainMenu.append(Option('Class', 'class'))
mainMenu.append(Option('Prestige', 'prestige'))
mainMenu.append(Option('Info', 'info'))
mainMenu.append(Option('Class Weapon List', 'weapons'))
mainMenu.append(Option('My Stats', 'stats'))
mainMenu.append(Option('Player Info', 'playerinfo'))
mainMenu.append(Option('Exit', 'exit'))

# Define the select callback
mainMenu.select_callback = mainMenuCallBack

raceMenu = SimpleMenu()   #Make sure to do LA races here
# Add a simple line
raceMenu.append(Text('[D&D] Main Menu'))
# Add two answer options. The first argument is the text that is displayed
# in the menu. The second argument is a value that you can access later in
# your select callback
for race in races:
    raceMenu.append(Option(race,race))
raceMenu.append(Option('Exit', 'exit'))
# Define the select callback
raceMenu.select_callback = raceMenuCallBack

classMenu = SimpleMenu()
# Add a simple line
classMenu.append(Text('[D&D] Main Menu'))
# Add two answer options. The first argument is the text that is displayed
# in the menu. The second argument is a value that you can access later in
# your select callback
for myClass in classes:
    classMenu.append(Option(myClass,myClass))
classMenu.append(Option('Exit', 'exit'))
# Define the select callback
classMenu.select_callback = classMenuCallBack

mainInfoMenu = SimpleMenu()
mainInfoMenu.append(Text('[D&D] Info Menus'))
mainInfoMenu.append(Option('Races', 'races'))
mainInfoMenu.append(Option('Classes', 'classes'))
mainInfoMenu.append(Option('Commands','commands'))
mainInfoMenu.append(Option('Exit','exit'))
mainInfoMenu.select_callback = mainInfoMenuCallBack

raceInfoMenu = SimpleMenu()
raceInfoMenu.append(Text('[D&D] Info Menus'))
raceInfoMenu.append(Option('Base Races','baseraces'))
raceInfoMenu.append(Option('LA Races','laraces'))
raceInfoMenu.append(Option('Exit','exit'))
raceInfoMenu.select_callback = raceInfoMenuCallBack

baseRaceInfoMenu = SimpleMenu()
baseRaceInfoMenu.append(Text('[D&D} Select a race to see information about it:'))
for race in races:
    baseRaceInfoMenu.append(Option(race,race))
baseRaceInfoMenu.append(Option('Exit','exit'))
baseRaceInfoMenu.select_callback = baseRaceInfoMenuCallBack

laRaceInfoMenu = SimpleMenu()
laRaceInfoMenu.append(Text('[D&D] Select a race to see information about it:'))
for race in laracesList:
    laRaceInfoMenu.append(Option(race,race))
laRaceInfoMenu.append(Option('Exit','exit'))
laRaceInfoMenu.select_callback = laRaceInfoMenuCallBack

classInfoMenu = SimpleMenu()
classInfoMenu.append(Text('[D&D] InfoMenus'))
classInfoMenu.append(Option('Base Classes','classes'))
classInfoMenu.append(Option('Prestige Classes','prestiges'))
classInfoMenu.append(Option('Exit','exit'))
classInfoMenu.select_callback = classInfoMenuCallBack

baseClassInfoMenu = SimpleMenu()
baseClassInfoMenu.append(Text('[D&D] InfoMenus'))
for myClass in classes:
    baseClassInfoMenu.append(Option(myClass,myClass))
baseClassInfoMenu.append(Option('Exit','exit'))
baseClassInfoMenu.select_callback = baseClassInfoMenuCallBack

prestigeClassInfoMenu = SimpleMenu()
prestigeClassInfoMenu.append(Text('[D&D] InfoMenus'))
for prestige in prestiges:
    prestigeClassInfoMenu.append(Option(prestige,prestige))
prestigeClassInfoMenu.append(Option('Exit','exit'))
prestigeClassInfoMenu.select_callback = prestigeClassInfoMenuCallBack

commandInfoMenu = SimpleMenu()
commandInfoMenu.append(Text('[D&D] Commands'))
commandInfoMenu.append(Text('!menu\n\tLoads Main Menu\n!skills\n\tSee class skills\n!spells\n\tSee class spells'))
commandInfoMenu.append(Option('Exit','exit'))