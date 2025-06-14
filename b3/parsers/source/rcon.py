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

from Queue import Queue
from socket import timeout
from threading import Event
from threading import Lock

from b3.lib.sourcelib.SourceRcon import SourceRcon
from b3.lib.sourcelib.SourceRcon import SourceRconError
from b3.lib.sourcelib.SourceRcon import SERVERDATA_EXECCOMMAND
from b3.lib.sourcelib.SourceRcon import SERVERDATA_AUTH

__version__ = '1.3'
__author__ = 'Courgette'

########################################################################################################################
##                                                                                                                    ##
##  PATCH SourceRcon.receive CLASS TO DETECT BAD RCON PASSWORD                                                        ##
##                                                                                                                    ##
########################################################################################################################

legacy_receive = SourceRcon.receive

def receive_wrapper(self):
    rv = legacy_receive(self)
    if isinstance(rv, str) and rv.strip().endswith(": Bad Password"):
        raise SourceRconError('Bad RCON password (patched SourceRcon)')
    else:
        return rv

SourceRcon.receive = receive_wrapper


class Rcon(object):
    """
    Facade to expose the SourceRcon class with an API as expected by B3 parsers
    """
    lock = Lock()

    def __init__(self, console, host, password):
        """
        Object constructor.
        :param console: The console implementation
        :param host: The host where to send RCON commands
        :param password: The RCON password
        """
        self.console = console
        self.host, self.port = host
        self.password = password
        self.timeout = 1.0
        self.queue = Queue()
        self.stop_event = Event()
        self.server = SourceRcon(self.host, self.port, self.password, self.timeout)

        self.console.info("RCON: connecting to Source game server")

        try:
            self.server.connect()
        except timeout as err:
            self.console.error("RCON: timeout error while trying to connect to game server at %s:%s. "
                               "Make sure the rcon_ip and port are correct and that the game server is "
                               "running" % (self.host, self.port))

    ####################################################################################################################
    #                                                                                                                  #
    #   EXPECTED B3 RCON API                                                                                           #
    #                                                                                                                  #
    ####################################################################################################################

    def writelines(self, lines):
        """
        Sends multiple rcon commands and do not wait for responses (non blocking).
        """
        self.queue.put(lines)

    def write(self, cmd, *args, **kwargs):
        """
        Sends a rcon command and return the response (blocking until timeout).
        """
        with Rcon.lock:
            try:
                self.console.info("RCON SEND: %s" % cmd)
                raw_data = self.server.rcon(self.encode_data(cmd))
                if raw_data:
                    data = raw_data.decode('UTF-8', 'replace')
                    self.console.info("RCON RECEIVED: %s" % data)
                    return data
            except timeout:
                self.console.error("RCON: timeout error while trying to connect to game server at %s:%s. "
                                   "Make sure the rcon_ip and port are correct and that the game server is "
                                   "running" % (self.host, self.port))

    def flush(self):
        pass

    def close(self):
        """
        Disconnects from the source game server.
        """
        if self.server:
            try:
                self.console.info("RCON disconnecting from Source game server")
                self.server.disconnect()
                self.console.verbose("RCON disconnected from Source game server")
            finally:
                self.server = None
                del self.server

    ####################################################################################################################
    #                                                                                                                  #
    #   OTHER METHODS                                                                                                  #
    #                                                                                                                  #
    ####################################################################################################################

    def _writelines(self):
        while not self.stop_event.isSet():
            lines = self.queue.get(True)
            for cmd in lines:
                if not cmd:
                    continue
                with self.lock:
                    self.rconNoWait(cmd)

    def rconNoWait(self, cmd):
        """
        Send a single command, do not wait for any response.
        Connect and auth if necessary.
        """
        try:
            self.console.info("RCON SEND: %s" % cmd)
            self.server.send(SERVERDATA_EXECCOMMAND, self.encode_data(cmd))
        except Exception:
            # timeout? invalid? we don't care. try one more time.
            self.server.disconnect()
            self.server.connect()
            self.server.send(SERVERDATA_AUTH, self.password)

            auth = self.server.receive()
            # the first packet may be a "you have been banned" or empty string.
            # in the latter case, fetch the second packet
            if auth == '':
                auth = self.server.receive()

            if auth is not True:
                self.server.disconnect()
                raise SourceRconError('RCON authentication failure: %s' % (repr(auth),))

            self.server.send(SERVERDATA_EXECCOMMAND, self.encode_data(cmd))


    def encode_data(self, data):
        """
        Encode data.
        """
        if not data:
            return data        if type(data) is str:
            return data.encode('UTF-8')
        else:
            return data

########################################################################################################################
## EXAMPLE PROGRAM                                                                                                     #
########################################################################################################################
##
## if __name__ == '__main__':
##    """
##    To run tests : python b3/parsers/source/rcon.py <rcon_ip> <rcon_port> <rcon_password>
##    """
##    import sys, os, time
##
##    host = port = pw = None
##
##    from ConfigParser import SafeConfigParser
##    test_config_file = os.path.join(os.path.dirname(__file__), 'test_rcon.ini')
##    if os.path.isfile(test_config_file):
##        try:
##            conf = SafeConfigParser()
##            conf.read(test_config_file)
##            host = conf.get("server", "host")
##            port = int(conf.get("server", "port"))
##            pw = conf.get("server", "password")
##        except:
##            pass
##
##    if not host and not port and not pw:
##        if len(sys.argv) != 4:
##            host = raw_input('Enter game server host IP/name: ')
##            port = int(raw_input('Enter host port: '))
##            pw = raw_input('Enter password: ')
##        else:
##            host = sys.argv[1]
##            port = int(sys.argv[2])
##            pw = sys.argv[3]
##
##    with open(test_config_file, "w") as f:
##        conf = SafeConfigParser()
##        conf.add_section('server')
##        conf.set("server", "host", host)
##        conf.set("server", "port", str(port))
##        conf.set("server", "password", pw)
##        conf.write(f)
##
##    from b3.fake import fakeconsole
##
##    r = Rcon(fakeconsole, (host, port), pw)
##    r.write('sm_say %s' % u"hello ÄÖtest")
########################################################################################################################