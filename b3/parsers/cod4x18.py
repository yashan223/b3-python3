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
# CHANGELOG:
#           0.1 - Initial release
#           0.2 - Added support for B3Hide plugin, force ID64

__author__ = 'Leiizko'
__version__ = '0.2'


import b3.clients
import b3.functions
import b3.parsers.cod4
import re


class Cod4X18Parser(b3.parsers.cod4.Cod4Parser):
    gameName = 'cod4'
    IpsOnly = False
    _guidLength = 0
    _commands = {
        'message': 'tell %(cid)s %(message)s',
        'say': 'say %(message)s',
        'set': 'set %(name)s "%(value)s"',
        'kick': 'kick %(cid)s %(reason)s ',
        'ban': 'permban %(cid)s %(reason)s ',
        'unban': 'unban %(guid)s',
        'tempban': 'tempban %(cid)s %(duration)sm %(reason)s',
        'kickbyfullname': 'kick %(cid)s'
    }

    def startup(self):
        """
        Called after the parser is created before run().
        """
        blank = self.write('sv_usesteam64id  1', maxRetries=3)
        data = self.write('plugininfo b3hide', maxRetries=3)
        
        # Always set COD4X18 regex patterns regardless of B3Hide plugin presence
        # COD4X18 servers may not have B3Hide but still use the extended format
        # Format: slot score ping guid steam64 name lastmsg ip:port qport rate
        self._regPlayer = re.compile(r'^\s*(?P<slot>[0-9]+)\s+'
                                r'(?P<score>-?[0-9]+)\s+'
                                r'(?P<ping>[0-9]+)\s+'
                                r'(?P<guid>[0-9]+)\s+'
                                r'(?P<steam>[0-9]+)\s+'
                                r'(?P<name>.+?)\s+'
                                r'(?P<lastmsg>[0-9]+)\s+'
                                r'(?P<ip>(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}'
                                r'(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])):?'
                                r'(?P<port>-?[0-9]{1,5})\s+'
                                r'(?P<qport>-?[0-9]{1,5})\s+'
                                r'(?P<rate>[0-9]+)\s*$', re.IGNORECASE | re.VERBOSE)
        
        # Short pattern for cases where some fields might be missing
        self._regPlayerShort = re.compile(r'^\s*(?P<slot>[0-9]+)\s+'
                                     r'(?P<score>-?[0-9]+)\s+'
                                     r'(?P<ping>[0-9]+)\s+'
                                     r'(?P<guid>[0-9]+)\s+'
                                     r'(?P<steam>[0-9]+)\s+'
                                     r'(?P<name>.+)', re.IGNORECASE | re.VERBOSE)
        
        if data and len(data) < 50:
            self.debug('B3Hide plugin detected on server')
        else:
            self.debug('B3Hide plugin not detected, using standard COD4X18 patterns')
            
        # Add debug logging for regex patterns
        self.debug('COD4X18 regex pattern set: %s', self._regPlayer.pattern)
        self.debug('COD4X18 short regex pattern set: %s', self._regPlayerShort.pattern)
								 
    def unban(self, client, reason='', admin=None, silent=False, *kwargs):
        """
        Unban a client.
        :param client: The client to unban
        :param reason: The reason for the unban
        :param admin: The admin who unbanned this client
        :param silent: Whether or not to announce this unban
        """
        result = self.write(self.getCommand('unban', guid=client.guid))
        if admin:
            admin.message(result)

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
        if isinstance(client, b3.clients.Client) and not client.guid:
            # client has no guid, kick instead
            return self.kick(client, reason, admin, silent)
        elif isinstance(client, str) and re.match('^[0-9]+$', client):
            self.write(self.getCommand('tempban', cid=client, reason=reason))
            return
        elif admin:
            banduration = b3.functions.minutesStr(duration)
            variables = self.getMessageVariables(client=client, reason=reason, admin=admin, banduration=banduration)
            fullreason = self.getMessage('temp_banned_by', variables)
        else:
            banduration = b3.functions.minutesStr(duration)
            variables = self.getMessageVariables(client=client, reason=reason, banduration=banduration)
            fullreason = self.getMessage('temp_banned', variables)

        duration = 43200 if int(duration) > 43200 else int(duration)
        self.write(self.getCommand('tempban', cid=client.cid, reason=reason, duration=duration))

        if not silent and fullreason != '':
            self.say(fullreason)

        self.queueEvent(self.getEvent('EVT_CLIENT_BAN_TEMP', {'reason': reason,
                                                              'duration': duration,
                                                              'admin': admin}, client))
        client.disconnect()

    def getPlayerList(self, maxRetries=None):
        """
        Query the game server for connected players with enhanced debugging.
        Override parent method to add detailed logging for troubleshooting.
        """
        self.debug('COD4X18: getPlayerList called')
        
        if self.PunkBuster:
            self.debug('COD4X18: Using PunkBuster getPlayerList')
            return self.PunkBuster.getPlayerList()
        else:
            self.debug('COD4X18: Sending RCON status command')
            data = self.write('status', maxRetries=maxRetries)
            
            self.debug('COD4X18: RCON status response: %r', data)
            
            if not data:
                self.debug('COD4X18: No data received from status command')
                return {}

            players = {}
            lastslot = -1
            lines = data.split('\n')
            
            self.debug('COD4X18: Status response has %d lines', len(lines))
            for i, line in enumerate(lines):
                self.debug('COD4X18: Line %d: %r', i, line)
            
            # Skip first 3 lines like parent class
            for i, line in enumerate(lines[3:], 3):
                line = line.strip()
                self.debug('COD4X18: Processing line %d: %r', i, line)
                
                if not line:
                    continue
                    
                m = re.match(self._regPlayer, line)
                if m:
                    self.debug('COD4X18: Full regex matched: %s', m.groupdict())
                    d = m.groupdict()
                    if int(m.group('slot')) > lastslot:
                        lastslot = int(m.group('slot'))
                        d['pbid'] = None
                        players[str(m.group('slot'))] = d
                        self.debug('COD4X18: Added player slot %s: %s', m.group('slot'), d)
                    else:
                        self.debug('COD4X18: Duplicate or incorrect slot number - client ignored %s last slot %s', 
                                  m.group('slot'), lastslot)
                else:
                    # Try short regex
                    m = re.match(self._regPlayerShort, line)
                    if m:
                        self.debug('COD4X18: Short regex matched: %s', m.groupdict())
                        d = m.groupdict()
                        if int(m.group('slot')) > lastslot:
                            lastslot = int(m.group('slot'))
                            d['pbid'] = None
                            # Add missing fields with defaults
                            d['lastmsg'] = '0'
                            d['ip'] = '0.0.0.0'
                            d['port'] = '0'
                            d['qport'] = '0'
                            d['rate'] = '25000'
                            players[str(m.group('slot'))] = d
                            self.debug('COD4X18: Added player (short) slot %s: %s', m.group('slot'), d)
                    else:
                        self.debug('COD4X18: No regex match for line: %r', line)

            self.debug('COD4X18: getPlayerList returning %d players: %s', len(players), players)
            return players