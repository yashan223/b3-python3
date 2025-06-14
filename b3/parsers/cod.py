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

__author__ = 'ThorN, xlr8or'
__version__ = '1.5.3'


import b3
import b3.events
import b3.parsers.punkbuster
import re
import string

from b3.parsers.q3a.abstractParser import AbstractParser
from threading import Timer

class CodParser(AbstractParser):

    gameName = 'cod'
    PunkBuster = None
    IpsOnly = False

    _guidLength = 6                                          # (minimum) length of the guid
    _reMap = re.compile(r'map ([a-z0-9_-]+)', re.IGNORECASE) # to extract map names
    _pbRegExp = re.compile(r'^[0-9a-f]{32}$', re.IGNORECASE) # RegExp to match a PunkBuster ID
    _logSync = 3                                             # Value for unbuffered game logging (append mode)
    _counter = {}

    _line_length = 65
    _line_color_prefix = ''

    _commands = {
        'message': 'tell %(cid)s %(message)s',
        'say': 'say %(message)s',
        'set': 'set %(name)s "%(value)s"',
        'kick': 'clientkick %(cid)s',
        'ban': 'banclient %(cid)s',
        'unban': 'unbanuser %(name)s',
        'tempban': 'clientkick %(cid)s'
    }

    _eventMap = {
        #'warmup': b3.events.EVT_GAME_WARMUP,
        #'restartgame': b3.events.EVT_GAME_ROUND_END
    }

    # remove the time off of the line
    _lineClear = re.compile(r'^(?:[0-9:]+\s?)?')

    _lineFormats = (
        # server events
        re.compile(r'^(?P<action>[a-z]+):\s?(?P<data>.*)$', re.IGNORECASE),

        # world kills
        re.compile(r'^(?P<action>[A-Z]);'
                   r'(?P<data>'
                   r'(?P<guid>[^;]+);'
                   r'(?P<cid>[0-9-]{1,2});'
                   r'(?P<team>[a-z]+);'
                   r'(?P<name>[^;]+);'
                   r'(?P<aguid>[^;]*);'
                   r'(?P<acid>-1);'
                   r'(?P<ateam>world);'
                   r'(?P<aname>[^;]*);'
                   r'(?P<aweap>[a-z0-9_-]+);'
                   r'(?P<damage>[0-9.]+);'
                   r'(?P<dtype>[A-Z_]+);'
                   r'(?P<dlocation>[a-z_]+))$', re.IGNORECASE),

        # player kills/damage
        re.compile(r'^(?P<action>[A-Z]);'
                   r'(?P<data>'
                   r'(?P<guid>[^;]+);'
                   r'(?P<cid>[0-9]{1,2});'
                   r'(?P<team>[a-z]*);'
                   r'(?P<name>[^;]+);'
                   r'(?P<aguid>[^;]+);'
                   r'(?P<acid>[0-9]{1,2});'
                   r'(?P<ateam>[a-z]*);'
                   r'(?P<aname>[^;]+);'
                   r'(?P<aweap>[a-z0-9_-]+);'
                   r'(?P<damage>[0-9.]+);'
                   r'(?P<dtype>[A-Z_]+);'
                   r'(?P<dlocation>[a-z_]+))$', re.IGNORECASE),

        # suicides (cod4/cod5)
        re.compile(r'^(?P<action>[A-Z]);'
                   r'(?P<data>'
                   r'(?P<guid>[^;]+);'
                   r'(?P<cid>[0-9]{1,2});'
                   r'(?P<team>[a-z]*);'
                   r'(?P<name>[^;]+);'
                   r'(?P<aguid>[^;]*);'
                   r'(?P<acid>-1);'
                   r'(?P<ateam>[a-z]*);'
                   r'(?P<aname>[^;]+);'
                   r'(?P<aweap>[a-z0-9_-]+);'
                   r'(?P<damage>[0-9.]+);'
                   r'(?P<dtype>[A-Z_]+);'
                   r'(?P<dlocation>[a-z_]+))$', re.IGNORECASE),

        # suicides (cod7)
        re.compile(r'^(?P<action>[A-Z]);'
                   r'(?P<data>'
                   r'(?P<guid>[^;]+);'
                   r'(?P<cid>[0-9]{1,2});'
                   r'(?P<team>[a-z]*);'
                   r'(?P<name>[^;]+);'
                   r'(?P<aguid>[^;]*);'
                   r'(?P<acid>[0-9]{1,2});'
                   r'(?P<ateam>[a-z]*);'
                   r'(?P<aname>[^;]+);'
                   r'(?P<aweap>[a-z0-9_-]+);'
                   r'(?P<damage>[0-9.]+);'
                   r'(?P<dtype>[A-Z_]+);'
                   r'(?P<dlocation>[a-z_]+))$', re.IGNORECASE),

        # for this one they appear to have swapped the attacker team and name in the
        # output, hence the specific entry for attacker name as it is a unique case
        re.compile(r'^(?P<action>[A-Z]);'
                   r'(?P<data>'
                   r'(?P<guid>[^;]+);'
                   r'(?P<cid>[0-9]{1,2});'
                   r'(?P<team>[a-z]*);'
                   r'(?P<name>[^;]+);'
                   r'(?P<aguid>[^;]*);'
                   r'(?P<acid>[0-9]{1,2});'
                   r'(?P<aname>world);'
                   r'(?P<ateam>[a-z]*);'
                   r'(?P<aweap>none);'
                   r'(?P<damage>[0-9.]+);'
                   r'(?P<dtype>[A-Z_]+);'
                   r'(?P<dlocation>[a-z_]+))$', re.IGNORECASE),

        # team actions
        re.compile(r'^(?P<action>[A-Z]);'
                   r'(?P<data>'
                   r'(?P<guid>[^;]+);'
                   r'(?P<cid>[0-9]{1,2});'
                   r'(?P<team>[a-z]+);'
                   r'(?P<name>[^;]+);'
                   r'(?P<type>[a-z_]+))$', re.IGNORECASE),

        # Join Team (cod5)
        re.compile(r'^(?P<action>JT);'
                   r'(?P<data>'
                   r'(?P<guid>[^;]+);'
                   r'(?P<cid>[0-9]{1,2});'
                   r'(?P<team>[a-z]+);'
                   r'(?P<name>[^;]+);)$', re.IGNORECASE),

        # tell like events
        re.compile(r'^(?P<action>[a-z]+);'
                   r'(?P<data>'
                   r'(?P<guid>[^;]+);'
                   r'(?P<cid>[0-9]{1,2});'
                   r'(?P<name>[^;]+);'
                   r'(?P<aguid>[^;]+);'
                   r'(?P<acid>[0-9]{1,2});'
                   r'(?P<aname>[^;]+);'
                   r'(?P<text>.*))$', re.IGNORECASE),

        # say like events
        re.compile(r'^(?P<action>[a-z]+);'
                   r'(?P<data>'
                   r'(?P<guid>[^;]+);'
                   r'(?P<cid>[0-9]{1,2});'
                   r'(?P<name>[^;]+);'
                   r'(?P<text>.*))$', re.IGNORECASE),

        # all other events
        re.compile(r'^(?P<action>[A-Z]);'
                   r'(?P<data>'
                   r'(?P<guid>[^;]+);'
                   r'(?P<cid>[0-9]{1,2});'
                   r'(?P<name>[^;]+))$', re.IGNORECASE)
    )

    # num score ping guid   name            lastmsg address               qport rate
    # --- ----- ---- ------ --------------- ------- --------------------- ----- -----
    # 2       0   29 465030 ThorN                50 68.63.6.62:-32085      6597  5000
    _regPlayer = re.compile(r'^\s*(?P<slot>[0-9]+)\s+'
                            r'(?P<score>[0-9-]+)\s+'
                            r'(?P<ping>[0-9]+)\s+'
                            r'(?P<guid>[0-9]+)\s+'
                            r'(?P<name>.*?)\s+'
                            r'(?P<last>[0-9]+?)\s*'
                            r'(?P<ip>(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}'
                            r'(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])):?'
                            r'(?P<port>-?[0-9]{1,5})\s*'
                            r'(?P<qport>-?[0-9]{1,5})\s+'
                            r'(?P<rate>[0-9]+)$', re.IGNORECASE | re.VERBOSE)

    ####################################################################################################################
    #                                                                                                                  #
    #   PARSER INITIALIZATION                                                                                          #
    #                                                                                                                  #
    ####################################################################################################################

    def startup(self):
        """
        Called after the parser is created before run().
        """
        if not self.config.has_option('server','game_log'):
            self.critical("Your main config file is missing the 'game_log' setting in section 'server'")
            raise SystemExit(220)

        if self.IpsOnly:
            self.debug('Authentication method: Using IP instead of GUID!')
            # add the world client

        self.clients.newClient('-1', guid='WORLD', name='World', hide=True, pbid='WORLD')

        if not self.config.has_option('server', 'punkbuster') or self.config.getboolean('server', 'punkbuster'):
            result = self.write('PB_SV_Ver')
            if result != '' and result[:7] != 'Unknown':
                self.info('punkbuster active: %s' % result)
                self.PunkBuster = b3.parsers.punkbuster.PunkBuster(self)
            else:
                self.warning('Punkbuster test failed: check your game server setup and B3 config!')
                self.debug('Disabling punkbuster support!')

        # add event mappings
        self._eventMap['warmup'] = self.getEventID('EVT_GAME_WARMUP')
        self._eventMap['restartgame'] = self.getEventID('EVT_GAME_ROUND_END')

        # get map from the status rcon command
        mapname = self.getMap()
        if mapname:
            self.game.mapName = mapname
            self.info('map is: %s' % self.game.mapName)

        # force g_logsync
        self.debug('Forcing server cvar g_logsync to %s' % self._logSync)
        self.setCvar('g_logsync', self._logSync)

        try:
            self.game.fs_game = self.getCvar('fs_game').getString()
        except:
            self.game.fs_game = None
            self.warning('Could not query server for fs_game')
        try:
            self.game.fs_basepath = self.getCvar('fs_basepath').getString().rstrip('/')
            self.debug('fs_basepath: %s' % self.game.fs_basepath)
        except:
            self.game.fs_basepath = None
            self.warning('could not query server for fs_basepath')
        try:
            self.game.fs_homepath = self.getCvar('fs_homepath').getString().rstrip('/')
            self.debug('fs_homepath: %s' % self.game.fs_homepath)
        except:
            self.game.fs_homepath = None
            self.warning('could not query server for fs_homepath')
        try:
            self.game.shortversion = self.getCvar('shortversion').getString()
            self.debug('shortversion: %s' % self.game.shortversion)
        except:
            self.game.shortversion = None
            self.warning('Could not query server for shortversion')

        self.setVersionExceptions()
        self.debug('Parser started')

    ####################################################################################################################
    #                                                                                                                  #
    #   EVENT HANDLERS                                                                                                 #
    #                                                                                                                  #
    ####################################################################################################################

    def OnK(self, action, data, match=None):
        victim = self.getClient(victim=match)
        if not victim:
            self.debug('No victim')
            self.OnJ(action, data, match)
            return None

        attacker = self.getClient(attacker=match)
        if not attacker:
            self.debug('No attacker')
            return None

        attacker.team = self.getTeam(match.group('ateam'))
        attacker.name = match.group('aname')
        victim.team = self.getTeam(match.group('team'))
        victim.name = match.group('name')

        event_key = 'EVT_CLIENT_KILL'
        if attacker.cid == victim.cid:
            event_key = 'EVT_CLIENT_SUICIDE'
        elif attacker.team != b3.TEAM_UNKNOWN and attacker.team == victim.team:
            event_key = 'EVT_CLIENT_KILL_TEAM'

        victim.state = b3.STATE_DEAD
        data = (float(match.group('damage')), match.group('aweap'), match.group('dlocation'), match.group('dtype'))
        return self.getEvent(event_key, data=data, client=attacker, target=victim)


    def OnD(self, action, data, match=None):
        victim = self.getClient(victim=match)
        if not victim:
            self.debug('No victim - attempt join')
            self.OnJ(action, data, match)
            return None

        attacker = self.getClient(attacker=match)
        if not attacker:
            self.debug('No attacker')
            return None

        attacker.team = self.getTeam(match.group('ateam'))
        attacker.name = match.group('aname')
        victim.team = self.getTeam(match.group('team'))
        victim.name = match.group('name')

        eventkey = 'EVT_CLIENT_DAMAGE'
        if attacker.cid == victim.cid:
            eventkey = 'EVT_CLIENT_DAMAGE_SELF'
        elif attacker.team != b3.TEAM_UNKNOWN and attacker.team == victim.team:
            eventkey = 'EVT_CLIENT_DAMAGE_TEAM'

        data = (float(match.group('damage')), match.group('aweap'), match.group('dlocation'), match.group('dtype'))
        return self.getEvent(eventkey, data=data, client=attacker, target=victim)

    def OnQ(self, action, data, match=None):
        client = self.getClient(match)
        if client:
            client.disconnect()
        else:
            # check if we're in the authentication queue
            if match.group('cid') in self._counter:
                # Flag it to remove from the queue
                cid = match.group('cid')
                self._counter[cid] = 'Disconnected'
                self.debug('Slot %s has disconnected or was forwarded to our http download location: '
                           'removing from authentication queue...' % cid)
        return None

    def OnJ(self, action, data, match=None):
        codguid = match.group('guid')
        cid = match.group('cid')
        name = match.group('name')
        if len(codguid) < self._guidLength:
            # invalid guid
            self.verbose2('Invalid GUID: %s. GUID length set to %s' % (codguid, self._guidLength))
            codguid = None

        client = self.getClient(match)

        if client:
            self.verbose2('Client object already exists')
            # lets see if the name/guids match for this client, prevent player mixups after mapchange (not with PunkBuster enabled)
            if not self.PunkBuster:
                if self.IpsOnly:
                    # this needs testing since the name cleanup code may interfere with this next condition
                    if name != client.name:
                        self.debug('This is not the correct client (%s <> %s): disconnecting..' % (name, client.name))
                        client.disconnect()
                        return None
                    else:
                        self.verbose2('client.name in sync: %s == %s' % (name, client.name))
                else:
                    if codguid != client.guid:
                        self.debug('This is not the correct client (%s <> %s): disconnecting...' % (codguid, client.guid))
                        client.disconnect()
                        return None
                    else:
                        self.verbose2('client.guid in sync: %s == %s' % (codguid, client.guid))

            client.state = b3.STATE_ALIVE
            client.name = name
            # join-event for mapcount reasons and so forth
            return self.getEvent('EVT_CLIENT_JOIN', client=client)
        else:
            if self._counter.get(cid) and self._counter.get(cid) != 'Disconnected':
                self.verbose('cid: %s already in authentication queue: aborting join' % cid)
                return None

            self._counter[cid] = 1
            t = Timer(2, self.newPlayer, (cid, codguid, name))
            t.start()
            self.debug('%s connected: waiting for authentication...' % name)
            self.debug('Our authentication queue: %s' % self._counter)

    def OnA(self, action, data, match=None):
        client = self.getClient(match)
        if not client:
            self.debug('No client - attempt join')
            self.OnJ(action, data, match)
            client = self.getClient(match)
            if not client:
                return None

        client.name = match.group('name')
        actiontype = match.group('type')
        self.verbose('On action: %s: %s' % (client.name, actiontype))
        return self.getEvent('EVT_CLIENT_ACTION', data=actiontype, client=client)

    def OnSay(self, action, data, match=None):
        client = self.getClient(match)
        if not client:
            self.debug('No client - attempt join')
            self.OnJ(action, data, match)
            client = self.getClient(match)
            if not client:
                return None

        data = match.group('text')
        if data and ord(data[:1]) == 21:
            data = data[1:]

        # decode the server data
        if self.encoding:
            try:
                # Only decode if data is bytes, not if it's already a string (Python 3 fix)
                if isinstance(data, bytes):
                    data = data.decode(self.encoding)
            except Exception as msg:
                self.warning('ERROR: decoding data: %r', msg)

        if client.name != match.group('name'):
            client.name = match.group('name')

        return self.getEvent('EVT_CLIENT_SAY', data=data, client=client)

    def OnSayteam(self, action, data, match=None):
        client = self.getClient(match)
        if not client:
            self.debug('No client - attempt join')
            self.OnJ(action, data, match)
            client = self.getClient(match)
            if not client:
                return None

        data = match.group('text')
        # sometimes there is a weird character in the message        # remove if it is there
        if data and ord(data[:1]) == 21:
            data = data[1:]

        # decode the server data
        if self.encoding:
            try:
                # Only decode if data is bytes, not if it's already a string (Python 3 fix)
                if isinstance(data, bytes):
                    data = data.decode(self.encoding)
            except Exception as msg:
                self.warning('ERROR: decoding data: %r', msg)

        if client.name != match.group('name'):
            client.name = match.group('name')

        return self.getEvent('EVT_CLIENT_TEAM_SAY', data=data, client=client)

    def OnTell(self, action, data, match=None):
        client = self.getClient(match)
        tclient = self.getClient(attacker=match)
        if not client:
            self.debug('No client - attempt join')
            self.OnJ(action, data, match)
            client = self.getClient(match)
            if not client:
                return None

        data = match.group('text')
        if data and ord(data[:1]) == 21:
            data = data[1:]

        # decode the server data
        if self.encoding:
            try:
                # Only decode if data is bytes, not if it's already a string (Python 3 fix)
                if isinstance(data, bytes):
                    data = data.decode(self.encoding)
            except Exception as msg:
                self.warning('ERROR: decoding data: %r', msg)

        client.name = match.group('name')
        return self.getEvent('EVT_CLIENT_PRIVATE_SAY', data=data, client=client, target=tclient)

    def OnInitgame(self, action, data, match=None):
        options = re.findall(r'\\([^\\]+)\\([^\\]+)', data)
        for o in options:
            if o[0] == 'mapname':
                self.game.mapName = o[1]
            elif o[0] == 'g_gametype':
                self.game.gameType = o[1]
            elif o[0] == 'fs_game':
                self.game.modName = o[1]
            else:
                setattr(self.game, o[0], o[1])
        self.verbose('...self.console.game.gameType: %s' % self.game.gameType)
        self.game.startRound()
        return self.getEvent('EVT_GAME_ROUND_START', data=self.game)

    def OnExitlevel(self, action, data, match=None):
        t = Timer(60, self.clients.sync)
        t.start()
        self.game.mapEnd()
        return self.getEvent('EVT_GAME_EXIT', data=data)

    def OnItem(self, action, data, match=None):
        guid, cid, name, item = string.split(data, ';', 3)
        client = self.clients.getByCID(cid)
        if client:
            return self.getEvent('EVT_CLIENT_ITEM_PICKUP', data=item, client=client)
        return None

    ####################################################################################################################
    #                                                                                                                  #
    #   OTHER METHODS                                                                                                  #
    #                                                                                                                  #
    ####################################################################################################################

    def setVersionExceptions(self):
        """
        Dummy to enable shortversionexceptions for cod2.
        Use this function in inheriting parsers to override certain vars based on ie. shortversion.
        """
        pass

    def getTeam(self, team):
        """
        Return a B3 team given the team value.
        :param team: The team value
        """
        if team == 'allies':
            return b3.TEAM_BLUE
        elif team == 'axis':
            return b3.TEAM_RED
        else:
            return b3.TEAM_UNKNOWN

    def connectClient(self, ccid):
        """
        Return the client matchign the given slot number.
        :param ccid: The client slot number
        """
        players = self.getPlayerList()
        self.verbose('connectClient() = %s' % players)
        for cid, p in players.items():
            #self.debug('cid: %s, ccid: %s, p: %s' %(cid, ccid, p))
            if int(cid) == int(ccid):
                self.debug('%s found in status/playerList' % p['name'])
                return p

    def newPlayer(self, cid, codguid, name):
        """
        Build a new client using data in the authentication queue.
        :param cid: The client slot number
        :param codguid: The client GUID
        :param name: The client name
        """
        if not self._counter.get(cid):
            self.verbose('newPlayer thread no longer needed: key no longer available')
            return None
        if self._counter.get(cid) == 'Disconnected':
            self.debug('%s disconnected: removing from authentication queue' % name)
            self._counter.pop(cid)
            return None
        self.debug('newClient: %s, %s, %s' % (cid, codguid, name))
        sp = self.connectClient(cid)
        # PunkBuster is enabled, using PB guid
        if sp and self.PunkBuster:
            self.debug('sp: %s' % sp)
            # test if pbid is valid, otherwise break off and wait for another cycle to authenticate
            if not re.match(self._pbRegExp, sp['pbid']):
                self.debug('PB-id is not valid: giving it another try')
                self._counter[cid] += 1
                t = Timer(4, self.newPlayer, (cid, codguid, name))
                t.start()
                return None
            if self.IpsOnly:
                guid = sp['ip']
                pbid = sp['pbid']
            else:
                guid = sp['pbid']
                pbid = guid # save pbid in both fields to be consistent with other pb enabled databases
            ip = sp['ip']
            if self._counter.get(cid):
                self._counter.pop(cid)
            else:
                return None
        # PunkBuster is not enabled, using codguid
        elif sp:
            if self.IpsOnly:
                codguid = sp['ip']
            if not codguid:
                self.warning('Missing or wrong CodGuid and PunkBuster is disabled: cannot authenticate!')
                if self._counter.get(cid):
                    self._counter.pop(cid)
                return None
            else:
                guid = codguid
                pbid = ''
                ip = sp['ip']
                if self._counter.get(cid):
                    self._counter.pop(cid)
                else:
                    return None
        elif self._counter.get(cid) > 10:
            self.debug('Could not auth %s: giving up...' % name)
            if self._counter.get(cid):
                self._counter.pop(cid)
            return None
        # Player is not in the status response (yet), retry
        else:
            if self._counter.get(cid):
                self.debug('%s not yet fully connected: retrying...#:%s' % (name, self._counter.get(cid)))
                self._counter[cid] += 1
                t = Timer(4, self.newPlayer, (cid, codguid, name))
                t.start()
            else:
                self.warning('All authentication attempts failed')
            return None

        client = self.clients.newClient(cid, name=name, ip=ip, state=b3.STATE_ALIVE,
                                        guid=guid, pbid=pbid, data={'codguid': codguid})

        self.queueEvent(self.getEvent('EVT_CLIENT_JOIN', client=client))

    ####################################################################################################################
    #                                                                                                                  #
    #   B3 PARSER INTERFACE IMPLEMENTATION                                                                             #
    #                                                                                                                  #
    ####################################################################################################################

    def unban(self, client, reason='', admin=None, silent=False, *kwargs):
        """
        Unban a client.
        :param client: The client to unban
        :param reason: The reason for the unban
        :param admin: The admin who unbanned this client
        :param silent: Whether or not to announce this unban
        """
        if self.PunkBuster:
            if client.pbid:
                result = self.PunkBuster.unBanGUID(client)

                if result:
                    admin.message('^3Unbanned^7: %s^7: %s' % (client.exactName, result))

                if admin:
                    variables = self.getMessageVariables(client=client, reason=reason, admin=admin)
                    fullreason = self.getMessage('unbanned_by', variables)
                else:
                    variables = self.getMessageVariables(client=client, reason=reason)
                    fullreason = self.getMessage('unbanned', variables)

                if not silent and fullreason != '':
                    self.say(fullreason)

            elif admin:
                admin.message('%s ^7unbanned but has no punkbuster id' % client.exactName)
        else:
            name = self.stripColors(client.exactName)
            result = self.write(self.getCommand('unban', name=name, reason=reason))
            if admin:
                admin.message(result)

    def getMaps(self):
        """
        Return the available maps/levels name
        """
        maps = self.getCvar('sv_mapRotation')
        nmaps = []
        if maps:
            maps = re.findall(self._reMap, maps[0])
            for m in maps:
                if m[:3] == 'mp_':
                    m = m[3:]
                nmaps.append(m.title())
        return nmaps

    def getNextMap(self):
        """
        Return the next map/level name to be played.
        """
        if not self.game.mapName: return None
        maps = self.getCvar('sv_mapRotation')
        if maps:
            maps = re.findall(self._reMap, maps[0])
            gmap = self.game.mapName.strip().lower()
            found = False
            nmap = ''
            for nmap in maps:
                nmap = nmap.strip().lower()
                if found:
                    found = nmap
                    break
                elif nmap == gmap:
                    # current map, break on next map
                    found = True

            if found is True:
                # map is first map in rotation
                nmap = maps[0].strip().lower()

            if found:
                if nmap[:3] == 'mp_': nmap = nmap[3:]
                return nmap.title()

            return None
        else:
            return None

    def sync(self):
        """
        For all connected players returned by self.get_player_list(), get the matching Client
        object from self.clients (with self.clients.get_by_cid(cid) or similar methods) and
        look for inconsistencies. If required call the client.disconnect() method to remove
        a client from self.clients.
        """
        self.debug('synchronising clients...')
        plist = self.getPlayerList(maxRetries=4)
        mlist = {}

        for cid, c in plist.items():
            client = self.clients.getByCID(cid)
            if client:
                if client.guid and 'guid' in c and not self.IpsOnly:
                    if client.guid == c['guid']:
                        # player matches
                        self.debug('in-sync %s == %s', client.guid, c['guid'])
                        mlist[str(cid)] = client
                    else:
                        self.debug('no-sync %s <> %s', client.guid, c['guid'])
                        client.disconnect()
                elif client.ip and 'ip' in c:
                    if client.ip == c['ip']:
                        # player matches
                        self.debug('in-sync %s == %s', client.ip, c['ip'])
                        mlist[str(cid)] = client
                    else:
                        self.debug('no-sync %s <> %s', client.ip, c['ip'])
                        client.disconnect()
                else:
                    self.debug('no-sync: no guid or ip found')

        return mlist

    def authorizeClients(self):
        """
        For all connected players, fill the client object with properties allowing to find
        the user in the database (usualy guid, or punkbuster id, ip) and call the
        Client.auth() method.
        """
        players = self.getPlayerList(maxRetries=4)
        self.verbose('authorizeClients() = %s' % players)
        for cid, p in players.items():
            sp = self.clients.getByCID(cid)
            if sp:
                # Only set provided data, otherwise use the currently set data
                sp.ip = p.get('ip', sp.ip)
                sp.pbid = p.get('pbid', sp.pbid)
                if self.IpsOnly:
                    sp.guid = p.get('ip', sp.guid)
                else:
                    sp.guid = p.get('guid', sp.guid)
                sp.data = p
                sp.auth()

#--LogLineFormats---------------------------------------------------------------

#===============================================================================
# 
# *** CoD:
# Join:               J;160913;10;PlayerName
# Quit:               Q;160913;10;PlayerName
# Damage by world:    D;160913;14;axis;PlayerName;;-1;world;;none;6;MOD_FALLING;none
# Damage by opponent: D;160913;19;allies;PlayerName;248102;10;axis;OpponentName;mp44_mp;27;MOD_PISTOL_BULLET;right_foot
# Kill:               K;160913;4;axis;PlayerName;578287;0;axis;OpponentName;kar98k_mp;180;MOD_HEAD_SHOT;head
# Weapon/ammo pickup: Weapon;160913;8;PlayerName;m1garand_mp
# Action:             A;160913;16;axis;PlayerName;htf_scored
# Say to All:         say;160913;8;PlayerName;^Ubye
# Say to Team:        sayteam;160913;8;PlayerName;^Ulol
# Private message:    tell;160913;12;PlayerName1;1322833;8;PlayerName2;what message?
# Winners:            W;axis;160913;PlayerName1;258015;PlayerName2
# Losers:             L;allies;160913;PlayerName1;763816;PlayerName2
# 
# ExitLevel:          ExitLevel: executed
# Shutdown Engine:    ShutdownGame:
# Seperator:          ------------------------------------------------------------
# InitGame:           InitGame: \_Admin\xlr8or\_b3\B3 v1.2.1b [posix]\_Email\admin@xlr8or.com\_Host\[SNT]
#                    \_Location\Twente University - The Netherlands\_URL\http://games.snt.utwente.nl/\fs_game\xlr1.7
#                    \g_antilag\1\g_gametype\tdm\gamename\Call of Duty 2\mapname\mp_toujane\protocol\115
#                    \scr_friendlyfire\3\scr_killcam\1\shortversion\1.0\sv_allowAnonymous\0\sv_floodProtect\1
#                    \sv_hostname\^5[SNT] #3 ^7Tactical Gaming ^9(^7B3^9) (^1v1.0^9)\sv_maxclients\24\sv_maxPing\220
#                    \sv_maxRate\20000\sv_minPing\0\sv_privateClients\8\sv_pure\1\sv_voice\1
# 
# 
# *** CoD5 specific lines:
# JoinTeam:           JT;283895439;17;axis;PlayerName;
#                    AD;564;allies;580090035;6;axis;PlayerName;stg44_mp;30;MOD_RIFLE_BULLET;right_arm_lower
#===============================================================================