# -*- coding: utf-8 -*-

# ################################################################### #
#                                                                     #
#  BigBrotherBot(B3) (www.bigbrotherbot.net)                          #
#  Copyright (C) 2005 Michael "ThorN" Thornton                        #
#                                                                     #
#  This program is free software; you can redistribute it and/or      #
#  modify it under the terms of the GNU General Public License        #
#  as published by the Free Software Foundation; either version 2     #
#  of the License, or (at your option) any later version.             #
#                                                                     #
#  This program is distributed in the hope that it will be useful,    #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of     #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the       #
#  GNU General Public License for more details.                       #
#                                                                     #
#  You should have received a copy of the GNU General Public License  #
#  along with this program; if not, write to the Free Software        #
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA      #
#  02110-1301, USA.                                                   #
#                                                                     #
# ################################################################### #

__author__ = 'Bakes, Courgette'
__version__ = '1.9'

import time
import b3.clients
import b3.events
import b3.functions

from b3.parsers.frostbite.abstractParser import AbstractParser
from b3.parsers.frostbite.util import PlayerInfoBlock

SAY_LINE_MAX_LENGTH = 100

class MohParser(AbstractParser):

    gameName = 'moh'
    
    _gameServerVars = (
        'serverName', # vars.serverName [name] Set the server name 
        'gamePassword', # vars.gamePassword [password] Set the game password for the server 
        'punkBuster', # vars.punkBuster [enabled] Set if the server will use PunkBuster or not 
        'hardCore', # vars.hardCore[enabled] Set hardcore mode 
        'ranked', # vars.ranked [enabled] Set ranked or not 
        'skillLimit', # vars.skillLimit [lower, upper] Set the skill limits allowed on to the server 
        'noUnlocks', # vars.noUnlocks [enabled] Set if unlocks should be disabled 
        'noAmmoPickups', # vars.noAmmoPickups [enabled] Set if pickups should be disabled 
        'realisticHealth', # vars.realisticHealth [enabled] Set if health should be realistic 
        'supportAction', # vars.supportAction [enabled] Set if support action should be enabled 
        'preRoundLimit', # vars.preRoundLimit [upper, lower] Set pre round limits.
        'roundStartTimerPlayersLimit', # vars.roundStartTimerPlayersLimit [limit]
        'roundStartTimerDelay', # vars.roundStartTimerDelay [delay] If set to other than -1, this value overrides
                                # the round start delay set on the individual levels.
        'tdmScoreCounterMaxScore', # vars.tdmScoreCounterMaxScore [score] If set to other than -1, this value overrides
                                  # the score needed to win a round of Team Assault, Sector Control or Hot Zone.
        'clanTeams', # vars.clanTeams [enabled] Set if clan teams should be used 
        'friendlyFire', # vars.friendlyFire [enabled] Set if the server should allow team damage 
        'currentPlayerLimit', # vars.currentPlayerLimit Retrieve the current maximum number of players 
        'maxPlayerLimit', # vars.maxPlayerLimit Retrieve the server-enforced maximum number of players 
        'playerLimit', # vars.playerLimit [nr of players] Set desired maximum number of players 
        'bannerUrl', # vars.bannerUrl [url] Set banner url 
        'serverDescription', # vars.serverDescription [description] Set server description 
        'noCrosshairs', # vars.noCrosshairs [enabled] Set if crosshairs for all weapons is hidden
        'noSpotting', # vars.noSpotting [enabled] Set if spotted targets are disabled in the 3d-world 
        'teamKillCountForKick', # vars.teamKillCountForKick [count] Set number of teamkills allowed during a round 
        'teamKillValueForKick', # vars.teamKillValueForKick [count] Set max kill-value allowed for a player before
                                # he/she is kicked
        'teamKillValueIncrease', # vars.teamKillValueIncrease [count] Set kill-value increase for a teamkill 
        'teamKillValueDecreasePerSecond', # vars.teamKillValueDecreasePerSecond [count] Set kill-value decrease per second
        'idleTimeout', # vars.idleTimeout [time] Set idle timeout vars.profanityFilter [enabled] Set if profanity
                       # filter is enabled
    )
    
    ####################################################################################################################
    #                                                                                                                  #
    #   PARSER INITIALIZATION                                                                                          #
    #                                                                                                                  #
    ####################################################################################################################

    def startup(self):
        """
        Called after the parser is created before run().
        """
        AbstractParser.startup(self)
        self.clients.newClient('Server', guid='Server', name='Server', hide=True, pbid='Server', team=b3.TEAM_UNKNOWN)

    def pluginsStarted(self):
        """
        Called after the parser loaded and started all plugins.
        Overwrite this in parsers to take actions once plugins are ready
        """
        self.info('Connecting all players...')
        plist = self.getPlayerList()
        for cid, p in plist.items():
            client = self.clients.getByCID(cid)
            if not client:
                name = p['name']
                if 'clanTag' in p and len(p['clanTag']) > 0:
                    name = "[" + p['clanTag'] + "] " + p['name']
                self.debug('Client %s found on the server' % cid)
                client = self.clients.newClient(cid, guid=p['guid'], name=name, team=p['teamId'], data=p)
                self.queueEvent(self.getEvent('EVT_CLIENT_JOIN', p, client))

    ####################################################################################################################
    #                                                                                                                  #
    #   OTHER METHODS                                                                                                  #
    #                                                                                                                  #
    ####################################################################################################################

    def checkVersion(self):
        version = self.output.write('version')
        self.info('server version: %s' % version)
        if version[0] != 'MOH':
            raise Exception("the moh parser can only work with Medal of Honor")

    def getClient(self, cid, _guid=None):
        """
        Get a connected client from storage or create it
        B3 CID   <--> MoH character name
        B3 GUID  <--> MoH EA_guid
        """
        # try to get the client from the storage of already authed clients
        client = self.clients.getByCID(cid)
        if not client:
            if cid == 'Server':
                return self.clients.newClient('Server', guid='Server', name='Server',
                                              hide=True, pbid='Server', team=b3.TEAM_UNKNOWN)
            # must be the first time we see this client
            words = self.write(('admin.listPlayers', 'player', cid))
            pib = PlayerInfoBlock(words)
            if len(pib) == 0:
                self.debug('No such client found')
                return None
            p = pib[0]
            cid = p['name']
            name = p['name']

            # Let's see if we have a guid, either from the PlayerInfoBlock,
            # or passed to us by OnPlayerAuthenticated()
            if p['guid']:
                guid = p['guid']
            elif _guid:
                guid = _guid
            else:
                # If we still don't have a guid, we cannot create a newclient without the guid!
                self.debug('No guid for %s: waiting for next event' %name)
                return None

            if 'clanTag' in p and len(p['clanTag']) > 0:
                name = "[" + p['clanTag'] + "] " + p['name']

            client = self.clients.newClient(cid, guid=guid, name=name,
                                            team=self.getTeam(p['teamId']),
                                            teamId=int(p['teamId']), data=p)

            self.queueEvent(self.getEvent('EVT_CLIENT_JOIN', p, client))
        
        return client

    def getHardName(self, mapname):
        """
        Change real name to level name.
        """
        mapname = mapname.lower()
        if mapname.startswith('mazar-i-sharif airfield'):
            return 'levels/mp_01'
        elif mapname.startswith('bagram hanger'):
            return 'levels/mp_01_elimination'
        elif mapname.startswith('shah-i-knot mountains'):
            return 'levels/mp_02'
        elif mapname.startswith('hindu kush pass'):
            return 'levels/mp_02_koth'
        elif mapname.startswith('khyber caves'):
            return 'levels/mp_03'
            #return 'levels/mp_03_elimination'
        elif mapname.startswith('helmand valley'):
            return 'levels/mp_04'
        elif mapname.startswith('helmand river hill'):
            return 'levels/mp_04_koth'
        elif mapname.startswith('kandahar marketplace'):
            return 'levels/mp_05'
        elif mapname.startswith('diwagal camp'):
            return 'levels/mp_06'
            #return 'mp_06_elimination'
        elif mapname.startswith('korengal outpost'):
            return 'levels/mp_07_koth'
        elif mapname.startswith('kunar base'):
            return 'levels/mp_08'
        elif mapname.startswith('kabul city ruins'):
            return 'levels/mp_09'
            #return 'levels/mp_09_elimination'
        elif mapname.startswith('garmzir town'):
            return 'levels/mp_10'
        else:
            self.warning('unknown level name : \'%s\' : please make sure you have entered a valid mapname' % mapname)
            return mapname

    def getEasyName(self, mapname):
        """
        Change levelname to real name.
        """
        if mapname.startswith('levels/mp_01_elimination'):
            return 'Bagram Hanger'
        elif mapname.startswith('levels/mp_01'):
            return 'Mazar-i-Sharif Airfield'
        elif mapname.startswith('levels/mp_02_koth'):
            return 'Hindu Kush Pass'
        elif mapname.startswith('levels/mp_02'):
            return 'Shah-i-Knot Mountains'
        elif mapname.startswith('levels/mp_03'):
            return 'Khyber Caves'
        elif mapname.startswith('levels/mp_04_koth'):
            return 'Helmand River Hill'
        elif mapname.startswith('levels/mp_04'):
            return 'Helmand Valley'
        elif mapname.startswith('levels/mp_05'):
            return 'Kandahar Marketplace'
        elif mapname.startswith('levels/mp_06'):
            return 'Diwagal Camp'
        elif mapname.startswith('levels/mp_07_koth'):
            return 'Korengal Outpost'
        elif mapname.startswith('levels/mp_08'):
            return 'Kunar Base'
        elif mapname.startswith('levels/mp_09'):
            return 'Kabul City Ruins'
        elif mapname.startswith('levels/mp_10'):
            return 'Garmzir Town'
        else:
            self.warning('unknown level name : \'%s\' : please report this on B3 forums' % mapname)
            return mapname

    def getServerVars(self):
        """
        Update the game property from server fresh data.
        """
        try:
            self.game.serverName = self.getCvar('serverName').getBoolean()
        except:
            pass
        try:
            self.game.gamePassword = self.getCvar('gamePassword').getBoolean()
        except:
            pass
        try:
            self.game.punkBuster = self.getCvar('punkBuster').getBoolean()
        except:
            pass
        try:
            self.game.hardCore = self.getCvar('hardCore').getBoolean()
        except:
            pass
        try:
            self.game.ranked = self.getCvar('ranked').getBoolean()
        except:
            pass
        try:
            self.game.skillLimit = self.getCvar('skillLimit').getBoolean()
        except:
            pass
        try:
            self.game.noUnlocks = self.getCvar('noUnlocks').getBoolean()
        except:
            pass
        try:
            self.game.noAmmoPickups = self.getCvar('noAmmoPickups').getBoolean()
        except:
            pass
        try:
            self.game.realisticHealth = self.getCvar('realisticHealth').getBoolean()
        except:
            pass
        try:
            self.game.supportAction = self.getCvar('supportAction').getBoolean()
        except:
            pass
        try:
            self.game.preRoundLimit = self.getCvar('preRoundLimit').getBoolean()
        except:
            pass
        try:
            self.game.roundStartTimerPlayersLimit = self.getCvar('roundStartTimerPlayersLimit').getBoolean()
        except:
            pass
        try:
            self.game.roundStartTimerDelay = self.getCvar('roundStartTimerDelay').getBoolean()
        except:
            pass
        try:
            self.game.tdmScoreCounterMaxScore = self.getCvar('tdmScoreCounterMaxScore').getBoolean()
        except:
            pass
        try:
            self.game.clanTeams = self.getCvar('clanTeams').getBoolean()
        except:
            pass
        try:
            self.game.friendlyFire = self.getCvar('friendlyFire').getBoolean()
        except:
            pass
        try:
            self.game.currentPlayerLimit = self.getCvar('currentPlayerLimit').getBoolean()
        except:
            pass
        try:
            self.game.maxPlayerLimit = self.getCvar('maxPlayerLimit').getBoolean()
        except:
            pass
        try:
            self.game.playerLimit = self.getCvar('playerLimit').getBoolean()
        except:
            pass
        try:
            self.game.bannerUrl = self.getCvar('bannerUrl').getBoolean()
        except:
            pass
        try:
            self.game.serverDescription = self.getCvar('serverDescription').getBoolean()
        except:
            pass
        try:
            self.game.noCrosshair = self.getCvar('noCrosshair').getBoolean()
        except:
            pass
        try:
            self.game.noSpotting = self.getCvar('noSpotting').getBoolean()
        except:
            pass
        try:
            self.game.teamKillCountForKick = self.getCvar('teamKillCountForKick').getBoolean()
        except:
            pass
        try:
            self.game.teamKillValueForKick = self.getCvar('teamKillValueForKick').getBoolean()
        except:
            pass
        try:
            self.game.teamKillValueIncrease = self.getCvar('teamKillValueIncrease').getBoolean()
        except:
            pass
        try:
            self.game.teamKillValueDecreasePerSecond = self.getCvar('teamKillValueDecreasePerSecond').getBoolean()
        except:
            pass
        try:
            self.game.idleTimeout = self.getCvar('idleTimeout').getBoolean()
        except:
            pass

    def getTeam(self, team):
        """
        Convert MOH team numbers to B3 team numbers.
        """
        team = int(team)
        if team == 1:
            return b3.TEAM_RED
        elif team == 2:
            return b3.TEAM_BLUE
        elif team == 3:
            return b3.TEAM_SPEC
        else:
            return b3.TEAM_UNKNOWN

    ####################################################################################################################
    #                                                                                                                  #
    #   EVENT HANDLERS                                                                                                 #
    #                                                                                                                  #
    ####################################################################################################################

    def OnPlayerSpawn(self, action, data):
        """
        player.onSpawn <soldier name: string> <kit: string> <weapon: string> <specializations: 3 x string>
        """
        if len(data) < 2:
            return None

        spawner = self.getClient(data[0])
        kit = data[1]
        weapon = data[2]
        spec1 = data[3]
        spec2 = data[4]
        spec3 = data[5]

        return self.getEvent('EVT_CLIENT_SPAWN', (kit, weapon, spec1, spec2, spec3), spawner)

    def OnPlayerTeamchange(self, action, data):
        """
        player.onTeamChange <soldier name: player name> <team: Team ID>
        Effect: Player might have changed team
        """
        #['player.onTeamChange', 'Dalich', '2']
        client = self.getClient(data[0])
        if client:
            client.team = self.getTeam(data[1]) # .team setter will send team change event
            client.teamId = int(data[1])

    ####################################################################################################################
    #                                                                                                                  #
    #   B3 PARSER INTERFACE IMPLEMENTATION                                                                             #
    #                                                                                                                  #
    ####################################################################################################################

    def tempban(self, client, reason='', duration=2, admin=None, silent=False, *kwargs):
        """
        Tempban a client.
        :param client: The client to tempban
        :param reason: The reason for this tempban
        :param duration: The duration of the tempban
        :param admin: The admin who performed the tempban
        :param silent: Whether or not to announce this tempban
        """
        duration = b3.functions.time2minutes(duration)
        if isinstance(client, str):
            self.write(self.getCommand('kick', cid=client, reason=reason[:80]))
            return
        elif admin:
            banduration = b3.functions.minutesStr(duration)
            variables = self.getMessageVariables(client=client, reason=reason, admin=admin, banduration=banduration)
            fullreason = self.getMessage('temp_banned_by', variables)
        else:
            banduration = b3.functions.minutesStr(duration)
            variables = self.getMessageVariables(client=client, reason=reason, banduration=banduration)
            fullreason = self.getMessage('temp_banned', variables)

        fullreason = self.stripColors(fullreason)
        reason = self.stripColors(reason)

        if self.PunkBuster:
            # punkbuster acts odd if you ban for more than a day
            # tempban for a day here and let b3 re-ban if the player
            # comes back
            if duration > 1440:
                duration = 1440
            self.PunkBuster.kick(client, duration, reason)

        self.write(('banList.list',))
        self.write(self.getCommand('tempban', guid=client.guid, duration=duration*60, reason=reason[:80]))
        self.write(('banList.list',))
        ## also kick as the MoH server seems not to enforce all bans correctly
        self.write(self.getCommand('kick', cid=client.cid, reason=reason[:80]))
        
        if not silent and fullreason != '':
            self.say(fullreason)

        self.queueEvent(self.getEvent('EVT_CLIENT_BAN_TEMP', {'reason': reason,
                                                              'duration': duration, 
                                                              'admin': admin} , client))

    def ban(self, client, reason='', admin=None, silent=False, *kwargs):
        """
        Ban a given client.
        :param client: The client to ban
        :param reason: The reason for this ban
        :param admin: The admin who performed the ban
        :param silent: Whether or not to announce this ban
        """
        self.debug('BAN : client: %s, reason: %s', client, reason)
        if isinstance(client, b3.clients.Client):
            self.write(self.getCommand('ban', guid=client.guid, reason=reason[:80]))
            try:
                self.write(self.getCommand('kick', cid=client.cid, reason=reason[:80]))
            except:
                pass
            return

        if admin:
            variables = self.getMessageVariables(client=client, reason=reason, admin=admin)
            reason = self.getMessage('banned_by', variables)
        else:
            variables = self.getMessageVariables(client=client, reason=reason)
            reason = self.getMessage('banned', variables)

        reason = self.stripColors(reason)

        if client.cid is None:
            # ban by ip, this happens when we !permban @xx a player that is not connected
            self.debug('EFFECTIVE BAN : %s', self.getCommand('banByIp', ip=client.ip, reason=reason[:80]))
            self.write(self.getCommand('banByIp', ip=client.ip, reason=reason[:80]))
            if admin:
                admin.message('Banned: %s (@%s). '
                              'His last ip (%s) has been added to banlist' % (client.exactName, client.id, client.ip))
        else:
            # ban by cid
            self.debug('EFFECTIVE BAN : %s',self.getCommand('ban', guid=client.guid, reason=reason[:80]))
            self.write(('banList.list',))
            self.write(self.getCommand('ban', cid=client.cid, reason=reason[:80]))
            self.write(('banList.list',))
            self.write(self.getCommand('kick', cid=client.cid, reason=reason[:80]))
            if admin:
                admin.message('Banned: %s (@%s) has been added to banlist' % (client.exactName, client.id))

        if self.PunkBuster:
            self.PunkBuster.banGUID(client, reason)
        
        if not silent:
            self.say(reason)
        
        self.queueEvent(self.getEvent('EVT_CLIENT_BAN', {'reason': reason, 'admin': admin}, client))


    def rotateMap(self):
        """
        Load the next map (not level). If the current game mod plays each level twice
        to get teams the chance to play both sides, then this rotate a second
        time to really switch to the next map.
        """
        nextIndex = self.getNextMapIndex()
        if nextIndex == -1:
            # No map in map rotation list, just call admin.runNextLevel
            self.write(('admin.runNextRound',))
        else:
            self.write(('mapList.nextLevelIndex', nextIndex))
            self.write(('admin.runNextRound',))

    def changeMap(self, mapname):
        """
        Change to the given map
        
        1) determine the level name
            If map is of the form 'mp_001' and 'Kaboul' is a supported
            level for the current game mod, then this level is loaded.
            
            In other cases, this method assumes it is given a 'easy map name' (like
            'Port Valdez') and it will do its best to find the level name that seems
            to be for 'Port Valdez' within the supported levels.
        
            If no match is found, then instead of loading the map, this method 
            returns a list of candidate map names
            
        2) if we got a level name
            if the level is not in the current rotation list, then add it to 
            the map list and load it
        """
        supportedMaps = self.getSupportedMaps()
        if 'levels/%s' % mapname in supportedMaps:
            mapname = 'levels/%s' % mapname

        if mapname not in supportedMaps:
            match = self.getMapsSoundingLike(mapname)
            if len(match) == 1:
                mapname = match[0]
            else:
                return match

        if mapname in supportedMaps:
            levelnames = self.write(('mapList.list',))
            if mapname not in levelnames:
                # add the map to the map list
                nextIndex = self.getNextMapIndex()
                if nextIndex == -1:
                    self.write(('mapList.append', mapname))
                    nextIndex = 0
                else:
                    if nextIndex == 0:
                        # case where the map list contains only 1 map
                        nextIndex = 1
                    self.write(('mapList.insert', nextIndex, mapname))
            else:
                nextIndex = 0
                while nextIndex < len(levelnames) and levelnames[nextIndex] != mapname:
                    nextIndex += 1
            
            self.say('Changing map to %s' % mapname)
            time.sleep(1)
            self.write(('mapList.nextLevelIndex', nextIndex))
            self.write(('admin.runNextRound', ))

    def saybig(self, msg):
        """
        Broadcast a message to all players.
        :param msg: The message to be broadcasted
        """
        self.say(msg)