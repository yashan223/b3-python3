#
# BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2005 Michael "ThorN" Thornton
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#
# CHANGELOG
#
# 08/08/2010 - 0.1    - Courgette - creation based on smg11 parser
# 09/08/2010 - 0.2    - Courgette - implement rotatemap()
# 09/08/2010 - 0.3    - GrosBedo  - bot now recognize /tell commands correctly
# 10/08/2010 - 0.4    - Courgette - recognizes MOD_SUICIDE as suicide
#                                 - get rid of PunkBuster related code
#                                 - should /rcon dumpuser in cases the ClientUserInfoChanged line does not have
#                                   guid while player is not a bot. (untested, cannot reproduce)
# 11/08/2010 - 0.5    - GrosBedo  - minor fix for the /rcon dumpuser when no guid
#                                 - added !nextmap (with recursive detection !)
# 11/08/2010 - 0.6    - GrosBedo  - fixed the permanent ban command (banClient -> banaddr)
# 12/08/2010 - 0.7    - GrosBedo  - added weapons and means of death. Define what means of death are suicides
# 17/08/2010 - 0.7.1  - GrosBedo  - added say_team recognition
# 20/08/2010 - 0.7.5  - GrosBedo  - added many more regexp to detect ctf events, cvars and awards
#                                 - implement permban by ip and unbanbyip
#                                 - implement team recognition
# 20/08/2010 - 0.8    - Courgette - clean regexp (Item, CTF, Award, fallback)
#                                 - clean on_item
#                                 - remove OnDamage
#                                 - add OnCtf and OnAward
# 27/08/2010 - 0.8.1  - GrosBedo  - fixed findnextmap underscore bug (maps and vstr cvars with an underscore are
#                                   now correctly parsed)
# 28/08/2010 - 0.8.2  - Courgette - fix another findnextmap underscore bug
# 28/08/2010 - 0.8.3  - Courgette - fix issue with the regexp that match 'Award:' lines
# 04/09/2010 - 0.8.4  - GrosBedo  - fix issue with CTF flag capture events
# 17/09/2010 - 0.8.5  - GrosBedo  - fix crash issue when a player has disconnected at the very time the bot check
#                                   for the list of players
# 20/10/2010 - 0.9    - GrosBedo  - fix a BIG issue when detecting teams (were always unknown)
# 20/10/2010 - 0.9.1  - GrosBedo  - fix tk issue with DM and other team free gametypes
# 20/10/2010 - 0.9.2  - GrosBedo  - added EVT_GAME_FLAG_RETURNED (move it to q3a or a generic ioquake3 parser?)
# 23/10/2010 - 0.9.3  - GrosBedo  - detect gametype and modname at startup
#                                 - added flag_taken action
#                                 - fix a small bug when triggering the flag return event
# 07/11/2010 - 0.9.4  - GrosBedo  - ban and unban messages are now more generic and can be configured from b3.xml
#                                 - messages now support named $variables instead of %s
# 08/11/2010 - 0.9.5  - GrosBedo  - messages can now be empty (no message broadcasted on kick/tempban/ban/unban)
# 09/04/2011 - 0.9.6  - Courgette - reflect that cid are not converted to int anymore in the clients module
# 06/06/2011 - 0.10.0 - Courgette - change data format for EVT_CLIENT_BAN events
# 14/06/2011 - 0.11.0 - Courgette - cvar code moved to q3a AbstractParser
# 13/01/2014 - 0.11.1 - Fenix     - PEP8 coding standards
#                                 - changed bots guid to match other q3a parsers (BOT<slot>)
#                                 - correctly set client bot flag upon new client connection
# 02/05/2014 - 0.11.2 - Fenix     - fixed get_player_pings method declaration not matching the method in Parser class
# 11/08/2014 - 0.12   - Fenix     - reformat changelog
#                                 - fixes for the new getWrap implementation
#                                 - make use of self.getEvent() when creating events instead of referencing dynamically
#                                   created attributes (does nothing new but removes several warnings)
# 29/08/2014 - 0.13   - Fenix     - syntax cleanup
# 16/04/2015 - 0.14   - Fenix     - uniform class variables (dict -> variable)
# 29/05/2017 - 0.15   - GrosBedo     - fix parseUserInfo when missing \ as first character
#                                                 - ExcessivePlus mod compatibility
# 29/05/2017 - 0.16   - GrosBedo     - fix guid detection (at clientconnect instead of userinfochanged)
#                                                 - adapted to quake 3 arena
# 02/06/2017 - 0.17   - GrosBedo     - fix /tell message command (works only on ioq3 or e+ mod, but anyway most servers are running these)

__author__ = 'Courgette, GrosBedo, Fenix'
__version__ = '0.17'

import b3
import b3.clients
import b3.events
import re
import string

from b3.parsers.q3a.abstractParser import AbstractParser


class Q3Parser(AbstractParser):

    gameName = 'q3a'
    PunkBuster = None

    _connectingSlots = []
    _empty_name_default = 'EmptyNameDefault'
    _maplist = None

    _line_length = 65
    _line_color_prefix = ''

    _commands = {
        'message': 'tell %(cid)s %(message)s',
        'say': 'say %(message)s',
        'set': 'set %(name)s "%(value)s"',
        'kick': 'clientkick %(cid)s',
        'ban': 'banaddr %(cid)s',
        'tempban': 'clientkick %(cid)s',
        'banByIp': 'banaddr %(ip)s',
        'unbanByIp': 'bandel %(cid)s',
        'banlist': 'listbans',
    }

    _eventMap = {
        #'warmup' : b3.events.EVT_GAME_WARMUP,
        #'restartgame' : b3.events.EVT_GAME_ROUND_END
    }

    # remove the time off of the line
    _lineClear = re.compile(r'^(?:[0-9:.]+\s?)?')

    _lineFormats = (

        re.compile(r'^(?P<action>[a-z]+):\s*'
                   r'(?P<data>'
                   r'(?P<cid>[0-9]+):\s*'
                   r'(?P<pbid>[0-9A-Z]{32}):\s*'
                   r'(?P<name>[^:]+):\s*'
                   r'(?P<num1>[0-9]+):\s*'
                   r'(?P<num2>[0-9]+):\s*'
                   r'(?P<ip>[0-9.]+):'
                   r'(?P<port>[0-9]+))$', re.IGNORECASE),

        re.compile(r'^(?P<action>[a-z]+):\s*'
                   r'(?P<data>'
                   r'(?P<cid>[0-9]+):\s*'
                   r'(?P<name>.+):\s+'
                   r'(?P<text>.*))$', re.IGNORECASE),

        # 1:25 CTF: 1 2 2: Sarge returned the BLUE flag!
        # 1:16 CTF: 1 1 3: Sarge fragged RED's flag carrier!
        # 6:55 CTF: 2 1 2: Burpman returned the RED flag!
        # 7:02 CTF: 2 2 1: Burpman captured the BLUE flag!
        re.compile(r'^(?P<action>CTF):\s+'
                   r'(?P<cid>[0-9]+)\s+'
                   r'(?P<fid>[0-9]+)\s+'
                   r'(?P<type>[0-9]+):\s+'
                   r'(?P<data>.*'
                   r'(?P<color>RED|BLUE).*)$', re.IGNORECASE),

        #47:05 Kill: 2 4 11: Sarge killed ^6Jondah by MOD_LIGHTNING
        re.compile(r'^(?P<action>[a-z]+):\s*'
                   r'(?P<data>'
                   r'(?P<acid>[0-9]+)\s'
                   r'(?P<cid>[0-9]+)\s'
                   r'(?P<aweap>[0-9]+):\s*'
                   r'(?P<text>.*))$', re.IGNORECASE),

        # 7:02 Award: 2 4: Burpman gained the CAPTURE award!
        # 7:02 Award: 2 5: Burpman gained the ASSIST award!
        # 7:30 Award: 2 3: Burpman gained the DEFENCE award!
        # 29:15 Award: 2 2: SalaManderDragneL gained the IMPRESSIVE award!
        # 32:08 Award: 2 1: SalaManderDragneL gained the EXCELLENT award!
        # 8:36 Award: 10 1: Karamel is a fake gained the EXCELLENT award!
        re.compile(r'^(?P<action>Award):\s+'
                   r'(?P<cid>[0-9]+)\s+'
                   r'(?P<awardtype>[0-9]+):\s+'
                   r'(?P<data>'
                   r'(?P<name>.+) gained the '
                   r'(?P<awardname>\w+) award!)$', re.IGNORECASE),

        re.compile(r'^(?P<action>[a-z]+):\s*(?P<data>(?P<cid>[0-9]+):\s*(?P<text>.*))$', re.IGNORECASE),
        re.compile(r'^(?P<action>[a-z]+):\s*(?P<data>(?P<cid>[0-9]+)\s(?P<text>.*))$', re.IGNORECASE),

        # 81:16 say: grosbedo: !help
        re.compile(r'^(?P<action>say):\s(?P<data>(?P<name>.+): (?P<text>.*?))(?P<eplusnb>\d+)?$', re.IGNORECASE),

        # 81:16 tell: grosbedo to courgette: !help
        re.compile(r'^(?P<action>tell):\s(?P<data>(?P<name>.+) to (?P<aname>.+): (?P<text>.*?))(?P<eplusnb>\d+)?$', re.IGNORECASE),

        # 19:33 sayteam: UnnamedPlayer: ahahaha
        re.compile(r'^(?P<action>sayteam):\s(?P<data>(?P<name>.+): (?P<text>.*?))(?P<eplusnb>\d+)?$', re.IGNORECASE),

        # 46:37 Item: 4 team_CTF_redflag
        # 54:52 Item: 2 weapon_plasmagun
        re.compile(r'^(?P<action>Item):\s+(?P<cid>[0-9]+)\s+(?P<data>.*)$', re.IGNORECASE),

        # Falling through?
        # 1:05 ClientConnect: 3
        # 1:05 ClientUserinfoChanged: 3 guid\CAB616192CB5652375401264987A23D0\n\xlr8or\t\0\model\wq_male2/...
        re.compile(r'^(?P<action>[a-z_]\w*):\s*(?P<data>.*)$', re.IGNORECASE)
    )

    # map: dm_fort
    # num score ping name            lastmsg address               qport rate
    # --- ----- ---- --------------- ------- --------------------- ----- -----
    #   1     1    0 TheMexican^7        100 bot                       0 16384
    #   2     1    0 Sentenza^7           50 bot                       0 16384
    #   3     3   37 xlr8or^7              0 145.99.135.227:27960   3598 25000
    _regPlayer = re.compile(r'^(?P<slot>[0-9]+)\s+'
                            r'(?P<score>[0-9-]+)\s+'
                            r'(?P<ping>[0-9]+)\s+'
                            r'(?P<name>.*?)\s+'
                            r'(?P<last>[0-9]+)\s+'
                            r'(?P<ip>[0-9.]+)\s+'
                            r'(?P<qport>[0-9]+)\s+'
                            r'(?P<rate>[0-9]+)$', re.IGNORECASE)

    _reColor = re.compile(r'(\^.)|[\x00-\x20]|[\x7E-\xff]')

    # 7:44 Exit: Capturelimit hit.
    # 7:44 red:8  blue:0
    # 7:44 score: 63  ping: 81  client: 2 ^2^^0Pha^7nt^2om^7^^0Boo
    # 7:44 score: 0  ping: 0  client: 1 Sarge
    _reTeamScores = re.compile(r'^red:(?P<RedScore>.+)\s+blue:(?P<BlueScore>.+)$', re.IGNORECASE)
    _rePlayerScore = re.compile(r'^score:\s+'
                                r'(?P<score>[0-9]+)\s+ping:\s+'
                                r'(?P<ping>[0-9]+|CNCT|ZMBI)\s+client:\s+'
                                r'(?P<slot>[0-9]+)\s+'
                                r'(?P<name>.*)$', re.IGNORECASE)

    # Ban #1: 200.200.200.200/32
    _reBanList = re.compile(r'^Ban #(?P<cid>[0-9]+):\s+(?P<ip>[0-9]+.[0-9]+.[0-9]+.[0-9]+)/(?P<range>[0-9]+)$', re.I)

    MOD_UNKNOWN = 0
    MOD_SHOTGUN = 1
    MOD_GAUNTLET = 2
    MOD_MACHINEGUN = 3
    MOD_GRENADE = 4
    MOD_GRENADE_SPLASH = 5
    MOD_ROCKET = 6
    MOD_ROCKET_SPLASH = 7
    MOD_PLASMA = 8
    MOD_PLASMA_SPLASH = 9
    MOD_RAILGUN = 10
    MOD_LIGHTNING = 11
    MOD_BFG = 12
    MOD_BFG_SPLASH = 13
    MOD_WATER = 14
    MOD_SLIME = 15
    MOD_LAVA = 16
    MOD_CRUSH = 17
    MOD_TELEFRAG = 18
    MOD_FALLING = 19
    MOD_SUICIDE = 20
    MOD_TARGET_LASER = 21
    MOD_TRIGGER_HURT = 22
    # #ifdef MISSIONPACK
    MOD_NAIL = 23
    MOD_CHAINGUN = 24
    MOD_PROXIMITY_MINE = 25
    MOD_KAMIKAZE = 26
    MOD_JUICED = 27
    # #endif
    MOD_GRAPPLE = 28

    ## meansOfDeath to be considered suicides
    Suicides = (
        MOD_WATER,
        MOD_SLIME,
        MOD_LAVA,
        MOD_CRUSH,
        MOD_FALLING,
        MOD_SUICIDE,
        MOD_TRIGGER_HURT,
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
        # registering a ioquake3 specific event
        self.Events.createEvent('EVT_GAME_FLAG_RETURNED', 'Flag returned')

        self._eventMap['warmup'] = self.getEventID('EVT_GAME_WARMUP')
        self._eventMap['restartgame'] = self.getEventID('EVT_GAME_ROUND_END')

        # add the world client
        self.clients.newClient('1022', guid='WORLD', name='World', hide=True, pbid='WORLD')

        # get map from the status rcon command
        mapname = self.getMap()
        if mapname:
            self.game.mapName = mapname
            self.info('map is: %s'%self.game.mapName)

        try:
            # get gamepaths/vars
            fs_game = self.getCvar('fs_game').getString()
            if fs_game == '':
                fs_game = 'baseq3'
            self.game.fs_game = fs_game
            self.game.modName = fs_game
            self.debug('fs_game: %s' % self.game.fs_game)
        except Exception:
            self.game.fs_game = None
            self.game.modName = None
            self.warning("Could not query server for fs_game")

        try:
            self.game.fs_basepath = self.getCvar('fs_basepath').getString().rstrip('/')
            self.debug('fs_basepath: %s' % self.game.fs_basepath)
        except Exception:
            self.game.fs_basepath = None
            self.warning("Could not query server for fs_basepath")

        try:
            self.game.fs_homepath = self.getCvar('fs_homepath').getString().rstrip('/')
            self.debug('fs_homepath: %s' % self.game.fs_homepath)
        except Exception:
            self.game.fs_homepath = None
            self.warning("Could not query server for fs_homepath")

        try:
            self.game.gameType = self.defineGameType(self.getCvar('g_gametype').getString())
            self.debug('g_gametype: %s' % self.game.gameType)
        except Exception:
            self.game.gameType = None
            self.warning("Could not query server for g_gametype")

        # initialize connected clients
        self.info('Discover connected clients')
        plist = self.getPlayerList()
        for cid, c in plist.items():
            userinfostring = self.queryClientUserInfoByCid(cid)
            if userinfostring:
                self.OnClientuserinfochanged(None, userinfostring)

    ####################################################################################################################
    #                                                                                                                  #
    #   PARSING                                                                                                        #
    #                                                                                                                  #
    ####################################################################################################################

    def getLineParts(self, line):
        """
        Parse a log line returning extracted tokens.
        :param line: The line to be parsed
        """
        line = re.sub(self._lineClear, '', line, 1)
        m = None
        for f in self._lineFormats:
            m = re.match(f, line)
            if m:
                self.debug('XLR--------> line matched %s' % f.pattern)
                break
        if m:
            client = None
            target = None
            try:
                action = m.group('action').lower()
            except IndexError:
                # special case for damage lines where no action group can be set
                action = 'damage'
            
            return m, action, m.group('data').strip(), client, target

        elif '------' not in line:
            self.verbose('XLR--------> line did not match format: %s' % line)
    
    def parseUserInfo(self, info):
        """
        Parse an infostring.
        :param info: The infostring to be parsed.
        """
        player_id, info = string.split(info, ' ', 1)
        # If userinfo not starting with \ character, prepend it to avoid breaking regex
        if info[:1] != '\\':
            info = '\\' + info

        options = re.findall(r'\\([^\\]+)\\([^\\]+)', info)
        data = dict()
        for o in options:
            data[o[0]] = o[1]

        data['cid'] = player_id
        if 'n' in data:
            data['name'] = data['n']

        t = -1
        if 'team' in data:
            t = data['team']
        elif 't' in data:
            t = data['t']

        data['team'] = self.getTeam(t)
        
        if 'id' in data:
            data['guid'] = data['id']
            del data['id']

        if 'cl_guid' in data:
            data['guid'] = data['cl_guid']
        
        return data
    
    ####################################################################################################################
    #                                                                                                                  #
    #   EVENT HANDLERS                                                                                                 #
    #                                                                                                                  #
    ####################################################################################################################
        
    def OnClientconnect(self, action, data, match=None):
        client = self.clients.getByCID(data)
        self.debug('OnClientConnect: %s, %s' % (data, client))
        self.OnClientuserinfochanged(action, data, match)
        return self.getEvent('EVT_CLIENT_JOIN', client=client)

    def OnClientuserinfochanged(self, action, data, match=None):
        if data is None:
            # if the client disconnected and we are trying to force the server
            # to give us an id, we end up with an empty data object, so we just return and
            # everything should be fine (the slot should already be removed ln 336)
            return

        bclient = self.parseUserInfo(data)
        self.verbose('Parsed user info: %s' % bclient)
        if bclient:
            cid = bclient['cid']
            
            if cid in self._connectingSlots:
                self.debug('Client on slot %s is already being connected' % cid)
                return
            
            self._connectingSlots.append(cid)
            client = self.clients.getByCID(cid)

            if client:
                # update existing client
                for k, v in bclient.items():
                    setattr(client, k, v)
                # use the full client as reference now
                bclient = client
            else:
                if not 'name' in bclient:
                    bclient['name'] = self._empty_name_default

                guid = None
                if 'guid' in bclient:
                    guid = bclient['guid']
                else:
                    if 'skill' in bclient:
                        guid = 'BOT' + str(cid)
                        self.verbose('BOT connected!')
                        self.clients.newClient(cid, name=bclient['name'], ip='0.0.0.0', state=b3.STATE_ALIVE,
                                               guid=guid, data={'guid': guid}, team=bclient['team'], bot=True, money=20)
                        self._connectingSlots.remove(cid)
                        return None
                    #else:
                        #self.info('We are missing the guid but this is not a bot either, dumpuser')
                        #self._connectingSlots.remove(cid)
                        #self.OnClientuserinfochanged(None, self.queryClientUserInfoByCid(cid))
                        #return

                if not 'ip' in bclient:
                    infoclient = self.parseUserInfo(self.queryClientUserInfoByCid(cid))
                    if 'ip' in infoclient:
                        bclient['ip'] = infoclient['ip']
                    else:
                        self.warning('Failed to get client ip')
                
                if 'ip' in bclient:
                    self.clients.newClient(cid, name=bclient['name'], ip=bclient['ip'], state=b3.STATE_ALIVE,
                                           guid=guid, data={'guid': guid}, team=bclient['team'], bot=False, money=20)
                else:
                    self.warning('Failed to get connect client')
                    
            self._connectingSlots.remove(cid)
                
        return None

    def OnKill(self, action, data, match=None):
        self.debug('OnKill: %s (%s)' % (match.group('aweap'), match.group('text')))
        victim = self.getByCidOrJoinPlayer(match.group('cid'))
        if not victim:
            self.debug('No victim')
            #self.OnClientuserinfochanged(action, data, match)
            return None

        weapon = match.group('aweap')
        if not weapon:
            self.debug('No weapon')
            return None

        ## Fix attacker
        if match.group('aweap') in self.Suicides:
            # those kills should be considered suicides
            self.debug('OnKill: fixed attacker, suicide detected: %s' % match.group('text'))
            attacker = victim
        else:
            attacker = self.getByCidOrJoinPlayer(match.group('acid'))
        ## End fix attacker
          
        if not attacker:
            self.debug('No attacker')
            return None

        damagetype = match.group('text').split()[-1:][0]
        if not damagetype:
            self.debug('No damage type, weapon: %s' % weapon)
            return None

        eventkey = 'EVT_CLIENT_KILL'
        # fix event for team change and suicides and tk
        if attacker.cid == victim.cid:
            eventkey = 'EVT_CLIENT_SUICIDE'
        elif attacker.team != b3.TEAM_UNKNOWN and attacker.team != b3.TEAM_FREE and attacker.team == victim.team:
            eventkey = 'EVT_CLIENT_KILL_TEAM'

        # if not defined we need a general hitloc (for xlrstats)
        if not hasattr(victim, 'hitloc'):
            victim.hitloc = 'body'
        
        victim.state = b3.STATE_DEAD
        # need to pass some amount of damage for the teamkill plugin - 100 is a kill
        return self.getEvent(eventkey, (100, weapon, victim.hitloc, damagetype), attacker, victim)

    def OnClientdisconnect(self, action, data, match=None):
        client = self.clients.getByCID(data)
        if client:
            client.disconnect()
        return None

    def OnInitgame(self, action, data, match=None):
        self.debug('OnInitgame: %s' % data)
        options = re.findall(r'\\([^\\]+)\\([^\\]+)', data)
        for o in options:
            if o[0] == 'mapname':
                self.game.mapName = o[1]
            elif o[0] == 'g_gametype':
                self.game.gameType = self.defineGameType(o[1])
            elif o[0] == 'fs_game':
                self.game.modName = o[1]
            else:
                #self.debug('%s = %s' % (o[0],o[1]))
                setattr(self.game, o[0], o[1])

        self.verbose('...self.console.game.gameType: %s' % self.game.gameType)
        self.game.startRound()
        self.debug('Synchronizing client info...')
        self.clients.sync()

        return self.getEvent('EVT_GAME_ROUND_START', data=self.game)

    def OnSayteam(self, action, data, match=None):
        # Teaminfo does not exist in the sayteam logline, so we can't
        # know in which team the user is in. So we set him in a -1 void team.
        client = self.clients.getByExactName(match.group('name'))

        if not client:
            self.verbose('No client found')
            return None

        data = match.group('text')
        client.name = match.group('name')
        return self.getEvent('EVT_CLIENT_TEAM_SAY', data, client, -1)

    def OnTell(self, action, data, match=None):
        # 5:27 tell: woekele to XLR8or: test
        client = self.clients.getByExactName(match.group('name'))
        tclient = self.clients.getByExactName(match.group('aname'))

        if not client:
            self.verbose('No client found')
            return None

        data = match.group('text')
        if data and ord(data[:1]) == 21:
            data = data[1:]

        client.name = match.group('name')
        return self.getEvent('EVT_CLIENT_PRIVATE_SAY', data, client, tclient)

    def OnAction(self, cid, actiontype, data, match=None):
        #Need example
        client = self.clients.getByCID(cid)
        if not client:
            self.debug('No client found')
            return None
        self.verbose('OnAction: %s: %s %s' % (client.name, actiontype, data))
        return self.getEvent('EVT_CLIENT_ACTION', actiontype, client)

    def OnItem(self, action, data, match=None):
        client = self.getByCidOrJoinPlayer(match.group('cid'))
        if client:
            return self.getEvent('EVT_CLIENT_ITEM_PICKUP', match.group('data'), client)
        return None

    def OnCtf(self, action, data, match=None):
        # 1:25 CTF: 1 2 2: Sarge returned the BLUE flag!
        # 1:16 CTF: 1 1 3: Sarge fragged RED's flag carrier!
        # 6:55 CTF: 2 1 2: Burpman returned the RED flag!
        # 7:02 CTF: 2 2 1: Burpman captured the BLUE flag!
        # 2:12 CTF: 3 1 0: Tanisha got the RED flag!
        # 2:12 CTF: 3 2 0: Tanisha got the BLUE flag!
        cid = match.group('cid')
        client = self.getByCidOrJoinPlayer(match.group('cid'))
        flagteam = self.getTeam(match.group('fid'))
        flagcolor = match.group('color')
        action_types = {
            '0': 'flag_taken',
            '1': 'flag_captured',
            '2': 'flag_returned',
            '3': 'flag_carrier_kill',
        }

        try:
            action_id = action_types[match.group('type')]
        except KeyError:
            action_id = 'flag_action_' + match.group('type')
            self.debug('Unknown CTF action type: %s (%s)' % (match.group('type'), match.group('data')))

        self.debug('CTF Event: %s from team %s %s by %s' % (action_id, flagcolor, flagteam, client.name))
        if action_id == 'flag_returned':
            return self.getEvent('EVT_GAME_FLAG_RETURNED', flagcolor)
        else:
            return self.OnAction(cid, action_id, data)
            #return b3.events.Event(b3.events.EVT_CLIENT_ACTION, action_id, client)

    def OnAward(self, action, data, match=None):
        ## Award: <cid> <awardtype>: <name> gained the <awardname> award!
        # 7:02 Award: 2 4: Burpman gained the CAPTURE award!
        # 7:02 Award: 2 5: Burpman gained the ASSIST award!
        # 7:30 Award: 2 3: Burpman gained the DEFENCE award!
        # 29:15 Award: 2 2: SalaManderDragneL gained the IMPRESSIVE award!
        # 32:08 Award: 2 1: SalaManderDragneL gained the EXCELLENT award!
        # 8:36 Award: 10 1: Karamel is a fake gained the EXCELLENT award!
        client = self.getByCidOrJoinPlayer(match.group('cid'))
        action_type = 'award_%s' % match.group('awardname')
        return self.getEvent('EVT_CLIENT_ACTION', action_type, client)

    ####################################################################################################################
    #                                                                                                                  #
    #   OTHER METHODS                                                                                                  #
    #                                                                                                                  #
    ####################################################################################################################

    def getTeam(self, team):
        """
        Return a B3 team given the team value.
        :param team: The team value
        """
        team = str(team).lower()
        if team == 'free' or team == '0':
            result = b3.TEAM_FREE
        elif team == 'red' or team == '1':
            result = b3.TEAM_RED
        elif team == 'blue' or team == '2':
            result = b3.TEAM_BLUE
        elif team == 'spectator' or team == '3':
            result = b3.TEAM_SPEC
        else:
            result = b3.TEAM_UNKNOWN
        
        return result

    def defineGameType(self, gametype_int):
        """
        Translate the gametype to a readable format (also for teamkill plugin!).
        """
        gametype = str(gametype_int)
        
        if gametype_int == '0':
            gametype = 'dm'        # Free for all
        elif gametype_int == '1':
            gametype = 'du'        # Tourney
        elif gametype_int == '3':
            gametype = 'tdm'       # Team Deathmatch
        elif gametype_int == '4':
            gametype = 'ctf'       # Capture The Flag
        elif gametype_int == '8':
            gametype = 'el'        # Elimination
        elif gametype_int == '9':
            gametype = 'ctfel'     # CTF Elimination
        elif gametype_int == '10':
            gametype = 'lms'       # Last Man Standing
        elif gametype_int == '11':
            gametype = 'del'       # Double Domination
        elif gametype_int == '12':
            gametype = 'dom'       # Domination

        return gametype

    def connectClient(self, ccid):
        players = self.getPlayerList()
        self.verbose('connectClient() = %s' % players)
        for cid, p in players.items():
            if int(cid) == int(ccid):
                self.debug('Client found in status/playerList')
                return p

    def getByCidOrJoinPlayer(self, cid):
        client = self.clients.getByCID(cid)
        if client:
            return client
        else:
            userinfostring = self.queryClientUserInfoByCid(cid)
            if userinfostring:
                self.OnClientuserinfochanged(None, userinfostring)
            return self.clients.getByCID(cid)

    def queryClientUserInfoByCid(self, cid):
        """
        : dumpuser 5
        Player 5 is not on the server

        ]\rcon dumpuser 0
        userinfo
        --------
        ip                  81.56.143.41
        cg_cmdTimeNudge     0
        cg_delag            0
        cg_scorePlums       1
        cl_voip             0
        cg_predictItems     1
        cl_anonymous        0
        sex                 male
        handicap            100
        color2              7
        color1              2
        team_headmodel      sarge/classic
        team_model          sarge/classic
        headmodel           sarge/classic
        model               sarge/classic
        snaps               20
        rate                25000
        name                Courgette
        teamtask            0
        cl_guid             201AB4BBC40B4EC7445B49CE82D209EC
        teamoverlay         0
        """
        data = self.write('dumpuser %s' % cid)
        if not data:
            return None

        if data.split('\n')[0] != "userinfo":
            self.debug("dumpuser %s returned : %s" % (cid, data))
            return None

        datatransformed = "%s " % cid
        for line in data.split('\n'):
            if line.strip() == "userinfo" or line.strip() == "--------":
                continue

            var = line[:20].strip()
            val = line[20:].strip()
            datatransformed += "\\%s\\%s" % (var, val)

        return datatransformed

    ####################################################################################################################
    #                                                                                                                  #
    #   B3 PARSER INTERFACE IMPLEMENTATION                                                                             #
    #                                                                                                                  #
    ####################################################################################################################

    def getMaps(self):
        """
        Return the available maps/levels name
        """
        if self._maplist is not None:
            return self._maplist

        data = self.write('fdir *.bsp')
        if not data:
            return []

        mapregex = re.compile(r'^maps/(?P<map>.+)\.bsp$', re.I)
        maps = []
        for line in data.split('\n'):
            m = re.match(mapregex, line.strip())
            if m:
                if m.group('map'):
                    maps.append(m.group('map'))

        return maps

    def getNextMap(self):
        """
        Return the next map/level name to be played.
        """
        data = self.write('nextmap')
        nextmap = self.findNextMap(data)
        if nextmap:
            return nextmap
        else:
            return 'no nextmap set or it is in an unrecognized format !'

    def findNextMap(self, data):
        # "nextmap" is: "vstr next4; echo test; vstr aupo3; map oasago2"
        # the last command in the line is the one that decides what is the next map
        # in a case like : map oasago2; echo test; vstr nextmap6; vstr nextmap3
        # the parser will recursively look each last vstr var, and if it can't find a map,
        # fallback to the last map command
        self.debug('extracting nextmap name from: %s' % data)
        nextmapregex = re.compile(r'.*("|;)\s*('
                                  r'(?P<vstr>vstr (?P<vstrnextmap>[a-z0-9_]+))|'
                                  r'(?P<map>map (?P<mapnextmap>[a-z0-9_]+)))', re.IGNORECASE)
        m = re.match(nextmapregex, data)
        if m:
            if m.group('map'):
                self.debug('found nextmap: %s' % (m.group('mapnextmap')))
                return m.group('mapnextmap')
            elif m.group('vstr'):
                self.debug('nextmap is redirecting to var: %s' % (m.group('vstrnextmap')))
                data = self.write(m.group('vstrnextmap'))
                result = self.findNextMap(data) # recursively dig into the vstr vars to find the last map called
                if result:
                    # if a result was found in a deeper level, then we return it to the upper level,
                    # until we get back to the root level
                    return result
                else:
                    # if none could be found, then try to find a map command in the current string
                    nextmapregex = re.compile(r'.*("|;)\s*(?P<map>map (?P<mapnextmap>[a-z0-9_]+))"', re.IGNORECASE)
                    m = re.match(nextmapregex, data)
                    if m.group('map'):
                        self.debug('found nextmap: %s' % (m.group('mapnextmap')))
                        return m.group('mapnextmap')
                    else:
                        # if none could be found, we go up a level by returning None (remember this is done recursively)
                        self.debug('no nextmap found in this string!')
                        return None
        else:
            self.debug('no nextmap found in this string!')
            return None

    def rotateMap(self):
        """
        Load the next map/level
        """
        self.write('vstr nextmap')

    def ban(self, client, reason='', admin=None, silent=False, *kwargs):
        """
        Ban a given client.
        :param client: The client to ban
        :param reason: The reason for this ban
        :param admin: The admin who performed the ban
        :param silent: Whether or not to announce this ban
        """
        self.debug('BAN : client: %s, reason: %s', client, reason)
        if isinstance(client, b3.clients.Client) and not client.guid:
            # client has no guid, kick instead
            return self.kick(client, reason, admin, silent)
        elif isinstance(client, str) and re.match('^[0-9]+$', client):
            self.write(self.getCommand('ban', cid=client, reason=reason))
            return
        elif not client.id:
            # no client id, database must be down, do tempban
            self.error('Q3AParser.ban(): no client id, database must be down, doing tempban')
            return self.tempban(client, reason, '1d', admin, silent)

        if admin:
            variables = self.getMessageVariables(client=client, reason=reason, admin=admin)
            fullreason = self.getMessage('banned_by', variables)
        else:
            variables = self.getMessageVariables(client=client, reason=reason)
            fullreason = self.getMessage('banned', variables)

        if client.cid is None:
            # ban by ip, this happens when we !permban @xx a player that is not connected
            self.debug('EFFECTIVE BAN : %s', self.getCommand('banByIp', ip=client.ip, reason=reason))
            self.write(self.getCommand('banByIp', ip=client.ip, reason=reason))
        else:
            # ban by cid
            self.debug('EFFECTIVE BAN : %s', self.getCommand('ban', cid=client.cid, reason=reason))
            self.write(self.getCommand('ban', cid=client.cid, reason=reason))

        if not silent and fullreason != '':
            self.say(fullreason)

        self.queueEvent(self.getEvent('EVT_CLIENT_BAN', {'reason': reason, 'admin': admin}, client))
        client.disconnect()

    def unban(self, client, reason='', admin=None, silent=False, *kwargs):
        """
        Unban a client.
        :param client: The client to unban
        :param reason: The reason for the unban
        :param admin: The admin who unbanned this client
        :param silent: Whether or not to announce this unban
        """
        data = self.write(self.getCommand('banlist', cid=-1))
        if not data:
            self.debug('ERROR: unban cannot be done, no ban list returned')
        else:
            for line in data.split('\n'):
                m = re.match(self._reBanList, line.strip())
                if m:
                    if m.group('ip') == client.ip:
                        self.write(self.getCommand('unbanByIp', cid=m.group('cid'), reason=reason))
                        self.debug('EFFECTIVE UNBAN : %s',self.getCommand('unbanByIp', cid=m.group('cid')))

                if admin:
                    variables = self.getMessageVariables(client=client, reason=reason, admin=admin)
                    fullreason = self.getMessage('unbanned_by', variables)
                else:
                    variables = self.getMessageVariables(client=client, reason=reason)
                    fullreason = self.getMessage('unbanned', variables)

                if not silent and fullreason != '':
                    self.say(fullreason)

    def getPlayerPings(self, filter_client_ids=None):
        """
        Returns a dict having players' id for keys and players' ping for values.
        :param filter_client_ids: If filter_client_id is an iterable, only return values for the given client ids.
        """
        data = self.write('status')
        if not data:
            return {}

        players = {}
        for line in data.split('\n'):
            m = re.match(self._regPlayer, line.strip())
            if m:
                if m.group('ping') == 'ZMBI':
                    # ignore them, let them not bother us with errors
                    pass
                else:
                    players[str(m.group('slot'))] = int(m.group('ping'))

        return players

    def sync(self):
        """
        For all connected players returned by self.get_player_list(), get the matching Client
        object from self.clients (with self.clients.get_by_cid(cid) or similar methods) and
        look for inconsistencies. If required call the client.disconnect() method to remove
        a client from self.clients.
        """
        plist = self.getPlayerList()
        mlist = dict()
        for cid, c in plist.items():
            client = self.getByCidOrJoinPlayer(cid)
            if client:
                if client.guid and 'guid' in c.keys():
                    if client.guid == c['guid']:
                        # player matches
                        self.debug('in-sync %s == %s', client.guid, c['guid'])
                        mlist[str(cid)] = client
                    else:
                        self.debug('no-sync %s <> %s', client.guid, c['guid'])
                        client.disconnect()
                elif client.ip and 'ip' in c.keys():
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